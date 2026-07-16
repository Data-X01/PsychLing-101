from pathlib import Path
import json
import zipfile

import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
INFILE = DATASET_DIR / "processed_data" / "exp1.csv"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"

STUDY_INSTRUCTIONS = (
    "Fase di studio. Vedrai una serie di parole da memorizzare. "
    "Cerca di ricordarle per una successiva prova di memoria."
)

RECOGNITION_INSTRUCTIONS = (
    "Fase di riconoscimento. Ora vedrai una parola alla volta. "
    "Decidi se la parola è stata presentata in precedenza. "
    "Rispondi 1 per VECCHIA e 0 per NUOVA."
)


def json_scalar(value):
    if hasattr(value, "item"):
        value = value.item()
    return value


def build_prompt(pdf: pd.DataFrame) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    study_df = pdf[pdf["phase_id"] == "study"]
    recog_df = pdf[pdf["phase_id"] == "recognition"]

    lines = [STUDY_INSTRUCTIONS]
    for i, row in enumerate(study_df.itertuples(index=False), start=1):
        lines.append(f"Prova di studio {i}: La parola è '{row.stimulus}'.")

    lines.extend(["", RECOGNITION_INSTRUCTIONS])
    for i, row in enumerate(recog_df.itertuples(index=False), start=1):
        lines.append(
            f"Prova di riconoscimento {i}: La parola è '{row.stimulus}'. "
            f"Rispondi <<{int(row.response)}>>."
        )

    return "\n".join(lines)


def main():
    df = pd.read_csv(INFILE)

    with JSONL.open("w", encoding="utf-8") as f:
        for participant_id, pdf in df.groupby("participant_id", sort=True):
            record = {
                "text": build_prompt(pdf),
                "experiment": str(pdf["experiment"].iloc[0]),
                "participant_id": json_scalar(participant_id),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIPFILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSONL, arcname="prompts.jsonl")

    print("Wrote:", JSONL)
    print("Wrote:", ZIPFILE)
    print("Participants:", df["participant_id"].nunique())


if __name__ == "__main__":
    main()
