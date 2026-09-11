"""Generate participant-level LLM prompts for the Provo Corpus.

Reads processed_data/exp1.csv and writes prompts.jsonl.zip, following the
formatting of the continuous-outcome example in the repository README and of
frank2013_reading.

Each passage the participant read becomes one trial, presented word by word
with the total reading time on that word marked in ``<< >>``. Words that never
received a fixation are marked ``<<not fixated>>``.

Sessions are split into two batches
-----------------------------------
Each participant read all 55 passages (2,743 words), which comes to roughly
39,000 tokens in a single prompt -- over the 32K-token budget in the README,
even though it stays under the validator's 100,000-character proxy. Each
session is therefore split into two consecutive batches of passages, in the
order the participant actually read them, and the batch number is recorded in
the ``batch`` metadata field. This is the same approach used for other
oversized sessions in this repository. No trials are dropped.
"""

import json
import zipfile
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.resolve()
PROCESSED_FILE = BASE_DIR / "processed_data" / "exp1.csv"
JSONL_PATH = BASE_DIR / "prompts.jsonl"
ZIP_PATH = BASE_DIR / "prompts.jsonl.zip"

EXPERIMENT_NAME = "luke2018_provo"

# Number of consecutive batches each participant's session is split into.
N_BATCHES = 2

INSTRUCTION = (
    "You will read short passages of English text presented one at a time on a "
    "screen. Read each passage silently and at your own pace, for comprehension, "
    "as you normally would. Your eye movements are recorded while you read. "
    "Press the button when you have finished reading a passage to move on to the "
    "next one. We will measure how long you look at each word.\n\n"
)


def format_trial(trial_number: int, words: pd.DataFrame) -> tuple[str, list[int]]:
    """Render one passage as a numbered trial block."""
    lines = [f"Trial {trial_number}:\n"]
    reading_times: list[int] = []

    for _, row in words.iterrows():
        position = int(row["word_position"])
        word = row["stimulus"]
        reading_time = int(row["rt"])

        if reading_time > 0:
            lines.append(f"  Word {position}: '{word}'  <<{reading_time}>> ms\n")
            reading_times.append(reading_time)
        else:
            lines.append(f"  Word {position}: '{word}'  <<not fixated>>\n")

    lines.append("\n")
    return "".join(lines), reading_times


def build_prompts(df: pd.DataFrame) -> list[dict]:
    prompts = []

    for participant_id, participant_rows in df.groupby("participant_id", sort=True):
        # Passages in the order this participant actually read them.
        trial_orders = sorted(participant_rows["trial_order"].unique())
        batches = _split_evenly(trial_orders, N_BATCHES)

        for batch_number, batch_trials in enumerate(batches, start=1):
            text = INSTRUCTION
            reading_times: list[int] = []

            for trial_number, trial_order in enumerate(batch_trials, start=1):
                words = participant_rows[
                    participant_rows["trial_order"] == trial_order
                ].sort_values("word_position")
                trial_text, trial_rts = format_trial(trial_number, words)
                text += trial_text
                reading_times.extend(trial_rts)

            prompts.append(
                {
                    "text": text,
                    "experiment": EXPERIMENT_NAME,
                    "participant_id": int(participant_id),
                    "batch": batch_number,
                    "rt": reading_times,
                }
            )

    return prompts


def _split_evenly(items: list, n_parts: int) -> list[list]:
    """Split *items* into *n_parts* consecutive, near-equal chunks."""
    size, remainder = divmod(len(items), n_parts)
    chunks = []
    start = 0
    for i in range(n_parts):
        stop = start + size + (1 if i < remainder else 0)
        chunks.append(items[start:stop])
        start = stop
    return chunks


def main() -> None:
    df = pd.read_csv(PROCESSED_FILE, low_memory=False)

    prompts = build_prompts(df)

    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for entry in prompts:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSONL_PATH, "prompts.jsonl")
    JSONL_PATH.unlink()

    lengths = [len(entry["text"]) for entry in prompts]
    print(f"Wrote {ZIP_PATH.name}")
    print(f"  lines:        {len(prompts)} "
          f"({df['participant_id'].nunique()} participants x {N_BATCHES} batches)")
    print(f"  chars/line:   min {min(lengths):,} max {max(lengths):,}")


if __name__ == "__main__":
    main()
