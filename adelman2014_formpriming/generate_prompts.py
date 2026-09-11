"""Generate participant-level LLM prompts for the Form Priming Project.

Reads processed_data/exp1.csv and writes prompts.jsonl.zip: one line per
participant, replaying all 840 masked-primed lexical decision trials in the
order they were presented.

Response keys
-------------
The source data records only whether each response was correct, and the original
apparatus used left/right buttons rather than named keys. Following the
convention used elsewhere in this repository, each participant is assigned two
random letters -- one for "word" and one for "nonword" -- so that the key
mapping varies across participants. The draw is seeded for reproducibility.

Feedback
--------
Participants received corrective feedback only when a response was incorrect or
when the 2000 ms deadline elapsed, so correct trials carry no feedback text.

Primes
------
The instruction text follows the original study, which described the sequence of
events *omitting mention of the prime* (Adelman et al., 2014, p. 11) -- the
primes were forward-masked and presented for only 50 ms, and participants were
not told about them. The trial lines nonetheless record the prime that was
displayed, because it is the experimental manipulation the dataset exists to
capture. See README.md.
"""

import json
import random
import string
import zipfile
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.resolve()
PROCESSED_FILE = BASE_DIR / "processed_data" / "exp1.csv"
JSONL_PATH = BASE_DIR / "prompts.jsonl"
ZIP_PATH = BASE_DIR / "prompts.jsonl.zip"

EXPERIMENT_NAME = "adelman2014_formpriming"

RANDOM_SEED = 20140101

INSTRUCTION = (
    "In this task you will decide whether a letter string is a real English word. "
    "Each trial starts with a fixation cross, followed by a row of hash marks "
    "(##########), after which a letter string appears in capitals. If the letter "
    "string is a real English word, press '{word_key}'. If it is not a real word, "
    "press '{nonword_key}'. Respond as quickly as you can, within 2 seconds, but "
    "do not sacrifice accuracy to do so. You will be told when a response is "
    "incorrect.\n\n"
)

TRIAL_CORRECT = "Trial {n}: '{prime}' flashes, then '{target}'. You press <<{key}>>.\n"
TRIAL_INCORRECT = (
    "Trial {n}: '{prime}' flashes, then '{target}'. You press <<{key}>>. Incorrect.\n"
)
TRIAL_TIMEOUT = "Trial {n}: '{prime}' flashes, then '{target}'. No response detected.\n"


def build_prompts(df: pd.DataFrame) -> list[dict]:
    rng = random.Random(RANDOM_SEED)
    prompts = []

    for participant_id, rows in df.groupby("participant_id", sort=True):
        word_key, nonword_key = rng.sample(string.ascii_lowercase, 2)
        keys = {"word": word_key, "nonword": nonword_key}

        text = INSTRUCTION.format(word_key=word_key, nonword_key=nonword_key)
        reaction_times = []

        rows = rows.sort_values("trial_order")
        for trial_number, row in enumerate(rows.itertuples(index=False), start=1):
            fields = {
                "n": trial_number,
                "prime": row.prime,
                "target": row.stimulus,
            }
            if row.is_timeout == 1:
                text += TRIAL_TIMEOUT.format(**fields)
            else:
                fields["key"] = keys[row.response]
                template = TRIAL_CORRECT if row.accuracy == 1 else TRIAL_INCORRECT
                text += template.format(**fields)
                reaction_times.append(int(round(row.rt)))

        entry = {
            "text": text,
            "experiment": EXPERIMENT_NAME,
            "participant_id": int(participant_id),
            "rt": reaction_times,
            "lab": rows["lab"].iloc[0],
        }

        vocabulary = rows["vocabulary_score"].iloc[0]
        spelling = rows["spelling_score"].iloc[0]
        if pd.notna(vocabulary):
            entry["vocabulary_score"] = round(float(vocabulary), 4)
        if pd.notna(spelling):
            entry["spelling_score"] = round(float(spelling), 4)

        prompts.append(entry)

    return prompts


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
    print(f"  lines:      {len(prompts):,} (one per participant)")
    print(f"  chars/line: min {min(lengths):,} max {max(lengths):,}")


if __name__ == "__main__":
    main()
