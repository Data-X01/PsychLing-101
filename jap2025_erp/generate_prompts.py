#!/usr/bin/env python3
"""
generate_prompts.py -- jap2025_erp
------------------------------------
Reads processed_data/exp1.csv and produces prompts.jsonl.zip.
One JSON line per participant encoding their full ERP session.

N400 and P600 mean amplitudes (uV) are marked << >> for every word
in each trial. Comprehension questions are appended after probed
trials -- no ERP values for the question screen itself.

JSONL fields:
  text           -- full natural-language prompt
  experiment     -- study identifier string
  participant_id -- participant code (e.g. "E01")
"""

import io
import json
import os
import zipfile

import pandas as pd
import tiktoken

# -- Paths ---------------------------------------------------------------------
BASE_DIR = r"D:\PsychLing-101\jap2025_erp"
IN_FILE  = os.path.join(BASE_DIR, "processed_data", "exp1.csv")
OUT_ZIP  = os.path.join(BASE_DIR, "processed_data", "prompts.jsonl.zip")

EXPERIMENT  = "jap2025_erp"
TOKEN_LIMIT = 128_000

# -- Task instructions (in Bahasa Indonesia, matching what participants saw) ---
INSTRUCTIONS = (
    "Dalam eksperimen ini, Anda akan membaca kalimat-kalimat bahasa Indonesia "
    "satu kata per kata sambil aktivitas otak Anda (EEG) direkam. Setiap kata "
    "muncul satu per satu di layar. Bacalah setiap kalimat secara alami dan "
    "penuh perhatian. Setelah beberapa kalimat, sebuah pertanyaan pemahaman "
    "ya/tidak akan muncul di layar sebagai kalimat utuh -- peserta menjawab "
    "dengan menekan tombol (ya / tidak). Tidak ada perekaman ERP untuk layar "
    "pertanyaan pemahaman itu sendiri. Amplitudo rata-rata N400 dan P600 "
    "(dalam uV, dirata-ratakan dari kluster elektroda yang relevan) "
    "dilaporkan untuk setiap kata dalam kalimat."
)

# -- Load ----------------------------------------------------------------------
df = pd.read_csv(IN_FILE)
print(f"Loaded {len(df):,} rows | {df['participant_id'].nunique()} participants")

# -- Token counter -------------------------------------------------------------
enc = tiktoken.get_encoding("cl100k_base")
def count_tokens(text):
    return len(enc.encode(text))

# -- Answer map ----------------------------------------------------------------
ANSWER_MAP = {"y": "ya (yes)", "t": "tidak (no)"}

def format_answer(ans):
    if pd.isna(ans):
        return ""
    return ANSWER_MAP.get(str(ans).strip().lower(), str(ans))

# -- Build prompts -------------------------------------------------------------
exp_df = df[df["condition"] != "Filler"].copy()

records      = []
token_counts = []

for pid, pdata in exp_df.groupby("participant_id"):
    lines     = [INSTRUCTIONS, ""]
    trial_num = 0

    for trial_id, tdata in pdata.sort_values(["trial", "position_num"]).groupby("trial"):
        trial_num += 1
        words = tdata.sort_values("position_num")

        lines.append(f"Trial {trial_num}:")

        comp_q   = None
        comp_ans = None

        for _, row in words.iterrows():
            word = row["word"]
            n4   = row["N400_mean_uV"]
            p6   = row["P600_mean_uV"]
            n4s  = f"<<{n4:.2f}>>" if pd.notna(n4) else "<<?>>"
            p6s  = f"<<{p6:.2f}>>" if pd.notna(p6) else "<<?>>"
            lines.append(f"  '{word}'  N400: {n4s} uV  P600: {p6s} uV")

            if pd.notna(row.get("comp_question")):
                comp_q   = row["comp_question"]
                comp_ans = row.get("comp_answer")

        if comp_q:
            lines.append(
                f"  Comprehension check: {comp_q}"
                f"  [Correct answer: {format_answer(comp_ans)}]"
            )

        lines.append("")

    text  = "\n".join(lines)
    n_tok = count_tokens(text)
    token_counts.append(n_tok)

    if n_tok > TOKEN_LIMIT:
        print(f"  WARNING {pid}: {n_tok:,} tokens exceeds {TOKEN_LIMIT:,} -- truncating...")
        safe_lines = []
        running    = 0
        buffer     = []
        for line in lines:
            buffer.append(line)
            if line == "":
                block_toks = count_tokens("\n".join(buffer))
                if running + block_toks > TOKEN_LIMIT:
                    break
                safe_lines.extend(buffer)
                running += block_toks
                buffer   = []
        text = "\n".join(safe_lines)

    records.append({
        "text":           text,
        "experiment":     EXPERIMENT,
        "participant_id": pid,
    })

print(f"\nToken stats across {len(token_counts)} participants:")
s = pd.Series(token_counts)
print(f"  min={s.min():,}  median={s.median():,.0f}  max={s.max():,}  "
      f"over_limit={(s > TOKEN_LIMIT).sum()}")

# -- Write prompts.jsonl.zip ---------------------------------------------------
os.makedirs(os.path.dirname(OUT_ZIP), exist_ok=True)
jsonl_buf = io.BytesIO()
for rec in records:
    jsonl_buf.write((json.dumps(rec, ensure_ascii=False) + "\n").encode("utf-8"))

with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("prompts.jsonl", jsonl_buf.getvalue())

print(f"\nWrote: processed_data/prompts.jsonl.zip")
print(f"  Participants : {len(records)}")

# -- Sample output -------------------------------------------------------------
sample = records[0]["text"].split("\n")[:50]
print("\nSample (first 50 lines of E01):")
print("\n".join(sample))
