import pandas as pd
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
EXP1_FILE = ROOT / "processed_data" / "exp1.csv"
PROMPTS_FILE = ROOT / "prompts.jsonl"
PROMPTS_ZIP = ROOT / "prompts.jsonl.zip"
EXPERIMENT_NAME = "aguasvivas2018_spalex"

df = pd.read_csv(EXP1_FILE, encoding="utf-8")

def make_prompt(participant_df):
    participant_df = participant_df.sort_values("trial")
    lines = [
        'In this task, you will see Spanish letter strings one at a time. '
        'If the string is a real Spanish word, press "word". '
        'If it is not a real Spanish word, press "nonword".',
        ""
    ]
    for _, row in participant_df.iterrows():
        stim     = str(row["stimulus"])
        label    = str(row["condition"])
        acc      = int(row["correct"])
        rt       = int(row["rt"])
        response = label if acc == 1 else ("nonword" if label == "word" else "word")
        feedback = "Correct." if acc == 1 else "Incorrect."
        lines.append(
            f'Trial {int(row["trial"]) + 1}: The letter string is "{stim}". '
            f'You press <<{response}>>. {feedback} Reaction time: <<{rt} ms>>.'
        )
    return "\n".join(lines)

with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
    for pid, subdf in df.groupby("participant", sort=True):
        obj = {
            "text": make_prompt(subdf),
            "experiment": EXPERIMENT_NAME,
            "participant": str(pid)
        }
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

with zipfile.ZipFile(PROMPTS_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(PROMPTS_FILE, arcname="prompts.jsonl")

print(f"Done. {df['participant'].nunique():,} participants written to {PROMPTS_ZIP}")
