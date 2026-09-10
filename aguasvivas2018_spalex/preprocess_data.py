import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "spalex lexical decision.csv"
PROCESSED_DATA = ROOT / "processed_data"
PROCESSED_DATA.mkdir(exist_ok=True)
EXP1_FILE = PROCESSED_DATA / "exp1.csv"

df = pd.read_csv(DATA_FILE, encoding="utf-8")

df = df.rename(columns={
    "exp_id": "participant_id",
    "trial_order": "trial_order",
    "spelling": "stimulus",
    "lexicality": "condition",
    "accuracy": "accuracy"
})

df["condition"] = df["condition"].map({"W": "word", "NW": "nonword"})

df = df[["participant_id", "trial_order", "stimulus", "condition", "rt", "accuracy"]].copy()

df["participant_id"] = pd.to_numeric(df["participant_id"], errors="coerce")
df["trial_order"]    = pd.to_numeric(df["trial_order"],    errors="coerce")
df["rt"]             = pd.to_numeric(df["rt"],             errors="coerce")
df["accuracy"]       = pd.to_numeric(df["accuracy"],       errors="coerce")
df["stimulus"]       = df["stimulus"].astype(str).str.strip()

df = df.dropna(subset=["participant_id", "trial_order", "stimulus", "condition", "rt", "accuracy"]).copy()

df["participant_id"] = df["participant_id"].astype(int)
df["trial_order"]    = df["trial_order"].astype(int)
df["accuracy"]       = df["accuracy"].astype(int)

df = df.sort_values(["participant_id", "trial_order"]).reset_index(drop=True)

df.to_csv(EXP1_FILE, index=False, encoding="utf-8")
print(f"Done. Saved {len(df):,} rows to {EXP1_FILE}")
