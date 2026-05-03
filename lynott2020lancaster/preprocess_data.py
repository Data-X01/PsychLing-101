"""
Preprocessing script for Lynott et al. (2020) Lancaster Sensorimotor Norms
Reads original_data/sm_norms_trial_level.csv and outputs:
  - processed_data/exp1.csv   Perception norms (one row per participant × word)
  - processed_data/exp2.csv   Action norms    (one row per participant × word)
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
ORIG_DIR = BASE / "original_data"
PROC_DIR = BASE / "processed_data"
PROC_DIR.mkdir(exist_ok=True)

print("Loading data …")
df = pd.read_csv(ORIG_DIR / "sm_norms_trial_level.csv")

# Rename columns to canonical names
df = df.rename(columns={
    "Participant_ID_anonymised": "participant_id",
    "Word":                      "stimulus",
    "Dimension":                 "dimension",
    "Rating":                    "response",
    "Age":                       "age",
    "Sex":                       "gender",
    "Norming_Component":         "norming_component",
})
df = df.drop(columns=["participant_ID", "response_ID", "List", "List_N", "Duration_minutes"])

# Sort, then assign trial_id: 1-based index of each stimulus within participant × component
df = df.sort_values(["participant_id", "norming_component", "stimulus", "dimension"]).reset_index(drop=True)
df["trial_id"] = (
    df.groupby(["participant_id", "norming_component"])["stimulus"]
      .transform(lambda s: s.ne(s.shift()).cumsum())
)

def process(component):
    sub = df[df["norming_component"] == component]
    wide = sub.pivot_table(
        index=["participant_id", "age", "gender", "stimulus", "trial_id"],
        columns="dimension",
        values="response",
        aggfunc="first"
    ).reset_index()
    wide.columns.name = None

    wide["trial_id"] = wide["trial_id"].astype(int)

    if "Dont_know_word" in wide.columns:
        wide = wide.rename(columns={"Dont_know_word": "unknown_word"})
        wide["unknown_word"] = wide["unknown_word"].fillna(0).astype(int)
        cols = [c for c in wide.columns if c != "unknown_word"] + ["unknown_word"]
        wide = wide[cols]

    wide = wide.sort_values(["participant_id", "trial_id"]).reset_index(drop=True)
    return wide

# ── exp1: Perception ──────────────────────────────────────────────────────────
exp1 = process("Perception")
exp1.to_csv(PROC_DIR / "exp1.csv", index=False)
print(f"exp1 (Perception): {len(exp1):,} rows | "
      f"{exp1['participant_id'].nunique():,} participants | "
      f"{exp1['stimulus'].nunique():,} words")

# ── exp2: Action ──────────────────────────────────────────────────────────────
exp2 = process("Action")
exp2.to_csv(PROC_DIR / "exp2.csv", index=False)
print(f"exp2 (Action):     {len(exp2):,} rows | "
      f"{exp2['participant_id'].nunique():,} participants | "
      f"{exp2['stimulus'].nunique():,} words")

print("\nDone.")