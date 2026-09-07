"""Preprocess the Form Priming Project (Adelman et al., 2014) for PsychLing-101.

Reads the source files in original_data/ and writes a tidy, trial-level CSV to
processed_data/exp1.csv, with column names following CODEBOOK.csv.

One row = one masked-primed lexical decision trial by one participant.

Notes on source-data conventions handled here
---------------------------------------------
* ``RT`` in the source file is stored as a **negative** number when the response
  was incorrect; the magnitude is the response time in ms. Exactly -2000 means
  the 2000 ms deadline elapsed without a response. This script stores the
  magnitude in ``rt`` and keeps correctness in ``accuracy``.
* ``trialNum`` starts at 29 because the first 28 trials of each session were
  unanalysed practice and are not distributed. Trials are renumbered from 1.
* The source file records only whether the response was correct, not which key
  was pressed. Because the task is a two-alternative decision, the response is
  recovered from ``accuracy`` and ``lexStatus``; it is left empty for timeouts,
  where no response was made.
"""

import zipfile
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.resolve()
ORIGINAL_DIR = BASE_DIR / "original_data"
PROCESSED_DIR = BASE_DIR / "processed_data"

TRIALS_ZIP = ORIGINAL_DIR / "FPP_text_files.zip"
TRIALS_MEMBER = "FPP/MP_data.txt"
STIMULI_FILE = ORIGINAL_DIR / "fpp_stimuli.csv"
SCORES_FILE = ORIGINAL_DIR / "fpp_participant_scores.csv"

# Trials 1-28 of each session were practice and are not in the data.
N_PRACTICE_TRIALS = 28

# Response deadline in ms; an RT of exactly -2000 marks a timeout.
RESPONSE_DEADLINE_MS = 2000

OUTPUT_COLUMNS = [
    "participant_id",
    "lab",
    "trial_order",
    "stimulus",
    "prime",
    "condition",
    "prime_code",
    "stimulus_type",
    "response",
    "accuracy",
    "rt",
    "is_timeout",
    "vocabulary_score",
    "spelling_score",
]


def load_trials() -> pd.DataFrame:
    with zipfile.ZipFile(TRIALS_ZIP) as zf:
        with zf.open(TRIALS_MEMBER) as f:
            return pd.read_csv(f, sep=r"\s+", encoding="latin-1", low_memory=False)


def load_prime_lookup() -> dict:
    """Return {(targetNum, lexStatus): (target, [prime for cond 1..28])}."""
    stimuli = pd.read_csv(STIMULI_FILE, encoding="utf-8")
    prime_columns = [f"prime_cond{i}" for i in range(1, 29)]
    lookup = {}
    for row in stimuli.itertuples(index=False):
        key = (row.targetNum, row.lexStatus)
        primes = [getattr(row, c) for c in prime_columns]
        lookup[key] = (row.target, primes)
    return lookup


def main() -> None:
    PROCESSED_DIR.mkdir(exist_ok=True)

    df = load_trials()
    lookup = load_prime_lookup()

    # Participant IDs -> sequential integers starting at 1.
    participants = sorted(df["uniqSubId"].unique())
    id_map = {p: i + 1 for i, p in enumerate(participants)}
    df["participant_id"] = df["uniqSubId"].map(id_map)

    # Renumber trials from 1 (the practice block is not distributed).
    df["trial_order"] = df["trialNum"].astype(int) - N_PRACTICE_TRIALS

    # Attach the target string and the prime actually shown on this trial.
    keys = list(zip(df["targetNum"], df["lexStatus"]))
    conds = df["cond"].astype(int).to_numpy()
    targets, primes = [], []
    for (key, cond) in zip(keys, conds):
        target, prime_row = lookup[key]
        targets.append(target)
        primes.append(prime_row[cond - 1])
    df["stimulus"] = targets
    df["prime"] = primes

    df["condition"] = df["cond.label"]
    df["prime_code"] = df["cond.digits"]

    df["stimulus_type"] = df["lexStatus"].map({1: "word", 0: "nonword"})

    # RT is negative on incorrect trials; -2000 exactly marks a timeout.
    df["accuracy"] = df["correct"].astype(int)
    df["is_timeout"] = (df["RT"] == -RESPONSE_DEADLINE_MS).astype(int)
    df["rt"] = df["RT"].abs().round(2)

    # Two-alternative task: recover the response from accuracy and stimulus type.
    correct_response = df["stimulus_type"]
    other_response = df["stimulus_type"].map({"word": "nonword", "nonword": "word"})
    df["response"] = correct_response.where(df["accuracy"] == 1, other_response)
    df.loc[df["is_timeout"] == 1, "response"] = pd.NA

    scores = pd.read_csv(SCORES_FILE, encoding="utf-8")
    df = df.merge(scores, on="uniqSubId", how="left")

    df = df.sort_values(["participant_id", "trial_order"])
    out = df[OUTPUT_COLUMNS].copy()

    for column in ["participant_id", "trial_order", "accuracy", "is_timeout"]:
        out[column] = out[column].astype("Int64")

    output_path = PROCESSED_DIR / "exp1.csv"
    out.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"  rows:         {len(out):,}")
    print(f"  participants: {out['participant_id'].nunique():,}")
    print(f"  labs:         {out['lab'].nunique()}")
    print(f"  conditions:   {out['condition'].nunique()}")
    print(f"  accuracy:     {out['accuracy'].mean():.1%}")
    print(f"  timeouts:     {int(out['is_timeout'].sum()):,}")


if __name__ == "__main__":
    main()
