from pathlib import Path
import pandas as pd

DATASET_DIR = Path("gatti2022_false_semantic_memory")
RAW_FILE = DATASET_DIR / "original_data" / "database_DRM.xlsx"
OUT_DIR = DATASET_DIR / "processed_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LIST_NAME_TO_ID = {
    "ago": 1,
    "alto": 2,
    "amaro": 3,
    "bandiera": 4,
    "fiume": 5,
    "freddo": 6,
    "fumo": 7,
    "giustizia": 8,
    "ladro": 9,
    "lampada": 10,
    "lento": 11,
    "musica": 12,
    "penna": 13,
    "ragno": 14,
    "sedia": 15,
    "soffice": 16,
}

def load_raw():
    study = pd.read_excel(RAW_FILE, sheet_name="EXP.1.1")
    recog = pd.read_excel(RAW_FILE, sheet_name="EXP.1.2")
    return study, recog

def build_study_trials(study: pd.DataFrame, recog: pd.DataFrame) -> pd.DataFrame:
    studied_lists = (
        recog[recog["Type"] == "critical_lure"]
        .groupby("Subject")["word"]
        .agg(list)
        .to_dict()
    )

    base_study = study[["Word", "Position", "List"]].copy()
    base_study = base_study.rename(columns={
        "Word": "stimulus",
        "Position": "position_in_list",
        "List": "list_name",
    })

    rows = []
    for participant_id, lists_for_participant in studied_lists.items():
        tmp = base_study[base_study["list_name"].isin(lists_for_participant)].copy()
        tmp["participant_id"] = participant_id
        tmp["phase_id"] = "study"
        rows.append(tmp)

    df = pd.concat(rows, ignore_index=True)

    df["list"] = df["list_name"].map(LIST_NAME_TO_ID)
    df = df.sort_values(["participant_id", "list", "position_in_list"]).reset_index(drop=True)
    df["trial_order"] = df.groupby("participant_id").cumcount()
    df["trial_id"] = "study_t" + df["trial_order"].astype(str)
    df["experiment"] = "EXP.1"
    df["condition"] = "studied_word"
    df["response"] = pd.NA
    df["accuracy"] = pd.NA

    df = df[
        [
            "experiment",
            "participant_id",
            "trial_id",
            "trial_order",
            "phase_id",
            "list",
            "list_name",
            "stimulus",
            "condition",
            "response",
            "accuracy",
        ]
    ]
    return df

def build_recognition_trials(recog: pd.DataFrame, n_study_trials_by_participant: pd.Series) -> pd.DataFrame:
    df = recog[["Subject", "word", "Response", "Type", "Type2"]].copy()

    df = df.rename(columns={
        "Subject": "participant_id",
        "word": "stimulus",
        "Response": "response",
        "Type": "probe_type",
        "Type2": "condition",
    })

    df["list_name"] = pd.NA
    df.loc[df["probe_type"] == "critical_lure", "list_name"] = df.loc[df["probe_type"] == "critical_lure", "stimulus"]
    df["list"] = df["list_name"].map(LIST_NAME_TO_ID)

    correct_map = {
        "false_recog": 0,
        "veridical_recog": 1,
    }
    df["accuracy"] = (df["response"] == df["condition"].map(correct_map)).astype(int)

    df["phase_id"] = "recognition"
    df["recog_order"] = df.groupby("participant_id").cumcount()
    df["trial_order"] = df["participant_id"].map(n_study_trials_by_participant) + df["recog_order"]
    df["trial_id"] = "recognition_t" + df["recog_order"].astype(str)
    df["experiment"] = "EXP.1"

    df = df[
        [
            "experiment",
            "participant_id",
            "trial_id",
            "trial_order",
            "phase_id",
            "list",
            "list_name",
            "stimulus",
            "condition",
            "response",
            "accuracy",
        ]
    ]
    return df

def main():
    study, recog = load_raw()

    study_df = build_study_trials(study, recog)
    n_study_trials = study_df.groupby("participant_id").size()
    recog_df = build_recognition_trials(recog, n_study_trials)

    out = pd.concat([study_df, recog_df], ignore_index=True)
    out = out.sort_values(["participant_id", "trial_order"]).reset_index(drop=True)

    out.to_csv(OUT_DIR / "exp1.csv", index=False)

    print("Wrote:", OUT_DIR / "exp1.csv")
    print("Shape:", out.shape)

    print("\nLIST CHECK:")
    print(sorted(out["list"].dropna().unique()))

    print("\nFIRST 20 ROWS:")
    print(out.head(20).to_string(index=False))

if __name__ == "__main__":
    main()
