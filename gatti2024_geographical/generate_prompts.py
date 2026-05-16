from pathlib import Path
import json
import pandas as pd


DATASET_DIR = Path(__file__).resolve().parent
INPUT_PATH = DATASET_DIR / "processed_data" / "exp1.csv"
OUTPUT_PATH = DATASET_DIR / "prompts.jsonl"


def build_text(row):
    return (
        "Task: decide which city is geographically closer to Milan.\n"
        f"Left city: {row['city_left']}\n"
        f"Right city: {row['city_right']}\n"
        "Response options: a = left, l = right.\n"
        f"Participant response: {row['response_raw']}\n"
        f"Reaction time (ms): {row['rt_ms']}"
    )


def main():
    df = pd.read_csv(INPUT_PATH)

    required_cols = [
        "participant_id",
        "age",
        "gender",
        "hand",
        "hand_raw",
        "city_left",
        "city_right",
        "response_raw",
        "response_side",
        "correct_response",
        "correct_side",
        "accuracy",
        "response_correct",
        "rt_raw",
        "rt_ms",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    records = []
    for row in df.to_dict(orient="records"):
        record = {
            "text": build_text(row),
            "metadata": {
                "dataset": "gatti2024_geographical",
                "subset": "exp1",
                "participant_id": row["participant_id"],
                "age": None if pd.isna(row["age"]) else int(row["age"]),
                "gender": row["gender"],
                "hand": row["hand"],
                "hand_raw": row["hand_raw"],
                "city_left": row["city_left"],
                "city_right": row["city_right"],
                "response_raw": row["response_raw"],
                "response_side": row["response_side"],
                "correct_response": row["correct_response"],
                "correct_side": row["correct_side"],
                "accuracy": None if pd.isna(row["accuracy"]) else int(row["accuracy"]),
                "response_correct": None if pd.isna(row["response_correct"]) else int(row["response_correct"]),
                "rt_raw": row["rt_raw"],
                "rt_ms": None if pd.isna(row["rt_ms"]) else float(row["rt_ms"]),
            },
        }
        records.append(record)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Rows: {len(records)}")
    print("\nFIRST_RECORD:")
    print(json.dumps(records[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
