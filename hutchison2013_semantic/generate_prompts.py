import random
import string
import zipfile
from pathlib import Path

import jsonlines
import numpy as np
import pandas as pd


MAX_CHARS = 50_000 # To limit the size of the prompts

LDT_INSTRUCTION = (
    "In this experiment, you will see pairs of letter strings. "
    "First, a cue will briefly appear on the screen. "
    "Then, a target will appear. "
    "Your task is to decide as quickly and accurately as possible "
    "whether the target is a real English word or not. "
    "Press '{yes_key}' if the target IS a real word (YES). "
    "Press '{no_key}' if the target is NOT a real word (NO). "
    "Reaction times are recorded.\n\n"
)

NAMING_INSTRUCTION = (
    "In this experiment, you will see pairs of letter strings. "
    "First, a cue will briefly appear on the screen. "
    "Then, a target will appear. "
    "Your task is to name the target word aloud as quickly and accurately as possible. "
    "Reaction times are recorded.\n\n"
)


def random_letters(n: int) -> str:
    return "".join(random.sample(string.ascii_lowercase, n))


def generate_ldt_prompts(base_dir: Path) -> list:
    df = pd.read_csv(base_dir / "processed_data" / "exp1.csv")
    df = df.sort_values(["participant_id", "trial_id"])

    participants = sorted(df["participant_id"].unique())
    id_map = {p: i + 1 for i, p in enumerate(participants)}
    df["participant_id"] = df["participant_id"].map(id_map)

    all_prompts = []
    for new_id, orig_id in enumerate(participants, start=1):
        df_p = df[df["participant_id"] == new_id].copy()

        age_val = df_p["age"].iloc[0]
        gender_val = df_p["gender"].iloc[0]

        # Randomly assign keys per participant
        yes_key, no_key = random.sample(string.ascii_lowercase, 2)

        instruction = LDT_INSTRUCTION.format(yes_key=yes_key, no_key=no_key)

        resp_series = df_p["response"].map({"word": yes_key, "nonword": no_key}).fillna("no response")
        rt_str = df_p["rt"].apply(lambda x: str(int(round(x))) if pd.notna(x) else "not recorded")

        lines = (
            "Trial " + df_p["trial_id"].astype(int).astype(str)
            + ": Cue: '" + df_p["prime"].str.upper()
            + "' → Target: '" + df_p["stimulus"]
            + "'. You press <<" + resp_series + ">>. RT: <<" + rt_str + ">> ms."
        ).tolist()

        prompt = instruction + "\n".join(lines) + "\n"

        # Truncate to MAX_CHARS if needed (e.g., anomalous participants with double trials)
        if len(prompt) > MAX_CHARS:
            cut = prompt[:MAX_CHARS].rfind("\n")
            prompt = prompt[:cut + 1]
            n_included = prompt.count("Trial ")
            rt_list = df_p.loc[df_p["rt"].notna()].head(n_included)["rt"].tolist()
        else:
            rt_list = df_p.loc[df_p["rt"].notna(), "rt"].tolist()

        entry = {
            "text": prompt,
            "experiment": "hutchison2013_semantic/lexical_decision",
            "participant_id": new_id,
            "rt": rt_list,
        }
        if pd.notna(age_val):
            entry["age"] = float(age_val)
        if pd.notna(gender_val):
            entry["gender"] = str(gender_val)
        edu_val = df_p["education"].iloc[0]
        if pd.notna(edu_val):
            entry["education"] = float(edu_val)
        school_val = df_p["school"].iloc[0]
        if pd.notna(school_val):
            entry["school"] = str(school_val)

        all_prompts.append(entry)

    return all_prompts


def generate_naming_prompts(base_dir: Path) -> list:
    df = pd.read_csv(base_dir / "processed_data" / "exp2.csv")
    df = df.sort_values(["participant_id", "trial_id"])

    participants = sorted(df["participant_id"].unique())
    id_map = {p: i + 1 for i, p in enumerate(participants)}
    df["participant_id"] = df["participant_id"].map(id_map)

    all_prompts = []
    for new_id, orig_id in enumerate(participants, start=1):
        df_p = df[df["participant_id"] == new_id].copy()

        age_val = df_p["age"].iloc[0]
        gender_val = df_p["gender"].iloc[0]

        rt_str = df_p["rt"].apply(
            lambda x: str(int(round(x))) if pd.notna(x) else "not recorded"
        )
        lines = (
            "Trial " + df_p["trial_id"].astype(int).astype(str)
            + ": Cue: '" + df_p["prime"].str.upper()
            + "' → Target: '" + df_p["stimulus"]
            + "'. Naming time: <<" + rt_str + ">> ms."
        ).tolist()

        prompt = NAMING_INSTRUCTION + "\n".join(lines) + "\n"

        # Truncate to MAX_CHARS if needed
        if len(prompt) > MAX_CHARS:
            cut = prompt[:MAX_CHARS].rfind("\n")
            prompt = prompt[:cut + 1]
            n_included = prompt.count("Trial ")
            rt_list = df_p.loc[df_p["rt"].notna()].head(n_included)["rt"].tolist()
        else:
            rt_list = df_p.loc[df_p["rt"].notna(), "rt"].tolist()

        entry = {
            "text": prompt,
            "experiment": "hutchison2013_semantic/speeded_naming",
            "participant_id": new_id,
            "rt": rt_list,
        }
        if pd.notna(age_val):
            entry["age"] = float(age_val)
        if pd.notna(gender_val):
            entry["gender"] = str(gender_val)
        edu_val = df_p["education"].iloc[0]
        if pd.notna(edu_val):
            entry["education"] = float(edu_val)
        school_val = df_p["school"].iloc[0]
        if pd.notna(school_val):
            entry["school"] = str(school_val)

        all_prompts.append(entry)

    return all_prompts


if __name__ == "__main__":
    base_dir = Path(__file__).parent.resolve()

    print("Generating LDT prompts...")
    ldt_prompts = generate_ldt_prompts(base_dir)
    print("Generating naming prompts...")
    naming_prompts = generate_naming_prompts(base_dir)
    all_prompts = ldt_prompts + naming_prompts

    jsonl_path = base_dir / "prompts.jsonl"
    with jsonlines.open(jsonl_path, "w") as writer:
        writer.write_all(all_prompts)

    zip_path = base_dir / "prompts.jsonl.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(jsonl_path, "prompts.jsonl")

    jsonl_path.unlink()

    print(f"Done. {len(all_prompts)} prompts ({len(ldt_prompts)} LDT + {len(naming_prompts)} naming).")
