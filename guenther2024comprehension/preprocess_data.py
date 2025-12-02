import os
from pathlib import Path
import pandas as pd
import re


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
        {"column_name": "age", "description": "Participant age in years"},
        {"column_name": "trial_id", "description": "Trial order index (factorized from raw trial_id)"},
        {"column_name": "stimulus", "description": "Concatenation of sentence_text and sentence_question_full"},
        {"column_name": "response", "description": "Participant's answer text"},
        {"column_name": "experiment", "description": "Experiment number (1 or 2)"},
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


        
    
    # creating new column "experiment" extracting the substring betweeen the first and the second "_" in the "participant_id" column
    df['experiment'] = df['participant_id'].apply(lambda x: x.split('_')[1])
    
    #  remove the experiment prefix and the .csv suffix
    df["participant_id"] = df["participant_id"].str.replace("COMPR_1word_", "", regex=False)
    df["participant_id"] = df["participant_id"].str.replace("COMPR_open_", "", regex=False)
    df["participant_id"] = df["participant_id"].str.replace(".csv", "", regex=False)

    # turn age to float
    df["age"] = df["age"].astype(float)

    # sort by participant_id and trial_id
    df = df.sort_values(by=['participant_id', 'trial_id'])

    # Factorize trial_id
    if "trial_id" in df.columns:
        df["trial_id"] = pd.factorize(df["trial_id"])[0] + 1
    
    # Select and sort
    cols = ["experiment", "participant_id", "age", "trial_id", "stimulus", "response"]
    

    
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant_id", "trial_id"] if c in df_out.columns])

    exp1 = df_out[df_out['experiment'] == '1word']
    exp2 = df_out[df_out['experiment'] == 'open']
    
    # Write
    out_path1 = processed_dir / "exp1.csv"
    exp1.to_csv(out_path1, index=False)
    out_path2 = processed_dir / "exp2.csv"
    exp2.to_csv(out_path2, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


