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
        {"column_name": "participant_id", "description": "Anonymized participant ID"},
        {"column_name": "trial_id", "description": "Trial order index (factorized from raw trial_id)"},
        {"column_name": "stimulus", "description": "Four options concatenated as 'opt1; opt2; opt3; opt4'"},
        {"column_name": "best", "description": "Participant's 'best' choice string"},
        {"column_name": "worst", "description": "Participant's 'worst' choice string"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "data_study1_ratings_words_complete.txt"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    # TSV with quoted fields
    df = pd.read_csv(original_path, sep="\t")

    # Build stimulus from the 4 options
    for col in ["option1", "option2", "option3", "option4"]:
        if col not in df.columns:
            df[col] = ""
    df["stimulus"] = (
        df["option1"].astype(str).str.strip()
        + "; "
        + df["option2"].astype(str).str.strip()
        + "; "
        + df["option3"].astype(str).str.strip()
        + "; "
        + df["option4"].astype(str).str.strip()
    )

    # Factorize trial_id
    if "trial_id" in df.columns:
        df["trial_id"] = pd.factorize(df["trial_id"])[0] + 1

    # Select and sort
    cols = ["participant_id", "trial_id", "stimulus", "best", "worst"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant_id", "trial_id"] if c in df_out.columns])

    # Write
    out_path = processed_dir / "exp1.csv"
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


