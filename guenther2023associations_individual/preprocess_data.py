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
    rows = [
        {"column_name": "participant", "description": "Anonymized participant ID (numeric)"},
        {"column_name": "age", "description": "Participant age in years"},
        {"column_name": "trial_index", "description": "0-based index of cue within participant"},
        {"column_name": "stimulus", "description": "Cue word (lowercased)"},
        {"column_name": "response1", "description": "First association response (lowercased)"},
        {"column_name": "response2", "description": "Second association response (lowercased)"},
        {"column_name": "response3", "description": "Third association response (lowercased)"},
        {"column_name": "response4", "description": "Fourth association response (lowercased)"},
        {"column_name": "response5", "description": "Fifth association response (lowercased)"},
        {"column_name": "response6", "description": "Sixth association response (lowercased)"},
        {"column_name": "response7", "description": "Seventh association response (lowercased)"},
        {"column_name": "response8", "description": "Eighth association response (lowercased)"},
        {"column_name": "response9", "description": "Ninth association response (lowercased)"},
        {"column_name": "response10", "description": "Tenth association response (lowercased)"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "raw_data_associations_individual.csv"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    # Some CSVs include an unnamed first index column; use index_col=0 to handle both cases robustly
    try:
        df = pd.read_csv(original_path, index_col=0)
    except Exception:
        df = pd.read_csv(original_path)

    # Select columns needed for wide output
    needed = ["participant", "age", "word", "resp.order", "critical_new", "trial_order"]
    df = df.loc[:, [c for c in needed if c in df.columns]].copy()
    df = df.rename(columns={"word": "cue", "critical_new": "response_clean"})

    # Normalize resp.order to ensure correct lexical ordering (critical01..critical10)
    if "resp.order" in df.columns:
        df["resp.order"] = df["resp.order"].astype(str)
        df["resp.order"] = df["resp.order"].str.replace("critical", "critical0", regex=False)
        df["resp.order"] = df["resp.order"].str.replace("critical010", "critical10", regex=False)

    # Lowercase textual fields
    if "cue" in df.columns:
        df["cue"] = df["cue"].astype(str).str.lower()
    if "response_clean" in df.columns:
        df["response_clean"] = df["response_clean"].astype(str).str.lower()

    # Clean participant IDs to numeric (remove 'association_' prefix and '.csv' suffix)
    df["participant"] = df["participant"].astype(str).str.replace("association_", "", regex=False)
    df["participant"] = df["participant"].str.replace(".csv", "", regex=False)
    # Cast to numeric where possible
    df["participant"] = pd.to_numeric(df["participant"], errors="ignore")

    # Deduplicate by participant + cue + response_clean
    subset_cols = [c for c in ["participant", "cue", "response_clean"] if c in df.columns]
    if subset_cols:
        df = df.drop_duplicates(subset=subset_cols, keep="first")

    # Extract numeric response position (1..10)
    df["resp_num"] = (
        df["resp.order"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
        .astype("Int64")
    )
    df = df[df["resp_num"].between(1, 10, inclusive="both")]

    # Compute trial_index (0-based) per (participant, cue), using trial_order if present, else first row order
    df["_row"] = np.arange(len(df))
    if "trial_order" in df.columns:
        first_order = (
            df.groupby(["participant", "cue"], as_index=False)["trial_order"]
            .min()
            .rename(columns={"trial_order": "_first_order"})
        )
    else:
        first_order = (
            df.groupby(["participant", "cue"], as_index=False)["_row"]
            .min()
            .rename(columns={"_row": "_first_order"})
        )

    # Wide pivot: response1..response10
    wide = (
        df.pivot_table(
            index=["participant", "cue"],
            columns="resp_num",
            values="response_clean",
            aggfunc="first",
        )
        .rename(columns=lambda n: f"response{int(n)}")
        .reset_index()
    )

    # Attach age (first per participant) and trial_index (rank within participant by first_order)
    age_by_participant = (
        df.dropna(subset=["age"])[["participant", "age"]]
        .drop_duplicates("participant")
    )
    wide = wide.merge(first_order, on=["participant", "cue"], how="left")
    wide = wide.merge(age_by_participant, on="participant", how="left")
    wide["_rank_within_participant"] = (
        wide.sort_values(["participant", "_first_order"])
        .groupby("participant")
        .cumcount()
    )
    wide = wide.rename(columns={"cue": "stimulus", "_rank_within_participant": "trial_index"})

    # Ensure all response columns exist and are strings
    for i in range(1, 11):
        col = f"response{i}"
        if col not in wide.columns:
            wide[col] = ""
        wide[col] = wide[col].fillna("").astype(str)

    # Final ordering and sorting
    final_cols = ["participant", "age", "trial_index", "stimulus"] + [f"response{i}" for i in range(1, 11)]
    df_out = wide.loc[:, final_cols]
    df_out = df_out.sort_values(["participant", "trial_index"]).reset_index(drop=True)

    # Make participant and age numeric if possible (needed by generate_prompts.py which uses .item())
    df_out["participant"] = pd.to_numeric(df_out["participant"], errors="coerce")
    if "age" in df_out.columns:
        df_out["age"] = pd.to_numeric(df_out["age"], errors="coerce")

    # Write wide format expected by generate_prompts.py
    out_path = processed_dir / "data_individual.csv"
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


