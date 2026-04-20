from pathlib import Path
import json
import zipfile
import pandas as pd

DATASET_DIR = Path("gatti2023_semantic_priming")
INFILE = DATASET_DIR / "processed_data" / "exp1.csv"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"

INSTRUCTIONS = (
    "Semantic priming task. On each trial, you first read a prime word and then a target string. "
    "Judge whether the target is an existing word or a pseudoword. "
    "Respond with 1 for existing word and 0 for pseudoword."
)

def format_response(x):
    if pd.isna(x):
        return "NA"
    return str(int(x))

def format_rt(x):
    if pd.isna(x):
        return "NA"
    return f"{float(x):.6f}"

def build_prompt(pdf: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    lines = [INSTRUCTIONS]

    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        lines.append(
            f"Trial {i}: You read the prime '{row.prime}' and then the target '{row.target}'. "
            f"You respond <<{format_response(row.response)}>>. "
            f"Reaction time: <<{format_rt(row.rt)} s>>."
        )

    return "\n".join(lines)

def build_metadata(pdf: pd.DataFrame) -> dict:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)

    return {
        "participant": int(pdf["participant_id"].iloc[0]),
        "experiment": str(pdf["experiment"].iloc[0]),
        "age": int(pdf["age"].iloc[0]),
        "gender": str(pdf["gender"].iloc[0]),
        "hand": str(pdf["hand"].iloc[0]),
        "priming_trials": [
            {
                "trial_id": row.trial_id,
                "trial_order": int(row.trial_order),
                "phase_id": row.phase_id,
                "prime": row.prime,
                "target": row.target,
                "response": None if pd.isna(row.response) else int(row.response),
                "response_correct": None if pd.isna(row.response_correct) else int(row.response_correct),
                "accuracy": None if pd.isna(row.accuracy) else int(row.accuracy),
                "rt": None if pd.isna(row.rt) else float(row.rt),
            }
            for row in pdf.itertuples(index=False)
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
