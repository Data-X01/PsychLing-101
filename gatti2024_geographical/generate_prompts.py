from pathlib import Path
import json
import zipfile

import numpy as np
import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
INPUT_PATH = DATASET_DIR / "processed_data" / "exp1.csv"
OUTPUT_PATH = DATASET_DIR / "prompts.jsonl"
ZIP_PATH = DATASET_DIR / "prompts.jsonl.zip"

def randomized_choice_options(num_choices: int):
    choice_options = list(map(chr, range(65, 91)))
    return np.random.choice(choice_options, num_choices, replace=False)


def build_instructions(choice_options) -> str:
    return (
        "In questo compito vedrai i nomi di due città italiane, una a sinistra e una "
        "a destra. Indica quale città è geograficamente più vicina a Milano. "
        f"Premi {choice_options[0]} per scegliere la città a sinistra oppure "
        f"{choice_options[1]} per scegliere la città a destra. Rispondi nel modo "
        "più rapido e accurato possibile."
    )


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


def build_text(pdf: pd.DataFrame, choice_options) -> str:
    pdf = pdf.sort_values("trial_order").reset_index(drop=True)
    lines = [build_instructions(choice_options)]
    side_to_choice = {"left": choice_options[0], "right": choice_options[1]}
    for i, row in enumerate(pdf.itertuples(index=False), start=1):
        lines.append(
            f"Prova {i}: A sinistra compare '{row.city_left}' e a destra compare "
            f"'{row.city_right}'. Premi <<{side_to_choice[row.response_side]}>>."
        )
    return "\n".join(lines)


def main():
    df = pd.read_csv(INPUT_PATH)

    required_cols = [
        "experiment",
        "participant_id",
        "trial_order",
        "age",
        "gender",
        "hand",
        "city_left",
        "city_right",
        "response_raw",
        "rt_ms",
    ]
    missing = [column for column in required_cols if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for participant_id, pdf in df.groupby("participant_id", sort=True):
            pdf = pdf.sort_values("trial_order").reset_index(drop=True)
            choice_options = randomized_choice_options(num_choices=2)
            record = {
                "text": build_text(pdf, choice_options),
                "experiment": str(pdf["experiment"].iloc[0]),
                "participant_id": json_scalar(participant_id),
                "age": json_scalar(pdf["age"].iloc[0]),
                "gender": json_scalar(pdf["gender"].iloc[0]),
                "hand": json_scalar(pdf["hand"].iloc[0]),
                "rt": format_rt_list(pdf["rt_ms"]),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUTPUT_PATH, arcname="prompts.jsonl")

    print("Wrote:", OUTPUT_PATH)
    print("Wrote:", ZIP_PATH)
    print("Participants:", df["participant_id"].nunique())


if __name__ == "__main__":
    main()
