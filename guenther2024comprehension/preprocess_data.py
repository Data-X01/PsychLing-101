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
        {"column_name": "participant", "description": "Anonymized participant ID"},
        {"column_name": "age", "description": "Participant age in years"},
        {"column_name": "trial_index", "description": "Trial order index (factorized from raw trial_index)"},
        {"column_name": "stimulus", "description": "Concatenation of sentence_text and sentence_question_full"},
        {"column_name": "response", "description": "Participant's answer text"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "human_comprehension_data.csv"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    df = pd.read_csv(original_path)

    # Ensure attention check sentences end with a period + space (as in R)
    if "attention_check" in df.columns and "sentence_text" in df.columns:
        mask = df["attention_check"] == 1
        df.loc[mask, "sentence_text"] = df.loc[mask, "sentence_text"].astype(str) + ". "

    # Build stimulus
    if "sentence_text" in df.columns and "sentence_question_full" in df.columns:
        df["stimulus"] = df["sentence_text"].astype(str) + df["sentence_question_full"].astype(str)

    # Factorize trial_index
    if "trial_index" in df.columns:
        df["trial_index"] = pd.factorize(df["trial_index"])[0] + 1

    # Select and sort
    cols = ["participant", "age", "trial_index", "stimulus", "response"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant", "trial_index"] if c in df_out.columns])

    # Write
    out_path = processed_dir / "comprehension_questions_cleaned.csv"
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


