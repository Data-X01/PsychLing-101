from pathlib import Path
import json
import zipfile

import numpy as np
import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
INFILE = DATASET_DIR / "processed_data" / "exp1.csv"
LISTS_FILE = DATASET_DIR / "original_data" / "liste.xls"
JSONL = DATASET_DIR / "prompts.jsonl"
ZIPFILE = DATASET_DIR / "prompts.jsonl.zip"

STUDY_INSTRUCTIONS = (
    "Fase di studio. Vedrai una serie di parole da memorizzare. "
    "Cerca di ricordarle per una successiva prova di memoria."
)

def randomized_choice_options(num_choices: int):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)


def recognition_instructions(choice_options) -> str:
    return (
        "Fase di riconoscimento. Ora vedrai una parola alla volta. "
        "Decidi se la parola è stata presentata in precedenza. "
        f"Rispondi {choice_options[1]} per VECCHIA e {choice_options[0]} per NUOVA."
    )


def json_scalar(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
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


def load_study_materials() -> pd.DataFrame:
    df = pd.read_excel(LISTS_FILE)
    return df.rename(columns={"text": "stimulus", "lista": "list_name"})


def build_prompt(pdf: pd.DataFrame, study_df: pd.DataFrame, choice_options) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    lines = [STUDY_INSTRUCTIONS]

    for i, row in enumerate(study_df.itertuples(index=False), start=1):
        lines.append(f"Prova di studio {i}: La parola è '{row.stimulus}'.")

    lines.extend(["", recognition_instructions(choice_options)])
    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        lines.append(
            f"Prova di riconoscimento {i}: La parola è '{row.stimulus}'. "
            f"Rispondi <<{choice_options[int(row.response)]}>>."
        )

    return "\n".join(lines)


def main():
    df = pd.read_csv(INFILE)
    study_df = load_study_materials()

    with JSONL.open("w", encoding="utf-8") as f:
        for participant_id, pdf in df.groupby("participant_id", sort=True):
            pdf = pdf.sort_values("trial_order").reset_index(drop=True)
            choice_options = randomized_choice_options(num_choices=2)
            record = {
                "text": build_prompt(pdf, study_df, choice_options),
                "experiment": str(pdf["experiment"].iloc[0]),
                "participant_id": json_scalar(participant_id),
                "age": json_scalar(pdf["age"].iloc[0]),
                "gender": json_scalar(pdf["gender"].iloc[0]),
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
