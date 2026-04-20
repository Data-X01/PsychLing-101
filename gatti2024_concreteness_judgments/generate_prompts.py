from pathlib import Path
import json
import zipfile
import pandas as pd

DATASET_DIR = Path("gatti2024_concreteness_judgments")
EXP1_FILE = DATASET_DIR / "processed_data" / "exp1.csv"
EXP2_FILE = DATASET_DIR / "processed_data" / "exp2.csv"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"

def get_instructions(condition_raw) -> str:
    cond = str(condition_raw).strip()
    if cond in {"A", "1"}:
        return (
            "Judgment task. On each trial, you will see two words. "
            "Choose the more abstract word."
        )
    if cond in {"B", "2"}:
        return (
            "Judgment task. On each trial, you will see two words. "
            "Choose the more concrete word."
        )
    return (
        "Judgment task. On each trial, you will see two words. "
        "Choose the word that best matches the task rule."
    )

def build_prompt(pdf: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    instruction = get_instructions(pdf["condition_raw"].iloc[0])
    lines = [instruction]

    has_rt = "rt" in pdf.columns and pdf["rt"].notna().any()

    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        line = (
            f"Trial {i}: Left word '{row.stimulus_left}', "
            f"right word '{row.stimulus_right}'. "
            f"You choose <<{row.response}>>."
        )
        if has_rt and hasattr(row, "rt") and not pd.isna(row.rt):
            line += f" Reaction time: <<{float(row.rt):.1f} ms>>."
        lines.append(line)

    return "\n".join(lines)

def build_metadata(pdf: pd.DataFrame) -> dict:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)

    record = {
        "participant": int(pdf["participant_id"].iloc[0]),
        "experiment": str(pdf["experiment"].iloc[0]),
        "age": None if pd.isna(pdf["age"].iloc[0]) else float(pdf["age"].iloc[0]),
        "gender": None if pd.isna(pdf["gender"].iloc[0]) else str(pdf["gender"].iloc[0]),
        "condition_raw": str(pdf["condition_raw"].iloc[0]),
        "judgment_trials": []
    }

    if "hand" in pdf.columns:
        hand_val = pdf["hand"].dropna()
        record["hand"] = None if hand_val.empty else str(hand_val.iloc[0])

    if "device" in pdf.columns:
        dev_val = pdf["device"].dropna()
        record["device"] = None if dev_val.empty else str(dev_val.iloc[0])

    for row in pdf.itertuples(index=False):
        item = {
            "trial_id": row.trial_id,
            "trial_order": int(row.trial_order),
            "phase_id": row.phase_id,
            "stimulus_left": row.stimulus_left,
            "stimulus_right": row.stimulus_right,
            "response": row.response,
            "response_side": row.response_side,
            "condition_raw": row.condition_raw,
        }
        if hasattr(row, "rt") and not pd.isna(row.rt):
            item["rt"] = float(row.rt)
        record["judgment_trials"].append(item)

    return record

def emit_records(df: pd.DataFrame, out_f):
    for participant_id, pdf in df.groupby("participant_id", sort=True):
        record = build_metadata(pdf)
        record["text"] = build_prompt(pdf)
        out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

def main():
    exp1 = pd.read_csv(EXP1_FILE)
    exp2 = pd.read_csv(EXP2_FILE)

    with JSONL.open("w", encoding="utf-8") as f:
        emit_records(exp1, f)
        emit_records(exp2, f)

    with zipfile.ZipFile(ZIPFILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSONL, arcname="prompts.jsonl")

    print("Wrote:", JSONL)
    print("Wrote:", ZIPFILE)
    print("EXP1 participants:", exp1["participant_id"].nunique())
    print("EXP2 participants:", exp2["participant_id"].nunique())

    with JSONL.open("r", encoding="utf-8") as f:
        first = f.readline().strip()

    print("\nFIRST JSONL LINE:")
    print(first)

if __name__ == "__main__":
    main()
