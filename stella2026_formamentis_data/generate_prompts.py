#!/usr/bin/env python3
"""
Generate LLM prompts for the behavioural Forma Mentis task.

Place this file in the experiment/dataset folder, next to processed_data/.

Expected input:
    processed_data/exp1.csv

Expected output:
    prompts.jsonl
    prompts.jsonl.zip
    prompt_generation_report.csv

Each line in prompts.jsonl is one participant session and contains at least:
    text
    experiment
    participant_id

The prompt text encodes, trial by trial, the behavioural Forma Mentis data:
    - one cue word
    - three ordered free associations/responses
    - four ordered valence ratings:
        cue valence, response1 valence, response2 valence, response3 valence

Human-entered responses and continuous/ordinal behavioural outcomes are marked
with double angle markers, as required by the PsychLing-101 prompt-generation
instructions. The script sanitizes raw text so those markers appear only where
the script deliberately inserts them.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Use the dataset folder name as a stable default if desired, but for this
# contribution the intended identifier is the Forma Mentis dataset folder.
DEFAULT_EXPERIMENT_ID = "stella2026_formamentis_data"

EXPECTED_N_PARTICIPANTS = 177
EXPECTED_MAX_TRIALS_PER_PARTICIPANT = 10
EXPECTED_MIN_TRIALS_PER_PARTICIPANT = 8

# Approximate 32K-token safeguard. 32K tokens is usually far above this
# dataset's prompt length, but this conservative character cap prevents
# accidental runaway prompts.
MAX_PROMPT_CHARS = 120_000

REQUIRED_COLUMNS = [
    "participant_id",
    "source_file",
    "age",
    "gender",
    "nationality",
    "first_language",
    "occupation",
    "stem_background",
    "trial_id",
    "trial_order",
    "stimulus",
    "response1",
    "response2",
    "response3",
    "stimulus_valence",
    "response1_valence",
    "response2_valence",
    "response3_valence",
]

WORD_COLUMNS = ["stimulus", "response1", "response2", "response3"]
VALENCE_COLUMNS = [
    "stimulus_valence",
    "response1_valence",
    "response2_valence",
    "response3_valence",
]
METADATA_COLUMNS = [
    "source_file",
    "age",
    "gender",
    "nationality",
    "first_language",
    "occupation",
    "stem_background",
]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def find_processed_csvs(base_dir: Path) -> list[Path]:
    """Find standardized exp*.csv files.

    The repository convention is processed_data/exp1.csv, processed_data/exp2.csv,
    etc. As a convenience for local testing, this also accepts exp1.csv in the
    dataset folder if processed_data/ is absent.
    """
    exp_name = re.compile(r"^exp\d+\.csv$", flags=re.IGNORECASE)

    processed_dir = base_dir / "processed_data"
    if processed_dir.exists():
        files = sorted(p for p in processed_dir.iterdir() if p.is_file() and exp_name.match(p.name))
        if files:
            return files

    files = sorted(p for p in base_dir.iterdir() if p.is_file() and exp_name.match(p.name))
    if files:
        return files

    raise FileNotFoundError(
        "Could not find standardized CSV files. Expected files named exp1.csv, "
        "exp2.csv, ... inside processed_data/ or inside the dataset folder."
    )


def read_standardized_data(csv_paths: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in csv_paths:
        frame = pd.read_csv(path)
        frame["experiment_file"] = path.name
        frames.append(frame)

    if not frames:
        raise ValueError("No CSV files were provided.")

    exp = pd.concat(frames, ignore_index=True)

    missing = [col for col in REQUIRED_COLUMNS if col not in exp.columns]
    if missing:
        raise ValueError(
            "The standardized CSV file is missing required columns: "
            + ", ".join(missing)
        )

    return exp


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if isinstance(value, float) and math.isnan(value):
            return True
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def clean_word(value: Any) -> str | None:
    """Clean a cue/response word for safe prompt display.

    This removes quotation marks, duplicated whitespace, and accidental marker
    symbols so that double angle markers are introduced only by this script.
    """
    if is_missing(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    replacements = {
        "\u2018": "",
        "\u2019": "",
        "\u201c": "",
        "\u201d": "",
        '"': "",
        "'": "",
        "`": "",
        "\n": " ",
        "\r": " ",
        "\t": " ",
        "<<": "",
        ">>": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def clean_metadata(value: Any) -> Any:
    """Convert metadata to JSON-safe scalars."""
    if is_missing(value):
        return None

    if isinstance(value, (int, str, bool)):
        return value

    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return value

    # Convert numpy/pandas scalar values if present.
    if hasattr(value, "item"):
        try:
            return clean_metadata(value.item())
        except Exception:
            pass

    text = str(value).strip()
    return text if text else None


def format_rating(value: Any) -> str | None:
    """Format valence ratings as compact JSON/prompt-safe text."""
    if is_missing(value):
        return None

    try:
        number = float(value)
        if math.isnan(number):
            return None
        if number.is_integer():
            return str(int(number))
        return f"{number:g}"
    except (TypeError, ValueError):
        text = str(value).strip()
        return text if text else None


def marked(value: str) -> str:
    """Mark one human response or behavioural outcome."""
    # Input has already been sanitized. This is the only place where marker
    # symbols should be introduced.
    safe = value.replace("<<", "").replace(">>", "")
    return f"<<{safe}>>"


def first_non_missing(series: pd.Series) -> Any:
    for value in series:
        if not is_missing(value):
            return clean_metadata(value)
    return None


def build_instruction() -> str:
    """Return the task instructions at the start of every prompt."""
    # Do not spell out the marker symbols in this instruction. They appear only
    # around actual human responses and behavioural ratings below.
    return (
        "You are taking part in a behavioural forma mentis word-association task.\n"
        "On each trial, a cue word appears on the screen.\n"
        "For every cue word, enter the first three single-word associations that come to mind, in order.\n"
        "Only associate to the cue word shown on the screen, not to your previous responses.\n"
        "After entering the associations, rate the emotional valence of the cue and of each association on a scale from 1 (very negative) to 5 (very positive).\n"
        "Please only enter single words.\n"
    )


def build_trial_text(row: pd.Series, display_trial_number: int) -> tuple[str, int]:
    stimulus = clean_word(row["stimulus"])
    if stimulus is None:
        stimulus = "not recorded"

    response_values = [clean_word(row[f"response{i}"]) for i in range(1, 4)]
    valence_values = [
        format_rating(row["stimulus_valence"]),
        format_rating(row["response1_valence"]),
        format_rating(row["response2_valence"]),
        format_rating(row["response3_valence"]),
    ]

    response_parts = []
    complete_responses = 0
    for i, response in enumerate(response_values, start=1):
        if response is None:
            response_parts.append(f"association {i} not provided")
        else:
            response_parts.append(f"association {i} {marked(response)}")
            complete_responses += 1

    # The cue is a displayed stimulus, not a human-entered response; therefore
    # it is not marked. Valence ratings are behavioural outcomes and are marked.
    valence_labels = [
        f"cue {stimulus}",
        "association 1",
        "association 2",
        "association 3",
    ]
    valence_parts = []
    for label, rating in zip(valence_labels, valence_values):
        if rating is None:
            valence_parts.append(f"{label} valence not recorded")
        else:
            valence_parts.append(f"{label} valence {marked(rating)}")

    trial_text = (
        f"Trial {display_trial_number}: The cue word shown is {stimulus}. "
        f"The participant enters {', '.join(response_parts)}. "
        f"The participant provides valence ratings: {', '.join(valence_parts)}.\n"
    )

    return trial_text, complete_responses


def build_prompt_for_participant(
    participant_id: str,
    participant_df: pd.DataFrame,
) -> tuple[str, dict[str, Any]]:
    participant_df = participant_df.sort_values(["experiment_file", "trial_order", "trial_id"])

    text = build_instruction()

    complete_trials = 0
    total_trials = 0
    for display_trial_number, (_, row) in enumerate(participant_df.iterrows(), start=1):
        trial_text, n_responses = build_trial_text(row, display_trial_number)
        text += trial_text
        total_trials += 1
        if n_responses == 3:
            complete_trials += 1

    if "<<" in participant_id or ">>" in participant_id:
        participant_id = participant_id.replace("<<", "").replace(">>", "")

    if len(text) > MAX_PROMPT_CHARS:
        raise ValueError(
            f"Prompt for participant {participant_id} has {len(text)} characters, "
            f"which exceeds the configured 32K-token safeguard."
        )

    first_row_metadata = {
        col: first_non_missing(participant_df[col])
        for col in METADATA_COLUMNS
        if col in participant_df.columns
    }

    summary = {
        "n_trials": total_trials,
        "n_complete_association_trials": complete_trials,
        **first_row_metadata,
    }

    return text, summary


def validate_dataset(exp: pd.DataFrame, expected_n: int | None, allow_non177: bool) -> None:
    n_participants = exp["participant_id"].nunique()
    n_rows = len(exp)

    trial_counts = exp.groupby("participant_id").size()
    min_trials = int(trial_counts.min())
    max_trials = int(trial_counts.max())

    print(f"Rows read: {n_rows}")
    print(f"Participants read: {n_participants}")
    print(f"Trials per participant: min={min_trials}, max={max_trials}")

    if expected_n is not None and n_participants != expected_n:
        message = (
            f"Expected {expected_n} valid participants, but found {n_participants}. "
            "Use the already-filtered exp1.csv containing only valid participants, "
            "or rerun the validity-selection script before generating prompts."
        )
        if allow_non177:
            print("WARNING:", message, file=sys.stderr)
        else:
            raise ValueError(message)

    if min_trials < EXPECTED_MIN_TRIALS_PER_PARTICIPANT or max_trials > EXPECTED_MAX_TRIALS_PER_PARTICIPANT:
        print(
            "WARNING: expected either 8 or 9 or 10 trials per participant,"
            f"but observed min={min_trials}, max={max_trials}.",
            file=sys.stderr,
        )


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        for record in records:
            # allow_nan=False prevents non-standard JSON values such as NaN.
            f.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


def write_zip(jsonl_path: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(jsonl_path, arcname=jsonl_path.name)


def write_report(records: list[dict[str, Any]], report_path: Path) -> None:
    fieldnames = [
        "participant_id",
        "experiment",
        "source_file",
        "n_trials",
        "n_complete_association_trials",
        "text_n_chars",
        "age",
        "gender",
        "nationality",
        "first_language",
        "occupation",
        "stem_background",
    ]

    with report_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({
                "participant_id": record.get("participant_id"),
                "experiment": record.get("experiment"),
                "source_file": record.get("source_file"),
                "n_trials": record.get("n_trials"),
                "n_complete_association_trials": record.get("n_complete_association_trials"),
                "text_n_chars": len(record.get("text", "")),
                "age": record.get("age"),
                "gender": record.get("gender"),
                "nationality": record.get("nationality"),
                "first_language": record.get("first_language"),
                "occupation": record.get("occupation"),
                "stem_background": record.get("stem_background"),
            })


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate participant-level JSONL prompts for the Forma Mentis task."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).parent.resolve(),
        help="Dataset folder containing processed_data/exp1.csv. Defaults to this script's folder.",
    )
    parser.add_argument(
        "--experiment",
        default=DEFAULT_EXPERIMENT_ID,
        help="Experiment identifier written to each JSONL record.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path for prompts.jsonl. Defaults to BASE_DIR/prompts.jsonl.",
    )
    parser.add_argument(
        "--expected-participants",
        type=int,
        default=EXPECTED_N_PARTICIPANTS,
        help="Expected number of valid participants. Defaults to 177.",
    )
    parser.add_argument(
        "--allow-non177",
        action="store_true",
        help="Generate prompts even if the participant count is not 177.",
    )

    args = parser.parse_args()

    base_dir = args.base_dir.resolve()
    output_jsonl = args.output.resolve() if args.output else base_dir / "prompts.jsonl"
    output_zip = output_jsonl.with_suffix(output_jsonl.suffix + ".zip")
    report_path = base_dir / "prompt_generation_report.csv"

    csv_paths = find_processed_csvs(base_dir)
    print("Reading standardized CSV file(s):")
    for path in csv_paths:
        print(f"  - {path}")

    exp = read_standardized_data(csv_paths)
    validate_dataset(exp, expected_n=args.expected_participants, allow_non177=args.allow_non177)

    records: list[dict[str, Any]] = []

    # One line per participant per standardized experiment file. With the current
    # dataset this is simply 177 lines from exp1.csv.
    grouped = exp.groupby(["experiment_file", "participant_id"], sort=True, dropna=False)

    for (experiment_file, participant_id), participant_df in grouped:
        participant_id = clean_word(participant_id) or str(participant_id)
        text, metadata = build_prompt_for_participant(participant_id, participant_df)

        record = {
            "text": text,
            "experiment": args.experiment,
            "participant_id": participant_id,
            **metadata,
            "experiment_file": experiment_file,
        }
        records.append(record)

    write_jsonl(records, output_jsonl)
    write_zip(output_jsonl, output_zip)
    write_report(records, report_path)

    print(f"Wrote {len(records)} participant-level prompts to {output_jsonl}")
    print(f"Wrote zipped prompts to {output_zip}")
    print(f"Wrote audit report to {report_path}")


if __name__ == "__main__":
    main()
