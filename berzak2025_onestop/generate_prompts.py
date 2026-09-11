"""Generate participant-level LLM prompts for OneStop Eye Movements.

Reads processed_data/exp1.csv and processed_data/exp2.csv and writes
prompts.jsonl.zip.

Each paragraph the participant read becomes one trial, presented word by word
with the total reading time on that word marked in ``<< >>``, followed by the
multiple-choice comprehension question and the answer the participant selected.
Words that never received a fixation are marked ``<<not fixated>>``.

The two experiments differ in the reading-goal manipulation, and the trials are
laid out accordingly. In exp1 (ordinary reading) the question appears after the
paragraph. In exp2 (information seeking) the participant saw the question
before reading, so the question is shown first.

Response keys
-------------
Answers were displayed in a cross arrangement and selected with the four
directional buttons of a gamepad, not with named keys. Each participant is
therefore assigned four random letters, one per on-screen answer position,
following the convention used elsewhere in this repository. The draw is seeded
for reproducibility.

Sessions are split into batches
-------------------------------
Each participant read about 65 paragraphs totalling roughly 7,000 words, which
comes to well over the 32K-token budget in the contribution guide. Each session
is split into consecutive batches of trials, in the order the participant read
them, with the batch number recorded in the ``batch`` metadata field. No trials
are dropped.
"""

import json
import random
import string
import zipfile
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.resolve()
PROCESSED_DIR = BASE_DIR / "processed_data"
JSONL_PATH = BASE_DIR / "prompts.jsonl"
ZIP_PATH = BASE_DIR / "prompts.jsonl.zip"

RANDOM_SEED = 20250526

# Consecutive batches each participant's session is split into. Four batches
# left the longest sessions within a few hundred tokens of the 32K budget, so
# five is used to keep a margin.
N_BATCHES = 5

# Separator between the four answer options in the answer_options column.
OPTION_SEPARATOR = " | "

ORDINARY_INSTRUCTION = (
    "You will read newspaper article paragraphs one at a time on a screen. Read "
    "each paragraph silently and at your own pace, for comprehension. Your eye "
    "movements are recorded while you read. After each paragraph you will be "
    "asked one multiple-choice question about it, with four answers to choose "
    "from. Press '{keys}' to select the answer in that position. Keep your head "
    "still while reading.\n\n"
)

SEEKING_INSTRUCTION = (
    "You will read newspaper article paragraphs one at a time on a screen. Before "
    "each paragraph you will be shown a multiple-choice question about it, and "
    "your task is to read the paragraph in order to answer that question. Read "
    "silently and at your own pace. Your eye movements are recorded while you "
    "read. After the paragraph the question is shown again with four answers to "
    "choose from. Press '{keys}' to select the answer in that position. Keep your "
    "head still while reading.\n\n"
)

EXPERIMENTS = [
    ("exp1.csv", "berzak2025_onestop/ordinary_reading", ORDINARY_INSTRUCTION),
    ("exp2.csv", "berzak2025_onestop/information_seeking", SEEKING_INSTRUCTION),
]


def split_evenly(items: list, n_parts: int) -> list[list]:
    """Split *items* into *n_parts* consecutive, near-equal chunks."""
    size, remainder = divmod(len(items), n_parts)
    chunks, start = [], 0
    for i in range(n_parts):
        stop = start + size + (1 if i < remainder else 0)
        chunks.append(items[start:stop])
        start = stop
    return chunks


def answer_lines(trial_head: pd.Series, keys: list[str]) -> str:
    """Render the four answer options in the order they appeared on screen."""
    raw = trial_head["answer_options"]
    options = str(raw).split(OPTION_SEPARATOR) if pd.notna(raw) else []
    lines = []
    for position, text in enumerate(options[:4]):
        lines.append(f"    {keys[position]}. {text}\n")
    return "".join(lines)


def format_trial(number: int, trial: pd.DataFrame, keys: list[str], seeking: bool):
    """Render one paragraph-reading trial. Returns (text, reading_times)."""
    head = trial.iloc[0]
    question = head["question"] if pd.notna(head["question"]) else ""

    parts = [f"Trial {number}:\n"]
    if seeking:
        parts.append(f"  Question: '{question}'\n")

    reading_times = []
    for row in trial.itertuples(index=False):
        position = int(row.word_position)
        reading_time = int(row.rt)
        if reading_time > 0:
            parts.append(f"  Word {position}: '{row.stimulus}'  <<{reading_time}>> ms\n")
            reading_times.append(reading_time)
        else:
            parts.append(f"  Word {position}: '{row.stimulus}'  <<not fixated>>\n")

    # The question page follows the paragraph in both regimes, so the question is
    # shown again here. In the information seeking regime this is its second
    # appearance, matching the question preview page seen before reading.
    parts.append(f"  Question: '{question}'\n")
    parts.append(answer_lines(head, keys))

    response_position = head["response_position"]
    if pd.notna(response_position):
        key = keys[int(response_position) - 1]
        verdict = "Correct." if head["accuracy"] == 1 else "Incorrect."
        parts.append(f"  You press <<{key}>>. {verdict}\n")
    else:
        parts.append("  No response detected.\n")

    parts.append("\n")
    return "".join(parts), reading_times


def build_prompts(df: pd.DataFrame, experiment: str, instruction: str,
                  rng: random.Random) -> list[dict]:
    seeking = experiment.endswith("information_seeking")
    prompts = []

    for participant_id, rows in df.groupby("participant_id", sort=True):
        keys = rng.sample(string.ascii_lowercase, 4)

        trial_orders = sorted(rows["trial_order"].unique())
        by_trial = {order: group.sort_values("word_position")
                    for order, group in rows.groupby("trial_order")}

        for batch_number, batch in enumerate(split_evenly(trial_orders, N_BATCHES), start=1):
            text = instruction.format(keys="', '".join(keys))
            reading_times = []

            for number, trial_order in enumerate(batch, start=1):
                trial_text, trial_rts = format_trial(
                    number, by_trial[trial_order], keys, seeking
                )
                text += trial_text
                reading_times.extend(trial_rts)

            entry = {
                "text": text,
                "experiment": experiment,
                "participant_id": int(participant_id),
                "batch": batch_number,
                "rt": reading_times,
            }
            head = rows.iloc[0]
            if pd.notna(head["comprehension_score"]):
                entry["comprehension_score"] = float(head["comprehension_score"])
            if pd.notna(head["lextale_score"]):
                entry["lextale_score"] = float(head["lextale_score"])
            prompts.append(entry)

    return prompts


def main() -> None:
    # One generator shared across both experiments, so that participants in the
    # two reading regimes do not receive the same key assignments in lockstep.
    rng = random.Random(RANDOM_SEED)

    all_prompts = []
    for filename, experiment, instruction in EXPERIMENTS:
        df = pd.read_csv(PROCESSED_DIR / filename, low_memory=False)
        prompts = build_prompts(df, experiment, instruction, rng)
        print(f"  {experiment}: {len(prompts)} lines "
              f"from {df['participant_id'].nunique()} participants")
        all_prompts.extend(prompts)

    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for entry in all_prompts:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSONL_PATH, "prompts.jsonl")
    JSONL_PATH.unlink()

    lengths = [len(entry["text"]) for entry in all_prompts]
    print(f"Wrote {ZIP_PATH.name}")
    print(f"  lines:      {len(all_prompts):,}")
    print(f"  chars/line: min {min(lengths):,} max {max(lengths):,}")


if __name__ == "__main__":
    main()
