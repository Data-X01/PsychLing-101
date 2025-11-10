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
        {"column_name": "age", "description": "Participant age in years (from 'Age')"},
        {"column_name": "trial_index", "description": "Trial order index (factorized from raw trial_index)"},
        {"column_name": "stimulus", "description": "Compound string shown on the trial (from 'comp')"},
        {"column_name": "response", "description": "Response key recoded to 'c' or 'n' (key 67 => 'c', else 'n')"},
        {"column_name": "RTs", "description": "Response time in ms (from 'rt')"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "dataset_diligent_LDT.txt"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    # Read whitespace-delimited table
    df = pd.read_table(original_path, delim_whitespace=True, engine="python")

    # Rename / create canonical columns
    df = df.rename(columns={"subject": "participant", "comp": "stimulus"})
    if "Age" in df.columns:
        df["age"] = df["Age"]
    if "rt" in df.columns:
        df["RTs"] = df["rt"]

    # Recode response from key_press
    df["response"] = "n"
    if "key_press" in df.columns:
        df.loc[df["key_press"] == 67, "response"] = "c"

    # Factorize trial_index to integers starting at 1
    if "trial_index" in df.columns:
        df["trial_index"] = pd.factorize(df["trial_index"])[0] + 1

    # Select and sort
    cols = ["participant", "age", "trial_index", "stimulus", "response", "RTs"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant", "trial_index"] if c in df_out.columns])
    
    # delete "association_" and ".csv" from the participant column
    df_out["participant"] = df_out["participant"].astype(str).str.replace("association_", "", regex=False)
    df_out["participant"] = df_out["participant"].str.replace(".csv", "", regex=False)

    # Write
    out_path = processed_dir / "LDT_compounds_cleaned.csv"
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


