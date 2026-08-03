#!/usr/bin/env python3
"""Create standardized processed datasets for all three experiments."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
ORIGINAL_DIR = DATASET_DIR / "original_data"
OUTPUT_DIR = DATASET_DIR / "processed_data"
INPUT_PATHS = {
    1: ORIGINAL_DIR / "exp1.csv",
    2: ORIGINAL_DIR / "exp2.csv",
    3: ORIGINAL_DIR / "exp3.csv",
}


def require_columns(data: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    """Raise a clear error when an input dataset lacks required columns."""
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {', '.join(missing)}"
        )


def normalize_gender(value: object) -> str:
    """Map source gender labels to the shared project vocabulary."""
    if pd.isna(value):
        return "unspecified"

    key = unicodedata.normalize("NFKD", str(value))
    key = key.encode("ascii", "ignore").decode("ascii")
    key = re.sub(r"\s+", " ", key.strip().lower())

    if key in {"mujer", "femenino"}:
        return "female"
    if key in {"hombre", "varon", "masculino"}:
        return "male"
    return "unspecified"


def participant_fields(data: pd.DataFrame, prefix: str) -> tuple[pd.Series, pd.Series]:
    """Create anonymous participant IDs and zero-based within-participant trial order."""
    codes, _ = pd.factorize(data["ID"], sort=False)
    participant_id = pd.Series(
        [f"{prefix}_{code}" for code in codes + 1],
        index=data.index,
        dtype="string",
    )
    trial_order = participant_id.groupby(participant_id, sort=False).cumcount()
    return participant_id, trial_order


def numeric(series: pd.Series, label: str) -> pd.Series:
    """Convert a source column to numbers without silently losing values."""
    try:
        return pd.to_numeric(series, errors="raise")
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} contains a non-numeric value") from error


def preprocess_exp1(raw: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        raw,
        [
            "ID",
            "response.text",
            "edad",
            "género",
            "generation.started",
            "generation.stopped",
            "Palabra",
            "emotion",
            "type",
        ],
        "original_data/exp1.csv",
    )

    data = raw.loc[raw["type"].eq("target")].reset_index(drop=True)
    participant_id, trial_order = participant_fields(data, "exp1")
    rt = (
        numeric(data["generation.stopped"], "exp1 generation.stopped")
        - numeric(data["generation.started"], "exp1 generation.started")
    ) * 1000

    return pd.DataFrame(
        {
            "experiment": "martineztomas2026_discrete_emotionality_exp1",
            "participant_id": participant_id,
            "trial_id": "exp1_t" + trial_order.astype(str),
            "trial_order": trial_order,
            "phase_id": "production",
            "stimulus": data["Palabra"],
            "response": data["response.text"],
            "emotion": data["emotion"],
            "rt": rt.round(3),
            "age": numeric(data["edad"], "exp1 edad").astype("Int64"),
            "gender": data["género"].map(normalize_gender),
        }
    )


def preprocess_exp2(raw: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        raw,
        [
            "ID",
            "edad",
            "género",
            "target_word",
            "response.text",
            "generation.started",
            "generation.stopped",
            "Palabra",
            "emotion",
        ],
        "original_data/exp2.csv",
    )

    data = raw.reset_index(drop=True)
    participant_id, trial_order = participant_fields(data, "exp2")
    rt = (
        numeric(data["generation.stopped"], "exp2 generation.stopped")
        - numeric(data["generation.started"], "exp2 generation.started")
    ) * 1000

    return pd.DataFrame(
        {
            "experiment": "martineztomas2026_discrete_emotionality_exp2",
            "participant_id": participant_id,
            "trial_id": "exp2_t" + trial_order.astype(str),
            "trial_order": trial_order,
            "phase_id": "word_decoding",
            "stimulus": data["Palabra"],
            "target_word": data["target_word"],
            "response": data["response.text"],
            "emotion": data["emotion"],
            "rt": rt.round(3),
            "age": numeric(data["edad"], "exp2 edad").astype("Int64"),
            "gender": data["género"].map(normalize_gender),
        }
    )


def preprocess_exp3(raw: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        raw,
        [
            "ID",
            "edad",
            "género",
            "Palabra",
            "target_word",
            "emotion_selected",
            "emotion",
            "accuracy",
            "RTs",
        ],
        "original_data/exp3.csv",
    )

    data = raw.reset_index(drop=True)
    participant_id, trial_order = participant_fields(data, "exp3")

    return pd.DataFrame(
        {
            "experiment": "martineztomas2026_discrete_emotionality_exp3",
            "participant_id": participant_id,
            "trial_id": "exp3_t" + trial_order.astype(str),
            "trial_order": trial_order,
            "phase_id": "emotion_decoding",
            "stimulus": data["Palabra"],
            "target_word": data["target_word"],
            "response": data["emotion_selected"],
            "response_correct": data["emotion"],
            "accuracy": numeric(data["accuracy"], "exp3 accuracy").astype("Int64"),
            "emotion": data["emotion"],
            "rt": (numeric(data["RTs"], "exp3 RTs") * 1000).round(3),
            "age": numeric(data["edad"], "exp3 edad").astype("Int64"),
            "gender": data["género"].map(normalize_gender),
        }
    )


def validate_output(data: pd.DataFrame, dataset_name: str) -> None:
    if data.duplicated(["participant_id", "trial_id"]).any():
        raise ValueError(f"{dataset_name} has duplicate participant/trial pairs")
    if data["rt"].isna().any() or data["rt"].le(0).any():
        raise ValueError(f"{dataset_name} has missing or non-positive RT values")
    responses = data["response"]
    if responses.isna().any() or responses.astype(str).str.strip().eq("").any():
        raise ValueError(f"{dataset_name} has missing or blank responses")


def main() -> None:
    missing_files = [str(path) for path in INPUT_PATHS.values() if not path.is_file()]
    if missing_files:
        raise FileNotFoundError(f"Missing input files: {', '.join(missing_files)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = {
        number: pd.read_csv(path, low_memory=False, keep_default_na=False)
        for number, path in INPUT_PATHS.items()
    }
    processed = {
        1: preprocess_exp1(raw[1]),
        2: preprocess_exp2(raw[2]),
        3: preprocess_exp3(raw[3]),
    }

    for number, data in processed.items():
        name = f"exp{number}"
        validate_output(data, name)
        output_path = OUTPUT_DIR / f"{name}.csv"
        data.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
            na_rep="",
            float_format="%.15g",
        )
        participant_count = data["participant_id"].nunique()
        print(f"{output_path}: {len(data)} rows, {participant_count} participants")


if __name__ == "__main__":
    main()
