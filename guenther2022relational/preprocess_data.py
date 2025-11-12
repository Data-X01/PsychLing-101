import os
from pathlib import Path
import pandas as pd


def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


def write_codebook(base_dir: Path) -> None:
    codebook_path = base_dir / "CODEBOOK.csv"
    if codebook_path.exists():
        return
    rows = [
        {"column_name": "participant", "description": "Anonymized participant ID (from 'subject')"},
        {"column_name": "age", "description": "Participant age in years (from 'age')"},
        {"column_name": "trial_index", "description": "Trial order index (factorized from raw trial_index)"},
        {"column_name": "stimulus", "description": "Stimulus string (from 'stim')"},
        {"column_name": "response", "description": "Participant response (from 'responses')"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "relational_entropy_novelcomp_raw.csv"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    df = pd.read_csv(original_path)

    # Rename / create canonical columns
    df = df.rename(columns={"subject": "participant", "responses": "response"})
    if "stim" in df.columns:
        df["stimulus"] = df["stim"]

    # Factorize trial_index to integers starting at 1
    if "trial_index" in df.columns:
        df["trial_index"] = pd.factorize(df["trial_index"])[0] + 1

    # Select and sort
    cols = ["participant", "age", "trial_index", "stimulus", "response"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant", "trial_index"] if c in df_out.columns])

    # Write
    out_path = processed_dir / "relations_compounds_cleaned.csv"
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


