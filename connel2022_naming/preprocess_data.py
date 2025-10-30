#!/usr/bin/env python3
"""
preprocess_data.py

Minimal preprocessing:
 - drop Unnamed* columns
 - rename ppn -> participant_id
 - map ppt_* style IDs to integers starting at 0
 - rename recognition_RT -> rt
 - rename image -> image_filename
 - add trial_i
 - leave all other columns unchanged
 - write processed_data/exp1.csv
"""
from pathlib import Path
import pandas as pd
import argparse
import re
import sys

def find_case_insensitive(df, name):
    name_l = name.lower()
    for c in df.columns:
        if c.lower() == name_l:
            return c
    return None

def extract_suffix_int(s):
    m = re.search(r'(\d+)$', str(s))
    return int(m.group(1)) if m else None

def build_numeric_mapping(orig_ids):
    # preserve first-seen order; prefer numeric-suffix ordering when present
    seen = []
    for v in orig_ids:
        if v not in seen:
            seen.append(v)
    with_suffix = []
    without_suffix = []
    for v in seen:
        s = extract_suffix_int(v)
        if s is not None:
            with_suffix.append((v, s))
        else:
            without_suffix.append(v)
    with_suffix_sorted = [v for v, _ in sorted(with_suffix, key=lambda x: x[1])]
    final_order = with_suffix_sorted + without_suffix
    return {orig: idx for idx, orig in enumerate(final_order)}

def main(input_csv: Path):
    if not input_csv.exists():
        print("ERROR: input file not found:", input_csv, file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(input_csv, low_memory=False)

    # drop Unnamed* columns
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed:
        df = df.drop(columns=unnamed, errors='ignore')

    # rename ppn -> participant_id (case-insensitive), or keep existing participant_id
    if find_case_insensitive(df, "ppn"):
        df = df.rename(columns={find_case_insensitive(df, "ppn"): "participant_id"})
    else:
        # if participant-like exists, normalize its name to participant_id
        for cand in ("participant_id", "participant", "ppt", "subj", "subject"):
            c = find_case_insensitive(df, cand)
            if c:
                df = df.rename(columns={c: "participant_id"})
                break
        else:
            # fallback: create synthetic participant_id from row index strings
            df["participant_id"] = df.index.astype(str)

    # rename recognition_RT -> rt (case-insensitive)
    recog_col = find_case_insensitive(df, "recognition_RT")
    if recog_col:
        df = df.rename(columns={recog_col: "rt"})

    # rename image -> image_filename (case-insensitive)
    image_col = find_case_insensitive(df, "image")
    if image_col:
        df = df.rename(columns={image_col: "image_filename"})

    # Build numeric mapping and apply immediately (no backup column)
    orig_ids = list(df["participant_id"].astype(str))
    mapping = build_numeric_mapping(orig_ids)
    df["participant_id"] = df["participant_id"].astype(str).map(mapping).astype(int)

    # Add trial_id: zero-based per numeric participant_id
    df["trial_id"] = df.groupby("participant_id").cumcount().astype(int)

    # reorder to put participant_id, trial_id, rt (if present) at front
    cols = list(df.columns)
    front = ["participant_id", "trial_id"]
    if "rt" in cols:
        front.append("rt")
    rest = [c for c in cols if c not in front]
    df = df[front + rest]

    # decide output folder (place processed_data next to original_data parent)
    out_parent = None
    for p in input_csv.parents:
        if p.name == "original_data":
            out_parent = p.parent
            break
    if out_parent is None:
        out_parent = input_csv.parent
    outdir = out_parent / "processed_data"
    outdir.mkdir(parents=True, exist_ok=True)

    outpath = outdir / "exp1.csv"
    df.to_csv(outpath, index=False)
    print(f"Wrote processed CSV: {outpath} (rows: {len(df)}, participants: {len(mapping)})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Create processed_data/exp1.csv with numeric participant IDs (no backup column).")
    ap.add_argument("input_csv", help="Path to trial_level_data.csv")
    args = ap.parse_args()
    main(Path(args.input_csv).expanduser().resolve())

