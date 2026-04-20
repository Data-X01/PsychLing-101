from pathlib import Path
import json
import zipfile
import pandas as pd

DATASET_DIR = Path("gatti2022_false_semantic_memory_pr")
INFILE = DATASET_DIR / "processed_data" / "exp1.csv"
LISTS_FILE = DATASET_DIR / "original_data" / "liste.xls"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"

STUDY_INSTRUCTIONS = (
    "Study phase. You will see a series of words to memorize. "
    "Try to remember them for a later memory test."
)

RECOGNITION_INSTRUCTIONS = (
    "Recognition phase. You will now see one word at a time. "
    "Decide whether the word was studied before. "
    "Respond with 1 for OLD and 0 for NEW."
)

def load_study_materials() -> pd.DataFrame:
    df = pd.read_excel(LISTS_FILE)
    df = df.rename(columns={"text": "stimulus", "lista": "list_name"})
    return df

def build_prompt(pdf: pd.DataFrame, study_df: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    lines = [STUDY_INSTRUCTIONS]

    for i, row in enumerate(study_df.itertuples(index=False), start=1):
        lines.append(
            f"Study trial {i}: "
            f"The word is '{row.stimulus}'."
        )

    lines.append("")
    lines.append(RECOGNITION_INSTRUCTIONS)

    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        lines.append(
            f"Recognition trial {i}: "
            f"The word is '{row.stimulus}'. "
            f"You respond <<{int(row.response)}>>."
        )

    return "\n".join(lines)

def build_metadata(pdf: pd.DataFrame, study_df: pd.DataFrame) -> dict:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)

    return {
        "participant": int(pdf["participant_id"].iloc[0]),
        "experiment": str(pdf["experiment"].iloc[0]),
        "age": int(pdf["age"].iloc[0]),
        "gender": str(pdf["gender"].iloc[0]),
        "study_trials": [
            {
                "study_order": i,
                "stimulus": row.stimulus,
                "list_name": row.list_name,
            }
            for i, row in enumerate(study_df.itertuples(index=False), start=1)
        ],
        "recognition_trials": [
            {
                "trial_id": row.trial_id,
                "trial_order": int(row.trial_order),
                "phase_id": row.phase_id,
                "stimulus": row.stimulus,
                "probe_type": row.probe_type,
                "condition": row.condition,
                "response": int(row.response),
                "accuracy": int(row.accuracy),
                "rt": int(row.rt),
            }
            for row in pdf.itertuples(index=False)
        ],
    }

def main():
    df = pd.read_csv(INFILE)
    study_df = load_study_materials()

    with JSONL.open("w", encoding="utf-8") as f:
        for participant_id, pdf in df.groupby("participant_id", sort=True):
            record = build_metadata(pdf, study_df)
            record["text"] = build_prompt(pdf, study_df)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIPFILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSONL, arcname="prompts.jsonl")

    print("Wrote:", JSONL)
    print("Wrote:", ZIPFILE)
    print("Participants:", df["participant_id"].nunique())

    with JSONL.open("r", encoding="utf-8") as f:
        first = f.readline().strip()

    print("\nFIRST JSONL LINE:")
    print(first)

if __name__ == "__main__":
    main()
