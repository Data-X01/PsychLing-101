import os
from pathlib import Path
import pandas as pd
import numpy as np


def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


def write_codebook(base_dir: Path) -> None:
    codebook_path = base_dir / "CODEBOOK.csv"
    if codebook_path.exists():
        return
    rows = [
        {"column_name": "participant_id", "description": "Anonymized participant ID (numeric factor from raw ID)"},
        {"column_name": "age", "description": "Participant age in years (merged from demographics if available)"},
        {"column_name": "trial_id", "description": "Per-participant sequential index starting at 1"},
        {"column_name": "stimulus", "description": "Target word shown on the trial (from 'word')"},
        {"column_name": "response", "description": "Participant's substitution"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def clean_common(df: pd.DataFrame) -> pd.DataFrame:
    # Map to canonical names
    df = df.rename(columns={"ID": "participant_id"})
    if "word" in df.columns:
        df["stimulus"] = df["word"]

    # Create per-participant trial index
    if "participant_id" in df.columns:
        df["trial_id"] = df.groupby("participant_id").cumcount() + 1

    # Factorize participant to numeric
    if "participant_id" in df.columns:
        df["participant_id"] = pd.factorize(df["participant_id"])[0] + 1

    # turn age to float
    df["age"] = df["age"].astype(float)
    
    # Select canonical columns
    cols = ["participant_id", "age", "trial_id", "stimulus", "response"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant_id", "trial_id"] if c in df_out.columns])
    return df_out


def preprocess_exp1(base_dir: Path, processed_dir: Path) -> None:
    exp1_path = base_dir / "original_data" / "raw_data_exp1.csv"
    demo_path = base_dir / "original_data" / "demographics_exp1.txt"
    df = pd.read_csv(exp1_path)
    # demographics_exp1.txt is tab-separated
    if demo_path.exists():
        demo = pd.read_table(demo_path)
        df = df.merge(demo, on="ID", how="left")
    df = clean_common(df)
    out_path = processed_dir / "exp1.csv"
    df.to_csv(out_path, index=False)


def preprocess_exp2(base_dir: Path, processed_dir: Path) -> None:
    exp2_path = base_dir / "original_data" / "raw_data_exp2.csv"
    df = pd.read_csv(exp2_path)
    df = df.drop_duplicates()

    # demographics for exp2 may be unavailable in this folder; merge if found
    demo2_path = base_dir / "original_data" / "demographics_exp2.txt"
    if demo2_path.exists():
        demo2 = pd.read_table(demo2_path)
        df = df.merge(demo2, on="ID", how="left")

    # instruction list exists but not needed for final tidy output (R created it but did not use)
    df = clean_common(df)
    out_path = processed_dir / "exp2.csv"
    df.to_csv(out_path, index=False)


def preprocess_replication(base_dir: Path, processed_dir: Path) -> None:
    rep_path = base_dir / "original_data" / "raw_data_exp3.csv"
    if not rep_path.exists():
        return
    # exp3.csv is a CSV with header; first column may be an index
    try:
        df = pd.read_csv(rep_path, index_col=0)
    except Exception:
        df = pd.read_csv(rep_path)

    # Map columns to canonical schema
    # PID is the participant identifier in replication data
    if "PID" in df.columns:
        df = df.rename(columns={"PID": "participant_id"})
    else:
        df = df.rename(columns={"ID": "participant_id"})
    if "word" in df.columns:
        df["stimulus"] = df["word"]
    # Keep response as is

    # Create per-participant trial index starting at 1
    if "participant_id" in df.columns:
        df["trial_id"] = df.groupby("participant_id").cumcount() + 1

    # Factorize participant to numeric (to match exp1/exp2 outputs)
    if "participant_id" in df.columns:
        df["participant_id"] = pd.factorize(df["participant_id"])[0] + 1

    # Select canonical columns
    cols = ["participant_id", "age", "trial_id", "stimulus", "response"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant_id", "trial_id"] if c in df_out.columns])

    out_path = processed_dir / "exp3.csv"
    df_out.to_csv(out_path, index=False)


def preprocess(base_dir: Path) -> None:
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)
    preprocess_exp1(base_dir, processed_dir)
    preprocess_exp2(base_dir, processed_dir)
    preprocess_replication(base_dir, processed_dir)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


