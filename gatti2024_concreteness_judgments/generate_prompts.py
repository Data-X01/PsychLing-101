from pathlib import Path
import json
import zipfile

import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
EXP1_FILE = DATASET_DIR / "processed_data" / "exp1.csv"
EXP2_FILE = DATASET_DIR / "processed_data" / "exp2.csv"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"


def json_scalar(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def format_rt_list(values):
    result = []
    for value in values:
        if pd.isna(value):
            result.append(None)
            continue
        value = round(float(value), 3)
        result.append(int(value) if value.is_integer() else value)
    return result


def get_instructions(condition_raw) -> str:
    condition = str(condition_raw).strip()
    if condition in {"A", "1"}:
        rule = "Scegli la parola più astratta."
    elif condition in {"B", "2"}:
        rule = "Scegli la parola più concreta."
    else:
        rule = "Scegli la parola che corrisponde meglio alla regola del compito."
    return (
        "Compito di giudizio. In ogni prova vedrai due parole, una a sinistra e una "
        f"a destra. {rule} Rispondi nel modo più rapido e accurato possibile."
    )


def build_prompt(pdf: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    lines = [get_instructions(pdf["condition_raw"].iloc[0])]

    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        lines.append(
            f"Prova {i}: A sinistra compare '{row.stimulus_left}' e a destra compare "
            f"'{row.stimulus_right}'. Scegli <<{row.response}>>."
        )

    return "\n".join(lines)


def build_record(participant_id, pdf: pd.DataFrame) -> dict:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    record = {
        "text": build_prompt(pdf),
        "experiment": str(pdf["experiment"].iloc[0]),
        "participant_id": json_scalar(participant_id),
        "age": json_scalar(pdf["age"].iloc[0]),
        "gender": json_scalar(pdf["gender"].iloc[0]),
        "condition": str(pdf["condition_raw"].iloc[0]),
    }

    if "hand" in pdf.columns:
        values = pdf["hand"].dropna()
        record["hand"] = None if values.empty else json_scalar(values.iloc[0])

    if "device" in pdf.columns:
        values = pdf["device"].dropna()
        record["device"] = None if values.empty else json_scalar(values.iloc[0])

    if "rt" in pdf.columns and pdf["rt"].notna().any():
        record["rt"] = format_rt_list(pdf["rt"])

    return record


def emit_records(df: pd.DataFrame, out_f):
    for participant_id, pdf in df.groupby("participant_id", sort=True):
        out_f.write(
            json.dumps(build_record(participant_id, pdf), ensure_ascii=False) + "\n"
        )


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


if __name__ == "__main__":
    main()
