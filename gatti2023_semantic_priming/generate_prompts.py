from pathlib import Path
import json
import zipfile

import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
INFILE = DATASET_DIR / "processed_data" / "exp1.csv"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"

INSTRUCTIONS = (
    "Compito di priming semantico. In ogni prova leggerai prima una parola e poi "
    "una seconda sequenza di lettere. Decidi se la seconda sequenza è una parola "
    "italiana esistente oppure una pseudoparola. Rispondi 1 per una parola "
    "esistente e 0 per una pseudoparola. Rispondi nel modo più rapido e accurato possibile."
)


def json_scalar(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    return value


def format_response(value):
    if pd.isna(value):
        return "nessuna risposta"
    return str(int(value))


def format_rt_list(values):
    result = []
    for value in values:
        if pd.isna(value):
            result.append(None)
            continue
        value = round(float(value), 3)
        result.append(int(value) if value.is_integer() else value)
    return result


def build_prompt(pdf: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    lines = [INSTRUCTIONS]

    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        lines.append(
            f"Prova {i}: Leggi prima la parola '{row.prime}' e poi la sequenza "
            f"'{row.target}'. Rispondi <<{format_response(row.response)}>>."
        )

    return "\n".join(lines)


def main():
    df = pd.read_csv(INFILE)

    with JSONL.open("w", encoding="utf-8") as f:
        for participant_id, pdf in df.groupby("participant_id", sort=True):
            pdf = pdf.sort_values("trial_order").reset_index(drop=True)
            record = {
                "text": build_prompt(pdf),
                "experiment": str(pdf["experiment"].iloc[0]),
                "participant_id": json_scalar(participant_id),
                "age": json_scalar(pdf["age"].iloc[0]),
                "gender": json_scalar(pdf["gender"].iloc[0]),
                "hand": json_scalar(pdf["hand"].iloc[0]),
                "rt": format_rt_list(pdf["rt"]),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIPFILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSONL, arcname="prompts.jsonl")

    print("Wrote:", JSONL)
    print("Wrote:", ZIPFILE)
    print("Participants:", df["participant_id"].nunique())


if __name__ == "__main__":
    main()
