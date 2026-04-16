from pathlib import Path
import json
import zipfile
import pandas as pd

DATASET_DIR = Path("gatti2022_false_semantic_memory")
INFILE = DATASET_DIR / "processed_data" / "exp1.csv"
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

def build_prompt(pdf: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)

    study_df = pdf[pdf["phase_id"] == "study"].copy()
    recog_df = pdf[pdf["phase_id"] == "recognition"].copy()

    lines = [STUDY_INSTRUCTIONS]

    for i, row in enumerate(study_df.itertuples(index=False), start=1):
        lines.append(
            f"Study trial {i}: The word is '{row.stimulus}'."
        )

    lines.append("")
    lines.append(RECOGNITION_INSTRUCTIONS)

    for i, row in enumerate(recog_df.itertuples(index=False), start=1):
        lines.append(
            f"Recognition trial {i}: "
            f"The word is '{row.stimulus}'. "
            f"You respond <<{int(row.response)}>>."
        )

    return "\n".join(lines)

def build_metadata(pdf: pd.DataFrame) -> dict:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)

    study_df = pdf[pdf["phase_id"] == "study"].copy()
    recog_df = pdf[pdf["phase_id"] == "recognition"].copy()

    return {
        "participant": int(pdf["participant_id"].iloc[0]),
        "experiment": str(pdf["experiment"].iloc[0]),
        "study_trials": [
            {
                "trial_id": row.trial_id,
                "trial_order": int(row.trial_order),
                "phase_id": row.phase_id,
                "list": None if pd.isna(row.list) else int(row.list),
                "list_name": None if pd.isna(row.list_name) else str(row.list_name),
                "stimulus": row.stimulus,
            }
            for row in study_df.itertuples(index=False)
        ],
        "recognition_trials": [
            {
                "trial_id": row.trial_id,
                "trial_order": int(row.trial_order),
                "phase_id": row.phase_id,
                "list": None if pd.isna(row.list) else int(row.list),
                "list_name": None if pd.isna(row.list_name) else str(row.list_name),
                "stimulus": row.stimulus,
                "condition": row.condition,
                "response": int(row.response),
                "accuracy": int(row.accuracy),
            }
            for row in recog_df.itertuples(index=False)
        ],
    }

def main():
    df = pd.read_csv(INFILE)

    with JSONL.open("w", encoding="utf-8") as f:
        for participant_id, pdf in df.groupby("participant_id", sort=True):
            record = build_metadata(pdf)
            record["text"] = build_prompt(pdf)
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
