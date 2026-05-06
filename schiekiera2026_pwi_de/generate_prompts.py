"""
generate_prompts.py
===================

Build PsychLing-101 LLM prompts for the schiekiera2026_pwi contribution,
German studies.

This script reads the standardized trial-level CSV from ``processed_data/``
and writes one JSON line per participant to:

* ``prompts.jsonl`` — German studies

Each output line follows PsychLing-101 §3.3 and has at minimum the fields::

    {
      "text":           "<instructions>\\n\\nTrial 1: …\\nTrial 2: …",
      "experiment":     "<experiment_id>",
      "participant_id": "<participant_id>",
      "rt":             [<int>, <int>, …]    # always included if available
      "age":            <float>              # optional, if column exists
      "first_language": "<str>"              # optional, if column exists
      …
    }

Conventions in ``text`` (see also ``pwi_prompt_examples.md``):

* Outcome marker ``<<…>>`` is reserved for the reaction time in milliseconds.
  In PWI the RT is the central dependent variable, so we mark it on every
  trial — irrespective of accuracy.
* ``accuracy`` and ``error_type`` appear as plain text in the trial line.
* Per-experiment-constant trial parameters (SOA, distractor modality,
  familiarization, …) are folded into the instruction block, not
  repeated per trial.
* Per-experiment-variable trial parameters (e.g. trial-by-trial
  ``congruency`` if it is not constant) appear as a parenthesised clause
  in each trial line.
* Instructions are uniform PWI-style across all studies; original
  per-study instruction texts are intentionally not used.
* Participants whose session exceeds the 32K-token limit are automatically
  split into two records (_part1 / _part2) by trial order.

Run from the experiment folder::

    python generate_prompts.py

Then zip the results for the PR::

    zip prompts.jsonl.zip prompts.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


# ---------- paths ----------------------------------------------------------

ROOT = Path(__file__).resolve().parent
PROCESSED_DIR = ROOT / "processed_data"

INPUT_FILE = "data_german.csv"
OUTPUT_PATH = ROOT / "prompts.jsonl"


# ---------- limits ---------------------------------------------------------

# PsychLing-101 hard limit per participant.
TOKEN_LIMIT = 32_000

# Rough character-to-token heuristic. 0.30 is conservative for English/German
# text. Replace with `tiktoken` or an Anthropic tokenizer for exact counts.
TOKENS_PER_CHAR = 0.30

# Experiments whose over-budget participants are split into 3 parts instead
# of the default 2 (used when ~half still exceeds TOKEN_LIMIT).
SPLIT_THREE_EXPERIMENTS: frozenset[str] = frozenset({
    "vieth_2014b_experiment3",
})


# ---------- instruction templates ------------------------------------------

INSTRUCTIONS_OVERT = (
    "You will see line drawings of everyday objects on the screen. "
    "{modality_clause}{soa_clause}. "
    "Your task is to name the object in the picture aloud as quickly and "
    "accurately as possible, while ignoring the distractor word."
    "{setting_clause}{familiarization_clause}{additional_clause}"
    "{gamified_clause}{condition_clause}"
)

INSTRUCTIONS_COVERT = (
    "You will see line drawings of everyday objects on the screen. "
    "{modality_clause}{soa_clause}. "
    "Your task is a covert task: silently retrieve the name of the "
    "depicted object and respond by pressing the appropriate response "
    "button. Do not name the picture aloud and ignore the distractor word."
    "{setting_clause}{familiarization_clause}{additional_clause}"
    "{gamified_clause}{condition_clause}"
)


# ---------- per-experiment-constant clauses --------------------------------

def _modality_clause(modality: Any) -> str:
    """Describe the picture/distractor modality in one sentence."""
    if pd.isna(modality):
        return "Each picture is shown together with a distractor word"
    m = str(modality).lower()
    if "audio" in m:
        return "Each picture is shown while a distractor word is played auditorily"
    return "Each picture is shown together with a visually presented distractor word"


def _soa_clause(soa: Any) -> str:
    if pd.isna(soa):
        return ""
    soa = int(round(float(soa)))
    if soa == 0:
        return " at simultaneous onset (SOA = 0 ms)"
    if soa < 0:
        return f", presented {abs(soa)} ms before picture onset (SOA = {soa} ms)"
    return f", presented {soa} ms after picture onset (SOA = +{soa} ms)"


def _setting_clause(value: Any) -> str:
    if pd.isna(value):
        return ""
    v = str(value).lower()
    if v == "online":
        return " The study was administered online."
    if v == "offline":
        return " The study was administered in a controlled lab setting."
    return ""


def _familiarization_clause(value: Any) -> str:
    if pd.isna(value) or str(value).lower() != "yes":
        return ""
    return " A familiarization phase preceded the main task."


def _additional_clause(value: Any) -> str:
    if pd.isna(value) or str(value).lower() != "yes":
        return ""
    return " The session also included additional unrelated tasks."


def _gamified_clause(value: Any) -> str:
    if pd.isna(value) or str(value).lower() != "yes":
        return ""
    return " The task was administered in a gamified format."


def _condition_clause(constants: dict[str, Any]) -> str:
    """Summarise condition columns that are constant across the experiment."""
    parts: list[str] = []

    cong = constants.get("congruency")
    if cong is not None:
        parts.append(f"all trials are {cong} picture-distractor pairs")

    for key, label in (
        ("categorical_relation", "categorical"),
        ("associative_relation", "associative"),
        ("phonological_relation", "phonological"),
    ):
        val = constants.get(key)
        if val is not None:
            parts.append(f"{label} relation: {val}")

    if not parts:
        return ""
    return " In this experiment, " + "; ".join(parts) + "."


# ---------- per-trial helpers ----------------------------------------------

_VARIABLE_CONDITION_COLS: tuple[tuple[str, str | None], ...] = (
    ("congruency", None),
    ("categorical_relation", "categorical"),
    ("associative_relation", "associative"),
    ("phonological_relation", "phonological"),
)


def _trial_variable_clause(row: dict[str, Any], constants: dict[str, Any]) -> str:
    """Per-trial clause for condition fields that vary across the experiment."""
    parts: list[str] = []
    for col, label in _VARIABLE_CONDITION_COLS:
        # Skip if this column is constant for the whole experiment — already
        # captured in the instruction block.
        if col in constants:
            continue
        val = row.get(col)
        if val is None or pd.isna(val):
            continue
        parts.append(str(val) if label is None else f"{label} relation: {val}")
    if not parts:
        return ""
    return f" ({'; '.join(parts)})"


def _accuracy_clause(row: dict[str, Any]) -> str:
    acc = row.get("accuracy")
    err = row.get("error_type")
    if acc is None or pd.isna(acc):
        return "No usable response recorded."
    if int(acc) == 1:
        return "Response correct."
    if err is not None and not pd.isna(err):
        return f"Response incorrect ({err})."
    return "Response incorrect."


def _rt_clause(row: dict[str, Any]) -> str:
    rt = row.get("rt")
    if rt is None or pd.isna(rt):
        return ""
    return f" RT: <<{int(round(float(rt)))}>> ms."


def _format_trial(row: dict[str, Any], idx: int, constants: dict[str, Any]) -> str:
    target = row.get("target_word_pwi")
    distractor = row.get("distractor_word_pwi")
    var_clause = _trial_variable_clause(row, constants)
    acc_clause = _accuracy_clause(row)
    rt_clause = _rt_clause(row)
    return (
        f'Trial {idx}: Picture of a {target}; distractor "{distractor}"'
        f"{var_clause}. {acc_clause}{rt_clause}"
    )


# ---------- experiment-level analysis --------------------------------------

_EXPERIMENT_CONSTANTS: tuple[str, ...] = (
    "soa",
    "distractor_modality",
    "collection_setting",
    "familiarization",
    "has_additional_tasks",
    "is_gamified",
    "congruency",
    "categorical_relation",
    "associative_relation",
    "phonological_relation",
)


def _experiment_constants(df_exp: pd.DataFrame) -> dict[str, Any]:
    """Return a dict of columns whose value is constant (after dropping NA)
    across the entire experiment — these go into the instruction block."""
    constants: dict[str, Any] = {}
    for col in _EXPERIMENT_CONSTANTS:
        if col not in df_exp.columns:
            continue
        unique = df_exp[col].dropna().unique()
        if len(unique) == 1:
            constants[col] = unique[0]
    return constants


def _build_instructions(constants: dict[str, Any], task_type: str) -> str:
    template = INSTRUCTIONS_OVERT if task_type == "overt" else INSTRUCTIONS_COVERT
    return template.format(
        modality_clause=_modality_clause(constants.get("distractor_modality")),
        soa_clause=_soa_clause(constants.get("soa")),
        setting_clause=_setting_clause(constants.get("collection_setting")),
        familiarization_clause=_familiarization_clause(
            constants.get("familiarization")
        ),
        additional_clause=_additional_clause(constants.get("has_additional_tasks")),
        gamified_clause=_gamified_clause(constants.get("is_gamified")),
        condition_clause=_condition_clause(constants),
    )


def _build_text(df_part: pd.DataFrame) -> str:
    task_type = str(df_part["naming_condition"].iloc[0]).strip().lower()
    constants = _experiment_constants(df_part)
    instructions = _build_instructions(constants, task_type)

    lines = [instructions, ""]
    for idx, row in enumerate(df_part.to_dict("records"), start=1):
        lines.append(_format_trial(row, idx, constants))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------- record builder -------------------------------------------------

# Optional participant-level metadata columns we copy into the JSON record
# whenever they exist and are non-null for the participant.
_OPTIONAL_META_COLS: tuple[str, ...] = (
    "age",
    "first_language",
    "nationality",
    "gender",
    "education",
    "country_of_birth",
    "country_of_residence",
    "clinical_diagnoses",
)


def _participant_record(
    experiment_id: str,
    participant_id: str,
    df_part: pd.DataFrame,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "text": _build_text(df_part),
        "experiment": experiment_id,
        "participant_id": participant_id,
    }

    # rt: list of trial-level RTs (None for missing values), in ms.
    rt_series = df_part["rt"]
    record["rt"] = [
        None if pd.isna(rt) else int(round(float(rt))) for rt in rt_series
    ]

    # Optional participant-level metadata: copy first non-null value.
    for col in _OPTIONAL_META_COLS:
        if col not in df_part.columns:
            continue
        non_null = df_part[col].dropna()
        if non_null.empty:
            continue
        val = non_null.iloc[0]
        # Coerce numpy types to plain Python for JSON serialisation.
        if hasattr(val, "item"):
            val = val.item()
        record[col] = val

    return record


# ---------- token estimation -----------------------------------------------

def _estimate_tokens(text: str) -> int:
    return int(len(text) * TOKENS_PER_CHAR)


# ---------- main pipeline --------------------------------------------------

def _process_language() -> tuple[int, int]:
    """Read the German CSV, build prompts, write to OUTPUT_PATH.

    Returns (n_records_written, n_participants_split).
    """
    path = PROCESSED_DIR / INPUT_FILE
    if not path.exists():
        print(f"  [skip] {INPUT_FILE} (not found)", file=sys.stderr)
        return 0, 0

    df = pd.read_csv(path, low_memory=False)
    print(f"  [read] {INPUT_FILE}: {len(df):,} rows, {len(df.columns)} cols")

    df = df.sort_values(
        by=["experiment_id", "participant_id", "trial_order"],
        kind="stable",
        na_position="last",
    )

    n_records = 0
    n_splits = 0

    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for (experiment_id, participant_id), df_part in df.groupby(
            ["experiment_id", "participant_id"], sort=False
        ):
            experiment_id = str(experiment_id)
            participant_id = str(participant_id)
            record = _participant_record(experiment_id, participant_id, df_part)
            tokens = _estimate_tokens(record["text"])

            if tokens > TOKEN_LIMIT:
                # Split session into equal parts by trial order.
                # Experiments with very long sessions use 3 parts; others 2.
                n_parts = 3 if experiment_id in SPLIT_THREE_EXPERIMENTS else 2
                chunk_size = len(df_part) // n_parts
                for i in range(n_parts):
                    start = i * chunk_size
                    end = start + chunk_size if i < n_parts - 1 else len(df_part)
                    chunk = df_part.iloc[start:end]
                    r = _participant_record(
                        experiment_id, participant_id + f"_part{i + 1}", chunk
                    )
                    out.write(json.dumps(r, ensure_ascii=False) + "\n")
                    n_records += 1
                n_splits += 1
            else:
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                n_records += 1

    print(f"  → {n_records:,} prompts written to {OUTPUT_PATH.name}", end="")
    if n_splits:
        print(f"  ({n_splits:,} participant(s) split due to token limit)", end="")
    print()
    return n_records, n_splits


def main() -> None:
    print(f"Reading processed data from {PROCESSED_DIR} …")

    n_records, n_splits = _process_language()

    print(f"\nTotal: {n_records:,} prompts")
    if n_splits:
        print(
            f"  {n_splits:,} participant(s) were split into 2 records "
            f"due to the {TOKEN_LIMIT:,}-token limit."
        )


if __name__ == "__main__":
    main()
