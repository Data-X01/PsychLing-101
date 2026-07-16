#!/usr/bin/env python3
"""
preprocess_data.py -- jap2025_erp
----------------------------------
Main folder   : D:\\PsychLing-101\\jap2025_erp\\
Amplitude files: D:\\PsychLing-101\\jap2025_erp\\original_data\\E*_erp_amplitudes*.csv
Output        : D:\\PsychLing-101\\jap2025_erp\\processed_data\\exp1.csv

List files (place in main folder):
  merged-list-1.txt
  merged-list-2.txt

Comprehension questions are NOT present in the amplitude files
(the question screen shows as a full sentence -- no ERP extracted).
comp_question and comp_answer are attached to the last-word row of
the preceding sentence trial via the E-Prime list lookup.
"""

import os
import glob
import pandas as pd

# -- Paths ---------------------------------------------------------------------
BASE_DIR   = r"D:\PsychLing-101\jap2025_erp"
IN_GLOB    = os.path.join(BASE_DIR, "original_data", "E*_erp_amplitudes*.csv")
OUT_DIR    = os.path.join(BASE_DIR, "processed_data")
OUT_FILE   = os.path.join(OUT_DIR,  "exp1.csv")
LIST1_FILE = os.path.join(BASE_DIR, "merged-list-1.txt")
LIST2_FILE = os.path.join(BASE_DIR, "merged-list-2.txt")
os.makedirs(OUT_DIR, exist_ok=True)

# -- E-Prime list parser -------------------------------------------------------
def parse_eprime_file(path):
    """
    Parse an E-Prime merged list file.
    Returns list of trial dicts: {words, comp_question, comp_answer}.
    comp_question / comp_answer are None for unprobed trials.
    """
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    trials, current_words = [], []
    for line in lines:
        parts    = line.split("\t")
        stim     = parts[0].strip() if parts         else ""
        code_str = parts[1].strip() if len(parts) > 1 else ""
        resp     = parts[2].strip() if len(parts) > 2 else ""
        if stim == "stim" and code_str == "code":
            continue
        if not stim and not code_str:
            continue
        try:
            code = int(code_str)
        except ValueError:
            continue
        if stim == "Siap?" and code == 100:
            if current_words:
                trials.append({"words": list(current_words),
                                "comp_question": None, "comp_answer": None})
            current_words = []
        elif code == 101:
            if trials:
                trials[-1]["comp_question"] = stim
                trials[-1]["comp_answer"]   = resp
        elif code != 100:
            current_words.append(stim)

    if current_words:
        trials.append({"words": list(current_words),
                        "comp_question": None, "comp_answer": None})
    return trials

def build_probe_lookup(path, list_num):
    """
    Return dict keyed by (sentence_text, list_num) for probed trials only.
    Value: {comp_question, comp_answer}
    """
    lookup = {}
    for t in parse_eprime_file(path):
        if t["comp_question"]:
            sentence = " ".join(t["words"])
            lookup[(sentence, list_num)] = {
                "comp_question": t["comp_question"],
                "comp_answer":   t["comp_answer"],
            }
    return lookup

# -- Build probe lookup --------------------------------------------------------
print("Parsing E-Prime list files for comprehension probes...")
probe_lookup = {}
for path, list_num in [(LIST1_FILE, 1), (LIST2_FILE, 2)]:
    if os.path.exists(path):
        d = build_probe_lookup(path, list_num)
        probe_lookup.update(d)
        print(f"  List {list_num}: {len(d)} probed sentences loaded")
    else:
        print(f"  WARNING: {path} not found -- comp columns will be empty for list {list_num}")

# -- Load amplitude files ------------------------------------------------------
files = sorted(glob.glob(IN_GLOB))
if not files:
    raise FileNotFoundError(f"No CSV files found matching: {IN_GLOB}")

print(f"\nFound {len(files)} participant file(s) in original_data/:")
chunks = []
for fp in files:
    chunk = pd.read_csv(fp)
    chunks.append(chunk)
    print(f"  {os.path.basename(fp):40s} -> {len(chunk):5,} rows")

df = pd.concat(chunks, ignore_index=True)
print(f"\nTotal rows  : {len(df):,}")
print(f"Participants: {df['participant_id'].nunique()}")

# -- Metadata columns ----------------------------------------------------------
df["study"]       = "jap2025_erp"
df["language"]    = "Indonesian"
df["paradigm"]    = "ERP"
df["word_length"] = df["word"].astype(str).str.len()

subj_num  = df["participant_id"].str.extract(r"E(\d+)")[0].astype(int)
df["list"] = subj_num.apply(lambda n: 1 if n <= 22 else 2)

# -- Sentence reconstruction ---------------------------------------------------
print("\nReconstructing sentence texts (experimental trials only)...")

exp_df  = df[df["condition"] != "Filler"].copy()
fill_df = df[df["condition"] == "Filler"].copy()

def reconstruct(group):
    return " ".join(group.sort_values("position_num")["word"].astype(str).tolist())

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

# -- Attach comprehension probe columns ----------------------------------------
# Comprehension questions are not rows in the amplitude data -- they were
# displayed as full sentences and no ERP was extracted.
# We attach probe info to the last-word row of the preceding sentence trial.
df_out["comp_question"] = pd.NA
df_out["comp_answer"]   = pd.NA

exp_mask = df_out["condition"] != "Filler"

max_pos = (
    df_out.loc[exp_mask]
    .groupby(["participant_id", "trial"])["position_num"]
    .transform("max")
)
max_pos = max_pos.reindex(df_out.index)
is_last = exp_mask & (df_out["position_num"] == max_pos)

n_matched = 0
for idx in df_out.index[is_last]:
    row   = df_out.loc[idx]
    key   = (row["sentence_text"], int(row["list"]))
    probe = probe_lookup.get(key)
    if probe:
        df_out.at[idx, "comp_question"] = probe["comp_question"]
        df_out.at[idx, "comp_answer"]   = probe["comp_answer"]
        n_matched += 1

print(f"\n  Comp probe rows matched  : {n_matched}")
print(f"  Probed sentences in lookup: {len(probe_lookup)}")

# -- Column order --------------------------------------------------------------
col_order = [
    "study", "language", "paradigm", "list",
    "participant_id", "trial", "sentence_id", "sentence_text",
    "token_id", "word", "original_code",
    "condition", "word_position", "position_num",
    "word_length", "eprime_onset_ms", "is_erp_target",
    "N400_mean_uV",  "P600_mean_uV",
    "N400_peak_uV",  "P600_peak_uV",
    "N400_peak_lat_ms", "P600_peak_lat_ms",
    "peak_uV",
    "comp_question", "comp_answer",
]
existing = [c for c in col_order if c in df_out.columns]
df_out = (
    df_out[existing]
    .sort_values(["participant_id", "trial", "token_id"])
    .reset_index(drop=True)
)

# -- Write ---------------------------------------------------------------------
df_out.to_csv(OUT_FILE, index=False)
print(f"\nWrote: {OUT_FILE}")
print(f"  Rows         : {len(df_out):,}")
print(f"  Participants : {df_out['participant_id'].nunique()}")
print(f"  Conditions   : {sorted(df_out['condition'].dropna().unique())}")
print(f"  Unique sentences : {df_out['sentence_id'].nunique()}")
print(f"  Rows with comp_q : {df_out['comp_question'].notna().sum()}")
print(f"  List 1 subjects  : {df_out.loc[df_out['list']==1, 'participant_id'].nunique()}")
print(f"  List 2 subjects  : {df_out.loc[df_out['list']==2, 'participant_id'].nunique()}")
