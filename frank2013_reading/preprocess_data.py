import numpy as np
import pandas as pd
from pathlib import Path


def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


def load_stimuli(base_dir: Path) -> pd.DataFrame:
    path = base_dir / "original_data" / "stimuli.txt"
    stimuli = pd.read_csv(path, sep="\t", dtype=str, encoding="latin-1")
    stimuli["sent_nr"] = stimuli["sent_nr"].astype(int)
    stimuli["sentence"] = stimuli["sentence"].str.strip()
    stimuli["question"] = stimuli["question"].str.strip().replace("-", np.nan)
    stimuli["answer"] = stimuli["answer"].str.strip().replace("-", np.nan)
    return stimuli


def code_accuracy(correct_series: pd.Series) -> pd.Series:
    return correct_series.map({"c": 1.0, "e": 0.0, "-": np.nan})


def infer_participant_response(answer_series: pd.Series, correct_series: pd.Series) -> pd.Series:
    """Infer participant's actual button press from the correct answer and trial accuracy."""
    is_correct = correct_series == "c"
    is_error = correct_series == "e"
    answered_y = answer_series == "y"
    answered_n = answer_series == "n"

    response = pd.Series(np.nan, index=answer_series.index, dtype=object)
    response[is_correct & answered_y] = "y"
    response[is_correct & answered_n] = "n"
    response[is_error & answered_y] = "n"  # participant said opposite of correct
    response[is_error & answered_n] = "y"
    return response


def code_gender(sex_series: pd.Series) -> pd.Series:
    return sex_series.map({"f": "female", "m": "male"})


def code_first_language(age_en_series: pd.Series) -> pd.Series:
    return age_en_series.apply(lambda x: "English" if x == 0 else np.nan)


# spr = self-paced reading
def preprocess_spr(base_dir: Path, processed_dir: Path, stimuli: pd.DataFrame) -> None:
    subj = pd.read_csv(base_dir / "original_data" / "selfpacedreading.subj.txt", sep="\t")
    rt = pd.read_csv(base_dir / "original_data" / "selfpacedreading.RT.txt", sep="\t")

    df = rt.merge(subj, on="subj_nr", how="left", suffixes=("_rt", "_subj"))
    df = df.merge(stimuli[["sent_nr", "sentence", "question", "answer"]], on="sent_nr", how="left")

    df["participant_id"] = df["subj_nr"].astype(int)
    df["age"] = df["age"].astype(float)
    df["gender"] = code_gender(df["sex"])
    df["first_language"] = code_first_language(df["age_en"])
    df["trial_id"] = df["sent_nr"].astype(int)
    df["trial_order"] = df["sent_pos"].astype(int)
    df["stimulus"] = df["sentence"]
    df["word"] = df["word"]
    df["word_position"] = df["word_pos"].astype(int)
    df["question"] = df["question"]
    df["response"] = infer_participant_response(df["answer"], df["correct_rt"])
    df["rt"] = df["RT"].astype(float)
    df["accuracy"] = code_accuracy(df["correct_rt"])

    cols = [
        "participant_id", "age", "gender", "first_language",
        "trial_id", "trial_order", "stimulus", "word", "word_position",
        "question", "response", "rt", "accuracy",
    ]
    df_out = df[cols].copy()
    df_out = df_out.sort_values(["participant_id", "trial_order", "word_position"])

    df_out.to_csv(processed_dir / "exp1.csv", index=False)
    print(f"exp1.csv: {len(df_out)} rows, {df_out['participant_id'].nunique()} participants")

# et = eye-tracking
def preprocess_et(base_dir: Path, processed_dir: Path, stimuli: pd.DataFrame) -> None:
    subj = pd.read_csv(base_dir / "original_data" / "eyetracking.subj.txt", sep="\t")
    rt = pd.read_csv(base_dir / "original_data" / "eyetracking.RT.txt", sep="\t")

    df = rt.merge(subj, on="subj_nr", how="left", suffixes=("_rt", "_subj"))
    df = df.merge(stimuli[["sent_nr", "sentence", "question", "answer"]], on="sent_nr", how="left")

    df["participant_id"] = df["subj_nr"].astype(int)
    df["age"] = df["age"].astype(float)
    df["gender"] = code_gender(df["sex"])
    df["first_language"] = code_first_language(df["age_en"])
    df["monolingual"] = df["monoling"].astype(int)
    df["trial_id"] = df["sent_nr"].astype(int)
    df["trial_order"] = df["sent_pos"].astype(int)
    df["stimulus"] = df["sentence"]
    df["word"] = df["word"]
    df["word_position"] = df["word_pos"].astype(int)
    df["question"] = df["question"]
    df["response"] = infer_participant_response(df["answer"], df["correct_rt"])
    df["accuracy"] = code_accuracy(df["correct_rt"])

    # 0 means word was not fixated → NaN
    for col_raw, col_out in [
        ("RTfirstfix", "rt"),
        ("RTfirstpass", "first_pass_duration"),
        ("RTrightbound", "right_bounded_duration"),
        ("RTgopast", "go_past_duration"),
    ]:
        df[col_out] = df[col_raw].astype(float).replace(0.0, np.nan)

    cols = [
        "participant_id", "age", "gender", "first_language", "monolingual",
        "trial_id", "trial_order", "stimulus", "word", "word_position",
        "question", "response", "rt", "first_pass_duration", "right_bounded_duration",
        "go_past_duration", "accuracy",
    ]
    df_out = df[cols].copy()
    df_out = df_out.sort_values(["participant_id", "trial_order", "word_position"])

    df_out.to_csv(processed_dir / "exp2.csv", index=False)
    print(f"exp2.csv: {len(df_out)} rows, {df_out['participant_id'].nunique()} participants")


def preprocess(base_dir: Path) -> None:
    processed_dir = ensure_processed_dir(base_dir)
    stimuli = load_stimuli(base_dir)
    preprocess_spr(base_dir, processed_dir, stimuli)
    preprocess_et(base_dir, processed_dir, stimuli)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())
