import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "spalex lexical decision.csv"
PROCESSED_DATA = ROOT / "processed_data"
PROCESSED_DATA.mkdir(exist_ok=True)
EXP1_FILE = PROCESSED_DATA / "exp1.csv"

df = pd.read_csv(DATA_FILE, encoding="utf-8")

df = df.rename(columns={
    "exp_id": "participant",
    "trial_order": "trial",
    "spelling": "stimulus",
    "lexicality": "condition",
    "accuracy": "correct"
})

df["condition"] = df["condition"].map({"W": "word", "NW": "nonword"})

df = df[["participant", "trial", "stimulus", "condition", "rt", "correct"]].copy()

df["participant"] = pd.to_numeric(df["participant"], errors="coerce")
df["trial"]       = pd.to_numeric(df["trial"],       errors="coerce")
df["rt"]          = pd.to_numeric(df["rt"],           errors="coerce")
df["correct"]     = pd.to_numeric(df["correct"],      errors="coerce")
df["stimulus"]    = df["stimulus"].astype(str).str.strip()

df = df.dropna(subset=["participant", "trial", "stimulus", "condition", "rt", "correct"]).copy()

df["participant"] = df["participant"].astype(int)
df["trial"]       = df["trial"].astype(int)
df["correct"]     = df["correct"].astype(int)

df = df.sort_values(["participant", "trial"]).reset_index(drop=True)

df.to_csv(EXP1_FILE, index=False, encoding="utf-8")
print(f"Done. Saved {len(df):,} rows to {EXP1_FILE}")
