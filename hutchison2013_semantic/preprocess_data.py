import numpy as np
import pandas as pd
from pathlib import Path


def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


def write_codebook(base_dir: Path) -> None:
    codebook_path = base_dir / "CODEBOOK.csv"
    if codebook_path.exists():
        return
    rows = [
        {"column_name": "participant_id", "description": "Anonymized participant ID"},
        {"column_name": "age", "description": "Participant age in years"},
        {"column_name": "gender", "description": "Participant gender (male/female)"},
        {"column_name": "education", "description": "Years of education"},
        {"column_name": "vision", "description": "Self-reported vision quality (1=excellent 20/20 or better, 7=poor 20/50)"},
        {"column_name": "school", "description": "University at which the participant was tested (msu/washu/suny/omaha)"},
        {"column_name": "ospan", "description": "Operation span score: sum of letters recalled in correct order (0-75)"},
        {"column_name": "saccade", "description": "Antisaccade task accuracy (proportion correct)"},
        {"column_name": "stroop", "description": "Stroop interference RT: mean RT in incongruent minus congruent condition (ms)"},
        {"column_name": "stroop_err", "description": "Stroop interference error rate: error rate in incongruent minus congruent condition"},
        {"column_name": "ac", "description": "Attentional control composite score (PCA of ospan, saccade, stroop)"},
        {"column_name": "passage", "description": "Woodcock-Johnson III passage comprehension score"},
        {"column_name": "vocaba", "description": "Woodcock-Johnson III synonym test score"},
        {"column_name": "vocabb", "description": "Woodcock-Johnson III antonym test score"},
        {"column_name": "vocabc", "description": "Woodcock-Johnson III analogy test score"},
        {"column_name": "meq", "description": "Morningness-Eveningness Questionnaire (MEQ) score (16-86; higher = more morning-type)"},
        {"column_name": "session", "description": "Session number (1 or 2)"},
        {"column_name": "trial_id", "description": "Trial order index within participant (1-indexed, sorted by Session, Block, Trial)"},
        {"column_name": "prime", "description": "Prime word presented before the target (lowercase)"},
        {"column_name": "prime_type", "description": "Type of prime: first_associate (most common association from Nelson norms) or other_associate (2nd-Nth association)"},
        {"column_name": "soa", "description": "Stimulus onset asynchrony in ms (200 = short/automatic, 1200 = long/intentional)"},
        {"column_name": "relatedness", "description": "Semantic relatedness of prime-target pair: related or unrelated"},
        {"column_name": "stimulus", "description": "Target word or nonword presented to the participant"},
        {"column_name": "lexicality", "description": "Whether the target is a real word or a nonword (exp1/LDT only)"},
        {"column_name": "response", "description": "Participant response: 'word' or 'nonword' for LDT (exp1); 'correct', 'unsure', 'mispronunciation', or 'extraneous' for naming (exp2)"},
        {"column_name": "rt", "description": "Response time in ms"},
        {"column_name": "accuracy", "description": "Response accuracy (1.0 = correct, 0.0 = incorrect)"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess_ldt(base_dir: Path, processed_dir: Path) -> None:
    ldt_cols = [
        "Subject", "Session", "Block", "Trial",
        "isi", "lexicality", "prime", "target",
        "type", "rel", "target.ACC", "target.RT",
    ]
    df = pd.read_excel(
        base_dir / "original_data" / "all ldt subs_all trials3.xlsx",
        usecols=ldt_cols,
        engine="openpyxl",
    )

    subj = pd.read_excel(
        base_dir / "original_data" / "LDT subject database.xlsx",
        engine="openpyxl",
    ).rename(columns={
        "SUBJECT": "Subject",
        "stroop": "stroop",
        "stroop_err": "stroop_err",
        "meq": "meq",
        "education": "education",
        "vision": "vision",
        "school": "school",
    })

    df = df.merge(subj, on="Subject", how="left")

    # Drop rows with no target (buffer/practice trials not in the main stimulus set)
    df = df.dropna(subset=["target"])

    df["age"] = pd.to_numeric(df["age"], errors="coerce").astype(float)
    # Normalize mixed-case and combined codes (e.g. 'wf' = white female → female)
    df["gender"] = df["gender"].astype(str).str.lower().str.strip().map(
        {"m": "male", "f": "female", "wf": "female", "nan": None}
    )
    df["education"] = pd.to_numeric(df["education"], errors="coerce").astype(float)
    df["vision"] = pd.to_numeric(df["vision"], errors="coerce").astype(float)
    for col in ["ospan", "saccade", "stroop", "stroop_err", "ac", "passage",
                "vocaba", "vocabb", "vocabc", "meq"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    df["soa"] = df["isi"].map({50: 200, 1050: 1200})
    df["prime"] = df["prime"].astype(str).str.lower()
    df["stimulus"] = df["target"].astype(str).str.lower()
    df["lexicality"] = df["lexicality"].map({1: "word", 2: "nonword"})
    df["prime_type"] = df["type"].map({"first": "first_associate", "other": "other_associate"})
    df["relatedness"] = df["rel"].map({"rel": "related", "un": "unrelated"})

    # #NULL! strings in target.RT become NaN via errors="coerce"
    df["rt"] = pd.to_numeric(df["target.RT"], errors="coerce").astype(float)
    df["accuracy"] = pd.to_numeric(df["target.ACC"], errors="coerce").astype(float)

    # Infer response from lexicality + accuracy
    df["response"] = pd.Series(np.nan, index=df.index, dtype=object)
    word_correct = (df["lexicality"] == "word") & (df["accuracy"] == 1.0)
    word_incorrect = (df["lexicality"] == "word") & (df["accuracy"] == 0.0)
    nw_correct = (df["lexicality"] == "nonword") & (df["accuracy"] == 1.0)
    nw_incorrect = (df["lexicality"] == "nonword") & (df["accuracy"] == 0.0)
    df.loc[word_correct | nw_incorrect, "response"] = "word"
    df.loc[word_incorrect | nw_correct, "response"] = "nonword"

    # trial_id: sequential within participant, sorted by session > block > trial
    df = df.sort_values(["Subject", "Session", "Block", "Trial"])
    df["trial_id"] = df.groupby("Subject").cumcount() + 1

    df = df.rename(columns={"Subject": "participant_id", "Session": "session"})

    out_cols = [
        "participant_id", "age", "gender", "education", "vision", "school",
        "ospan", "saccade", "stroop", "stroop_err", "ac",
        "passage", "vocaba", "vocabb", "vocabc", "meq",
        "session", "trial_id",
        "prime", "prime_type", "soa", "relatedness",
        "stimulus", "lexicality", "response", "rt", "accuracy",
    ]
    df[out_cols].sort_values(["participant_id", "trial_id"]).to_csv(
        processed_dir / "exp1.csv", index=False
    )


def preprocess_naming(base_dir: Path, processed_dir: Path) -> None:
    naming_cols = [
        "Subject", "Session", "Trial",
        "isi", "primecond", "prime", "target",
        "coding.RESP", "target.RT", "target.ACC", "micerror",
        "age.RESP", "Gender.RESP", "EducationLevel.RESP", "Vision.RESP",
    ]
    df = pd.read_excel(
        base_dir / "original_data" / "all naming subjects.xlsx",
        usecols=naming_cols,
        engine="openpyxl",
    )

    # Drop rows with no prime or target (buffer/rest-break markers in the data)
    df = df.dropna(subset=["prime", "target"])

    # Demographics are embedded only in Session 1; propagate to all sessions per subject
    df = df.sort_values(["Subject", "Session", "Trial"])
    for src, dst in [("age.RESP", "age"), ("Gender.RESP", "_gender_raw"),
                     ("EducationLevel.RESP", "education"), ("Vision.RESP", "vision")]:
        per_subj = df.groupby("Subject")[src].first()
        df[dst] = df["Subject"].map(per_subj)

    df["age"] = pd.to_numeric(df["age"], errors="coerce").astype(float)
    df["gender"] = df["_gender_raw"].map({"m": "male", "f": "female"})
    df["education"] = pd.to_numeric(df["education"], errors="coerce").astype(float)
    df["vision"] = pd.to_numeric(df["vision"], errors="coerce").astype(float)

    # Merge cognitive/individual-difference measures from naming subject spreadsheet
    nam_subj = pd.read_excel(
        base_dir / "original_data" / "naming subject-based spreadsheet.xlsx",
        engine="openpyxl",
    ).rename(columns={
        "subject": "Subject",
        "university": "school",
        "str": "stroop",
        "str_err": "stroop_err",
        "MEQ": "meq",
    })
    for col in ["ospan", "saccade", "stroop", "stroop_err", "ac",
                "passage", "vocaba", "vocabb", "vocabc", "meq"]:
        nam_subj[col] = pd.to_numeric(nam_subj[col], errors="coerce").astype(float)

    df = df.merge(nam_subj[["Subject", "school", "ospan", "saccade", "stroop",
                             "stroop_err", "ac", "passage", "vocaba", "vocabb",
                             "vocabc", "meq"]], on="Subject", how="left")

    isi_num = pd.to_numeric(df["isi"], errors="coerce")
    df["soa"] = isi_num.map({50.0: 200, 1050.0: 1200})

    df["prime"] = df["prime"].astype(str).str.lower()
    df["stimulus"] = df["target"].astype(str).str.lower()

    # primecond: 1=first_related, 2=other_related, 3=first_unrelated, 4=other_unrelated
    primecond = pd.to_numeric(df["primecond"], errors="coerce")
    df["prime_type"] = primecond.map(
        {1.0: "first_associate", 2.0: "other_associate",
         3.0: "first_associate", 4.0: "other_associate"}
    )
    df["relatedness"] = primecond.map(
        {1.0: "related", 2.0: "related", 3.0: "unrelated", 4.0: "unrelated"}
    )

    df["rt"] = pd.to_numeric(df["target.RT"], errors="coerce").astype(float)
    df.loc[df["micerror"] == 1.0, "rt"] = np.nan

    df["accuracy"] = pd.to_numeric(df["target.ACC"], errors="coerce").astype(float)

    coding_map = {1.0: "correct", 2.0: "unsure", 3.0: "mispronunciation", 4.0: "extraneous"}
    df["response"] = pd.to_numeric(df["coding.RESP"], errors="coerce").map(coding_map)

    df["trial_id"] = df.groupby("Subject").cumcount() + 1
    df = df.rename(columns={"Subject": "participant_id", "Session": "session"})

    out_cols = [
        "participant_id", "age", "gender", "education", "vision", "school",
        "ospan", "saccade", "stroop", "stroop_err", "ac",
        "passage", "vocaba", "vocabb", "vocabc", "meq",
        "session", "trial_id",
        "prime", "prime_type", "soa", "relatedness",
        "stimulus", "response", "rt", "accuracy",
    ]
    df[out_cols].sort_values(["participant_id", "trial_id"]).to_csv(
        processed_dir / "exp2.csv", index=False
    )


def preprocess(base_dir: Path) -> None:
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)
    print("Processing LDT data...")
    preprocess_ldt(base_dir, processed_dir)
    print("Processing Naming data...")
    preprocess_naming(base_dir, processed_dir)
    print("Done.")


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())
