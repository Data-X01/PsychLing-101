"""
Generate LLM prompts for Chen et al. (2026) Semantic Transparency Ratings.

Reads processed_data/exp1.csv and writes prompts.jsonl (3 lines per participant),
then compresses it to prompts.jsonl.zip.

Each participant's trials are split into 3 prompts (chunks) to stay within token limit.
Responses are marked with << >>.

Each line in the JSONL file contains:
  - "text": Full prompt with instructions, cover story, and all trial-by-trial data
  - "experiment": Identifier for the experiment
  - "participant": Participant ID (format: original_id_part1/2/3)
  - "trial_id_start": Global trial ID at the start of this prompt
  - "trial_id_end": Global trial ID at the end of this prompt (trial numbers do not reset across prompts)

"""

import json
import zipfile
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
PROC_DIR = BASE / "processed_data"
OUT_JSONL = BASE / "prompts.jsonl"
OUT_ZIP = BASE / "prompts.jsonl.zip"

exp1 = pd.read_csv(PROC_DIR / "exp1.csv")
exp1 = exp1.sort_values(["participant_id", "trial_id"]).reset_index(drop=True)

INSTRUCTION = (
    "请你对复合词的语义透明度进行打分："
    "（1）复合词各组成成分对复合词整体语义的贡献程度；"
    "（2）复合词整体语义的可推测性（即能否从各组成成分的意义推断出复合词的意义）。"
    "打分范围为0到5，其中0表示\u201c完全没有贡献\u201d或\u201c非常难以推测\u201d，5表示\u201c贡献非常大\u201d或\u201c非常容易推测\u201d。"
    "如果某个词或者汉字有多种意义，请根据第一反应进行打分。\n\n"
)

def format_trial(trial_num: int, row: pd.Series) -> str:
    compound = row["stimulus"]
    c1 = row["constituent_1"]
    c2 = row["constituent_2"]
    r1 = row["constituent_1_contribution"]
    r2 = row["constituent_2_contribution"]
    r3 = row["predictability"]
    return (
        f'{trial_num}：\n'
        f'1. "{c1}"为"{compound}"这个词的整体语义贡献了多少？'
        f'请用0-5之间的整数来回答。\n'
        f'<<{r1}>>\n'
        f'2. "{c2}"为"{compound}"这个词的整体语义贡献了多少？'
        f'请用0-5之间的整数来回答。\n'
        f'<<{r2}>>\n'
        f'3. "{compound}"的意思能从"{c1}"和"{c2}"的语义上推测出来吗？'
        f'请用0-5之间的整数来回答。\n'
        f'<<{r3}>>\n'
    )



all_prompts = []
for pid, group in exp1.groupby("participant_id", sort=False):
    # Split trials into 3 chunks
    trials_list = list(group.iterrows())
    n_trials = len(trials_list)
    chunk_size = (n_trials + 2) // 3  # Round up to distribute evenly
    
    for chunk_idx in range(3):
        start_idx = chunk_idx * chunk_size
        end_idx = min(start_idx + chunk_size, n_trials)
        
        # Get trial_id_start and trial_id_end from the data
        trial_id_start = trials_list[start_idx][1]["trial_id"]
        trial_id_end = trials_list[end_idx - 1][1]["trial_id"]
        
        # Build text for this chunk
        text = INSTRUCTION
        for trial_num, (_, row) in enumerate(trials_list[start_idx:end_idx], start=start_idx+1):
            text += format_trial(trial_num, row) + "\n"
        
        all_prompts.append({
            "text": text,
            "experiment": "chen2026transparency",
            "participant_id": f"{pid}_part{chunk_idx+1}",
            "trial_id_start": trial_id_start,
            "trial_id_end": trial_id_end,
        })

# Write JSONL

with open(OUT_JSONL, "w", encoding="utf-8") as f:
    for entry in all_prompts:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# Compress
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(OUT_JSONL, OUT_JSONL.name)
OUT_JSONL.unlink()

print(f"Written {len(all_prompts)} prompts to {OUT_ZIP.name} ({len(all_prompts) // 3} participants × 3 chunks)")
