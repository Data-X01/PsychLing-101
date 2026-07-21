from pathlib import Path
import pandas as pd

DATASET_DIR = Path("gatti2024_concreteness_judgments")
RAW_EXP1 = DATASET_DIR / "original_data" / "data_EXP1_fin.csv"
RAW_EXP2 = DATASET_DIR / "original_data" / "data_EXP2_full.csv"
OUT_DIR = DATASET_DIR / "processed_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_gender_exp1(x):
    x = str(x).strip().upper()
    if x == "F":
        return "F"
    if x == "M":
        return "M"
    return x


def normalize_hand_exp1(x):
    x = str(x).strip().lower()
    if x in {"dx", "destra"}:
        return "right"
    return x


def normalize_gender_exp2(x):
    x = str(x).strip().lower()
    if x in {"f", "femmina", "femminile", "donna"}:
        return "F"
    if x in {"m", "maschio", "uomo"}:
        return "M"
    return x.upper()


def normalize_device_exp2(x):
    x = str(x).strip().lower()
    if "mouse" in x:
        return "mouse"
    if "trackpad" in x:
        return "trackpad"
    return x


def build_exp1():
    df = pd.read_csv(RAW_EXP1, sep=";")

    df["rt"] = pd.to_numeric(
        df["RTs"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

    df = df.rename(columns={
        "ID": "participant_id",
        "text": "stimulus_left",
        "text2": "stimulus_right",
        "resp": "response",
        "condition": "condition_raw",
        "age": "age",
        "gender": "gender",
        "hand": "hand",
    })

    df["gender"] = df["gender"].apply(normalize_gender_exp1)
    df["hand"] = df["hand"].apply(normalize_hand_exp1)

    # trial order reconstructed from file order within participant
    df["trial_order"] = df.groupby("participant_id").cumcount()
    df["trial_id"] = "exp1_t" + df["trial_order"].astype(str)
    df["experiment"] = "EXP1"
    df["phase_id"] = "judgment"

    # chosen side
    df["response_side"] = pd.NA
    df.loc[df["response"] == df["stimulus_left"], "response_side"] = "left"
    df.loc[df["response"] == df["stimulus_right"], "response_side"] = "right"

    out = df[[
        "experiment",
        "participant_id",
        "trial_id",
        "trial_order",
        "phase_id",
        "stimulus_left",
        "stimulus_right",
        "response",
        "response_side",
        "condition_raw",
        "rt",
        "age",
        "gender",
        "hand",
    ]].copy()

    return out


def build_exp2():
    df = pd.read_csv(RAW_EXP2, sep=";")

    df = df.rename(columns={
        "ID": "participant_id",
        "text": "stimulus_left",
        "text2": "stimulus_right",
        "resp": "response",
        "condition": "condition_raw",
        "age": "age",
        "gender": "gender",
        "type": "device",
    })

    df["gender"] = df["gender"].apply(normalize_gender_exp2)
    df["device"] = df["device"].apply(normalize_device_exp2)
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    df["trial_order"] = df.groupby("participant_id").cumcount()
    df["trial_id"] = "exp2_t" + df["trial_order"].astype(str)
    df["experiment"] = "EXP2"
    df["phase_id"] = "judgment"

    df["response_side"] = pd.NA
    df.loc[df["response"] == df["stimulus_left"], "response_side"] = "left"
    df.loc[df["response"] == df["stimulus_right"], "response_side"] = "right"

    out = df[[
        "experiment",
        "participant_id",
        "trial_id",
        "trial_order",
        "phase_id",
        "stimulus_left",
        "stimulus_right",
        "response",
        "response_side",
        "condition_raw",
        "device",
        "age",
        "gender",
    ]].copy()

    return out


def main():
    exp1 = build_exp1()
    exp2 = build_exp2()

    exp1.to_csv(OUT_DIR / "exp1.csv", index=False)
    exp2.to_csv(OUT_DIR / "exp2.csv", index=False)

    print("Wrote:", OUT_DIR / "exp1.csv", exp1.shape)
    print("Wrote:", OUT_DIR / "exp2.csv", exp2.shape)

    print("\nEXP1 PREVIEW:")
    print(exp1.head(10).to_string(index=False))

    print("\nEXP2 PREVIEW:")
    print(exp2.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
