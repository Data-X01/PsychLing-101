from pathlib import Path
import pandas as pd

DATASET_DIR = Path("gatti2023_semantic_priming")
RAW_FILE = DATASET_DIR / "original_data" / "data_acc.csv"
OUT_DIR = DATASET_DIR / "processed_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize_gender(x):
    x = str(x).strip().upper()
    if x in {"F", "M"}:
        return x
    return x

def normalize_hand(x):
    x = str(x).strip().upper()
    if x == "DX":
        return "right"
    if x == "SX":
        return "left"
    return x

def main():
    df = pd.read_csv(RAW_FILE, sep=";")

    df = df.rename(columns={
        "ID": "participant_id",
        "Prime": "prime",
        "Target": "target",
        "resp": "response",
        "resp_corr": "response_correct",
        "RTs": "rt_raw",
    })

    df["gender"] = df["gender"].apply(normalize_gender)
    df["hand"] = df["hand"].apply(normalize_hand)

    df["rt"] = pd.to_numeric(
        df["rt_raw"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

    # preserve source order within participant
    df["trial_order"] = df.groupby("participant_id").cumcount()
    df["trial_id"] = "exp1_t" + df["trial_order"].astype(str)
    df["experiment"] = "semantic_priming"
    df["phase_id"] = "judgment"

    df = df[[
        "experiment",
        "participant_id",
        "trial_id",
        "trial_order",
        "phase_id",
        "prime",
        "target",
        "response",
        "response_correct",
        "accuracy",
        "rt",
        "age",
        "gender",
        "hand",
    ]].copy()

    outpath = OUT_DIR / "exp1.csv"
    df.to_csv(outpath, index=False)

    print("Wrote:", outpath)
    print("Shape:", df.shape)

    print("\nUNIQUE PARTICIPANTS:")
    print(df["participant_id"].nunique())

    print("\nFIRST 20 ROWS:")
    print(df.head(20).to_string(index=False))

if __name__ == "__main__":
    main()
