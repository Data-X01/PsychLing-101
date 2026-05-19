#!/usr/bin/env python3
"""
preprocess_data.py — jap2026_indonesian_verb_bias_erp
------------------------------------------------------
Save this file in: D:\Verb bias data\ERP_output\
Output will be written to: D:\Verb bias data\ERP_output\processed_data\exp1.csv
"""

import os
import glob
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # same folder as this script
IN_GLOB  = os.path.join(BASE_DIR, "E*_erp_amplitudes*.csv")
OUT_DIR  = os.path.join(BASE_DIR, "processed_data")
OUT_FILE = os.path.join(OUT_DIR, "exp1.csv")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load all participant files ─────────────────────────────────────────────────
files = sorted(glob.glob(IN_GLOB))
if not files:
    raise FileNotFoundError(f"No CSV files found in: {BASE_DIR}")

print(f"Found {len(files)} participant file(s):")
chunks = []
for fp in files:
    chunk = pd.read_csv(fp)
    chunks.append(chunk)
    print(f"  {os.path.basename(fp):40s}  →  {len(chunk):5,} rows")

df = pd.concat(chunks, ignore_index=True)
print(f"\nTotal rows  : {len(df):,}")
print(f"Participants: {df['participant_id'].nunique()}")

# ── Metadata columns ───────────────────────────────────────────────────────────
df["study"]       = "jap2026_indonesian_verb_bias_erp"
df["language"]    = "Indonesian"
df["paradigm"]    = "ERP"
df["word_length"] = df["word"].astype(str).str.len()

subj_num   = df["participant_id"].str.extract(r"E(\d+)")[0].astype(int)
df["list"] = subj_num.apply(lambda n: 1 if n <= 22 else 2)

# ── Sentence reconstruction ────────────────────────────────────────────────────
# Filter for non-Filler BEFORE grouping. Filler rows share the same trial number
# as experimental rows but have position_num=0, which would corrupt word order.
print("\nReconstructing sentence texts (experimental trials only)...")

exp_df  = df[df["condition"] != "Filler"].copy()
fill_df = df[df["condition"] == "Filler"].copy()

def reconstruct(group):
    return " ".join(
        group.sort_values("position_num")["word"].astype(str).tolist()
    )

sent_map = (
    exp_df
    .groupby(["participant_id", "trial"])
    .apply(reconstruct)
    .reset_index(name="sentence_text")
)
exp_df = exp_df.merge(sent_map, on=["participant_id", "trial"], how="left")

unique_sents = sorted(exp_df["sentence_text"].dropna().unique())
sent_id_map  = {s: i + 1 for i, s in enumerate(unique_sents)}
exp_df["sentence_id"] = exp_df["sentence_text"].map(sent_id_map)

print(f"  Unique experimental sentences: {len(unique_sents)}")

fill_df["sentence_text"] = ""
fill_df["sentence_id"]   = pd.NA

df_out = pd.concat([exp_df, fill_df], ignore_index=True)

# ── Column order (CODEBOOK-aligned) ───────────────────────────────────────────
col_order = [
    "study", "language", "paradigm", "list",
    "participant_id", "trial", "sentence_id", "sentence_text",
    "token_id", "word", "original_code",
    "condition", "word_position", "position_num",
    "word_length", "eprime_onset_ms", "is_erp_target",
    "N400_mean_uV", "P600_mean_uV",
    "N400_peak_uV", "P600_peak_uV",
    "N400_peak_lat_ms", "P600_peak_lat_ms",
    "peak_uV",
]
existing = [c for c in col_order if c in df_out.columns]
df_out = (
    df_out[existing]
    .sort_values(["participant_id", "trial", "token_id"])
    .reset_index(drop=True)
)

# ── Write ──────────────────────────────────────────────────────────────────────
df_out.to_csv(OUT_FILE, index=False)

print(f"\n✓ Wrote: {OUT_FILE}")
print(f"  Rows             : {len(df_out):,}")
print(f"  Participants     : {df_out['participant_id'].nunique()}")
print(f"  Conditions       : {sorted(df_out['condition'].dropna().unique())}")
print(f"  Unique sentences : {df_out['sentence_id'].nunique()}")
print(f"  List 1 subjects  : {df_out.loc[df_out['list']==1, 'participant_id'].nunique()}")
print(f"  List 2 subjects  : {df_out.loc[df_out['list']==2, 'participant_id'].nunique()}")