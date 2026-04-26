#!/usr/bin/env python3
"""
generate_prompts.py — jap2026_indonesian_verb_bias_erp
-------------------------------------------------------
Reads processed_data/exp1.csv and produces prompts.jsonl.zip
for the PsychLing-101 database. One JSON line per participant,
encoding their full ERP session in natural language.

ERP amplitudes (N400_mean_uV, P600_mean_uV) at the three
ERP-target positions (VERB, ADV, NP2_w2) are marked << >>.

JSONL fields per line:
  text           — full natural-language prompt (< 32K tokens)
  experiment     — study identifier string
  participant_id — participant code (e.g. "E01")

Token budget: ~4,500–6,500 tokens per participant (well within 32K).
"""

import io
import json
import os
import zipfile

import pandas as pd
import tiktoken

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IN_FILE  = os.path.join(BASE_DIR, "processed_data", "exp1.csv")
OUT_ZIP  = os.path.join(BASE_DIR, "processed_data", "prompts.jsonl.zip")

EXPERIMENT = "jap2026_indonesian_verb_bias_erp"
TOKEN_LIMIT = 32_000

# ── Task instructions (translated from original E-Prime script) ────────────────
INSTRUCTIONS = """\
In this experiment, you will read Indonesian sentences word by word \
while your brain activity (EEG) is recorded. Each sentence appears \
one word at a time on the screen. Read each sentence naturally and \
attentively. After some sentences, a yes/no comprehension question \
will appear — answer as accurately as you can by pressing the \
corresponding button. Your brain's electrical response is measured \
at three key positions in each experimental sentence: the main verb, \
the post-verbal adverb, and the head noun of the second argument NP. \
N400 and P600 mean amplitudes (in µV, averaged over the relevant \
electrode clusters) are reported for those positions.\
"""

# ── Load ───────────────────────────────────────────────────────────────────────
df = pd.read_csv(IN_FILE)
print(f"Loaded {len(df):,} rows | {df['participant_id'].nunique()} participants")

# ── Token counter (cl100k_base is a safe approximation) ───────────────────────
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# ── Build prompts ──────────────────────────────────────────────────────────────
exp_df   = df[df["condition"] != "Filler"].copy()
filler_df = df[df["condition"] == "Filler"].copy()

records  = []
token_counts = []

for pid, pdata in exp_df.groupby("participant_id"):
    lines = [INSTRUCTIONS, ""]
    trial_num = 0

    for trial_id, tdata in pdata.sort_values(["trial", "position_num"]).groupby("trial"):
        trial_num += 1
        words = tdata.sort_values("position_num")

        cond = words["condition"].iloc[0]
        lines.append(f"Trial {trial_num} [{cond}]:")

        for _, row in words.iterrows():
            word     = row["word"]
            pos_name = row["word_position"]
            is_tgt   = row["is_erp_target"] == 1

            if is_tgt:
                n4  = row["N400_mean_uV"]
                p6  = row["P600_mean_uV"]
                n4s = f"<<{n4:.2f}>>" if pd.notna(n4) else "<<NA>>"
                p6s = f"<<{p6:.2f}>>" if pd.notna(p6) else "<<NA>>"
                lines.append(
                    f"  {pos_name:8s}  '{word}'"
                    f"   N400: {n4s} µV   P600: {p6s} µV"
                )
            else:
                lines.append(f"  {pos_name:8s}  '{word}'")

        lines.append("")   # blank line between trials

    text = "\n".join(lines)
    n_tok = count_tokens(text)
    token_counts.append(n_tok)

    if n_tok > TOKEN_LIMIT:
        print(f"  ⚠ {pid}: {n_tok:,} tokens — EXCEEDS 32K limit, truncating...")
        # Truncate to last complete trial that fits
        safe_lines = []
        running = 0
        buffer  = []
        for line in lines:
            buffer.append(line)
            if line == "":          # end of a trial block
                block_toks = count_tokens("\n".join(buffer))
                if running + block_toks > TOKEN_LIMIT:
                    break
                safe_lines.extend(buffer)
                running += block_toks
                buffer = []
        text = "\n".join(safe_lines)

    records.append({
        "text"          : text,
        "experiment"    : EXPERIMENT,
        "participant_id": pid,
    })

print(f"\nToken stats across {len(token_counts)} participants:")
s = pd.Series(token_counts)
print(f"  min={s.min():,}  median={s.median():,.0f}  max={s.max():,}  "
      f"over_32k={( s > TOKEN_LIMIT).sum()}")

# ── Write prompts.jsonl.zip ────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT_ZIP), exist_ok=True)
jsonl_buf = io.BytesIO()
for rec in records:
    jsonl_buf.write((json.dumps(rec, ensure_ascii=False) + "\n").encode("utf-8"))

with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("prompts.jsonl", jsonl_buf.getvalue())

print(f"\n✓ Wrote: processed_data/prompts.jsonl.zip")
print(f"  Participants : {len(records)}")

# ── Show one sample ────────────────────────────────────────────────────────────
sample = records[0]["text"].split("\n")[:30]
print("\nSample (first 30 lines of E01):")
print("\n".join(sample))