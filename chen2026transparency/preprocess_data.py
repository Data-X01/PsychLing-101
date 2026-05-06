"""
Preprocessing script for Chen et al. (2026) Semantic Transparency Ratings

Reads long-format CSVs from original_data/ (one row per participant × stimulus) and outputs:
  - original_data/item-set.csv    unique stimulus catalogue
  - processed_data/exp1.csv       cleaned long-format ratings
"""

import re
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
ORIG_DIR = BASE / "original_data"
PROC_DIR = BASE / "processed_data"
PROC_DIR.mkdir(exist_ok=True)

CONSTITUENT_RE = re.compile(r'["\u201c]\s*(.+?)\s*["\u201d]')


def list_id_from_name(stem: str) -> int:
    return int(stem.rsplit("_", 1)[-1])


def extract_constituent(query: str) -> str:
    """Extract the constituent word from a question like '"船"对这个词…'"""
    if pd.isna(query):
        return ""
    m = CONSTITUENT_RE.search(str(query))
    return m.group(1).strip() if m else ""


# ── Step 1: load all list CSVs ────────────────────────────────────────────────
print("Loading list CSVs …")
frames = []
for fn in sorted(ORIG_DIR.glob("list_*.csv"), key=lambda p: list_id_from_name(p.stem)):
    lid = list_id_from_name(fn.stem)
    df = pd.read_csv(fn, encoding="utf-8-sig")
    df["list"] = lid

    # trial_order: 0-indexed position of each stimulus within the list,
    # determined from the first participant (order is fixed across participants)
    first_pid = df["participant_id"].iloc[0]
    stim_order = {s: i for i, s in enumerate(df[df["participant_id"] == first_pid]["stimulus"])}
    df["trial_order"] = df["stimulus"].map(stim_order)

    frames.append(df)

all_data = pd.concat(frames, ignore_index=True)
print(f"  → {len(all_data)} rows across {all_data['list'].nunique()} lists")

# ── Step 2: extract constituents from query columns ───────────────────────────
all_data["constituent_1"] = all_data["query_c1"].apply(extract_constituent)
all_data["constituent_2"] = all_data["query_c2"].apply(extract_constituent)

# ── Step 3: build item-set.csv ────────────────────────────────────────────────
item_set = (
    all_data[["stimulus", "constituent_1", "constituent_2", "list"]]
    .drop_duplicates(subset="stimulus", keep="first")
    .rename(columns={"list": "list_id"})
    .sort_values(["list_id", "stimulus"])
    .reset_index(drop=True)
)
item_set.to_csv(ORIG_DIR / "item-set.csv", index=False, encoding="utf-8-sig")
print(f"item-set.csv: {len(item_set)} unique stimuli")

# ── Step 6: build exp1.csv ────────────────────────────────────────────────────
exp1 = all_data.rename(columns={
    "c1_contribution": "constituent_1_contribution",
    "c2_contribution": "constituent_2_contribution",
    "comp": "predictability",
})

# Drop rows with missing ratings and warn
n_before = len(exp1)
exp1 = exp1.dropna(subset=["constituent_1_contribution", "constituent_2_contribution", "predictability"])
n_dropped = n_before - len(exp1)
if n_dropped:
    print(f"\n⚠ Dropped {n_dropped} rows with missing ratings")

# Cast ratings to integer
for col in ["constituent_1_contribution", "constituent_2_contribution", "predictability"]:
    exp1[col] = exp1[col].astype(int)

exp1 = exp1[[
    "participant_id",
    "stimulus", "constituent_1", "constituent_2",
    "constituent_1_contribution", "constituent_2_contribution", "predictability",
]].sort_values(["participant_id", "stimulus"]).reset_index(drop=True)

# trial_id: 1-indexed sequential number for each row (one participant × stimulus observation)
exp1.insert(1, "trial_id", range(1, len(exp1) + 1))

exp1.to_csv(PROC_DIR / "exp1.csv", index=False, encoding="utf-8-sig")
print(f"\nexp1.csv: {len(exp1)} rows, {exp1['participant_id'].nunique()} participants, "
      f"{exp1['stimulus'].nunique()} unique stimuli")
print("\nDone.")
