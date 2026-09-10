from pathlib import Path
import pandas as pd

DATASET_DIR = Path("gatti2022_false_semantic_memory_pr")
RAW_FILE = DATASET_DIR / "original_data" / "data_DRM.xls"
OUT_DIR = DATASET_DIR / "processed_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_excel(RAW_FILE)

    df = df[[
        "ID", "age", "gender", "word", "resp_resp", "ord", "type", "type.2", "RT"
    ]].copy()

    df = df.rename(columns={
        "ID": "participant_id",
        "word": "stimulus",
        "resp_resp": "response",
        "ord": "trial_order",
        "type": "probe_type",
        "type.2": "condition",
        "RT": "rt",
    })

    # Normalize gender coding
    df["gender"] = df["gender"].astype(str).str.upper()

    # trial_order should be 0-indexed
    df["trial_order"] = df["trial_order"] - 1

    # Binary correctness based on studied vs new
    correct_map = {
        "studied": 1,
        "new": 0,
    }
    df["accuracy"] = (df["response"] == df["condition"].map(correct_map)).astype(int)

    df["experiment"] = "data_DRM"
    df["trial_id"] = "recognition_t" + df["trial_order"].astype(int).astype(str)
    df["phase_id"] = "recognition"

    df = df[[
        "experiment",
        "participant_id",
        "trial_id",
        "trial_order",
        "phase_id",
        "stimulus",
        "probe_type",
        "condition",
        "response",
        "accuracy",
        "rt",
        "age",
        "gender",
    ]]

    df = df.sort_values(["participant_id", "trial_order"]).reset_index(drop=True)

    outpath = OUT_DIR / "exp1.csv"
    df.to_csv(outpath, index=False)
    
    print("Wrote:", outpath)
    print("Shape:", df.shape)
    print("\nCONDITION COUNTS:")
    print(df["condition"].value_counts(dropna=False).to_string())
    print("\nPROBE TYPE COUNTS:")
    print(df["probe_type"].value_counts(dropna=False).to_string())
    print("\nFIRST 20 ROWS:")
    print(df.head(20).to_string(index=False))

if __name__ == "__main__":
    main()
