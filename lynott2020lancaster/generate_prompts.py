"""
Generate LLM prompts for Lynott et al. (2020) Lancaster Sensorimotor Norms.

Reads processed_data/exp1.csv (Perception) and exp2.csv (Action) and writes
prompts.jsonl.zip (one line per participant per chunk of up to MAX_TRIALS_PER_PROMPT trials).

Each prompt represents a session chunk from one participant, starting with the
original task instructions followed by trial-by-trial data.

Human responses are marked with << >> as required by PsychLing-101 format.
"""

import json
import zipfile
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
PROC_DIR = BASE / "processed_data"
OUT_ZIP  = BASE / "prompts.jsonl.zip"

MAX_TRIALS_PER_PROMPT = 100   # max trials per prompt entry

# ── Instructions (verbatim from original Qualtrics survey) ────────────────────

GENERAL_INSTRUCTION = (
    "This study uses a wide range of words that are encountered in everyday life. "
    "Very occasionally, this means that some words may be offensive or explicit. "
    "If you feel that being exposed to such words will be distressing for you, we "
    "would like to remind you that you are free to end your participation in the "
    "study now or at any time you choose.\n\n"
    "If you wish to continue, please press the \"Next\" button.\n\n"
)

INSTRUCTION_PERCEPTION = (
    GENERAL_INSTRUCTION
    + "You will be asked to rate how much you experience everyday concepts using "
    "six different perceptual senses. There are no right or wrong answers so "
    "please use your own judgement.\n\n"
    "The rating scale runs from 0 (not experienced at all with that sense) to 5 "
    "(experienced greatly with that sense). Click on a number to select a rating "
    "for each scale, then click on the Next button to move on to the next item.\n\n"
    "If you do not know the meaning of a word, just check the "
    "\"Don't know the meaning of this word\" box and click \"Next\" to move onto "
    "the next item.\n\n"
)

INSTRUCTION_ACTION = (
    GENERAL_INSTRUCTION
    + "You will be asked to rate how much you experience everyday concepts by "
    "performing an action with different parts of the body. There are no right or "
    "wrong answers so please use your own judgement.\n\n"
    "The rating scale runs from 0 (not experienced at all with that body part) to "
    "5 (experienced greatly with that body part). Click on a number to select a "
    "rating for each scale, then click on the Next button to move on to the next "
    "item.\n\n"
    "If you do not know the meaning of a word, just check the "
    "\"Don't know the meaning of this word\" box and click \"Next\" to move onto "
    "the next item.\n\n"
)

# ── Dimension labels matching the on-screen wording in the Qualtrics survey ───

# Perception screen: "To what extent do you experience WORD"
#   By sensations inside your body  → Interoceptive
#   By tasting                      → Gustatory
#   By smelling                     → Olfactory
#   By feeling through touch        → Haptic
#   By hearing                      → Auditory
#   By seeing                       → Visual
PERCEPTION_DIMS = [
    ("Auditory",      "By hearing"),
    ("Gustatory",     "By tasting"),
    ("Haptic",        "By feeling through touch"),
    ("Interoceptive", "By sensations inside your body"),
    ("Olfactory",     "By smelling"),
    ("Visual",        "By seeing"),
]

# Action screen: "To what extent do you experience WORD by performing an action with the"
#   head excluding mouth  → Head
#   foot / leg            → Foot_leg
#   hand / arm            → Hand_arm
#   mouth / throat        → Mouth
#   torso                 → Torso
ACTION_DIMS = [
    ("Foot_leg", "foot / leg"),
    ("Hand_arm", "hand / arm"),
    ("Head",     "head excluding mouth"),
    ("Mouth",    "mouth / throat"),
    ("Torso",    "torso"),
]


# ── Trial formatting ──────────────────────────────────────────────────────────

def fmt_rating(val) -> str:
    """Return the rating as an integer string, or 'NA' if missing."""
    if pd.isna(val):
        return "NA"
    return str(int(val))


def format_perception_trial(trial_num: int, word: str, row: pd.Series) -> str:
    """
    Format one perception trial to mirror the Qualtrics screen:

        Trial 1: To what extent do you experience ACCOUNT (integer from 0 = not at all to 5 = greatly)
          By hearing:                    <<0>>
          By tasting:                    <<0>>
          By feeling through touch:      <<1>>
          By sensations inside your body:<<0>>
          By smelling:                   <<0>>
          By seeing:                     <<2>>
          Don't know the meaning of this word: <<0>>
    """
    lines = [f"Trial {trial_num}: To what extent do you experience {word.upper()} (integer from 0 = not at all to 5 = greatly)"]
    for col, label in PERCEPTION_DIMS:
        lines.append(f"  {label}: <<{fmt_rating(row.get(col))}>>" )
    unknown = row.get("unknown_word", 0)
    lines.append(f"  Don't know the meaning of this word: <<{fmt_rating(unknown)}>>")
    return "\n".join(lines) + "\n"


def format_action_trial(trial_num: int, word: str, row: pd.Series) -> str:
    """
    Format one action trial to mirror the Qualtrics screen:

        Trial 1: To what extent do you experience SHELL by performing an action with the (integer from 0 = not at all to 5 = greatly)
          foot / leg:           <<0>>
          hand / arm:           <<4>>
          head excluding mouth: <<0>>
          mouth / throat:       <<3>>
          torso:                <<0>>
          Don't know the meaning of this word: <<0>>
    """
    lines = [
        f"Trial {trial_num}: To what extent do you experience {word.upper()} "
        f"by performing an action with the (integer from 0 = not at all to 5 = greatly)"
    ]
    for col, label in ACTION_DIMS:
        lines.append(f"  {label}: <<{fmt_rating(row.get(col))}>>" )
    unknown = row.get("unknown_word", 0)
    lines.append(f"  Don't know the meaning of this word: <<{fmt_rating(unknown)}>>")
    return "\n".join(lines) + "\n"


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_prompts(
    exp: pd.DataFrame,
    instruction: str,
    format_trial_fn,
    exp_name: str,
) -> list[dict]:
    """
    Build prompt entries for one experiment.

    One participant's trials are split into chunks of MAX_TRIALS_PER_PROMPT.
    Each chunk becomes one JSONL entry. The chunk number is appended to the
    participant_id so entries remain uniquely identifiable:
        participant_id  →  "<pid>_part1", "<pid>_part2", …
    """
    all_prompts = []

    for pid, group in exp.groupby("participant_id", sort=False):
        group = group.sort_values("trial_id").reset_index(drop=True)

        age    = group["age"].iloc[0]
        gender = group["gender"].iloc[0]

        # Split into chunks of MAX_TRIALS_PER_PROMPT
        chunks = [
            group.iloc[i : i + MAX_TRIALS_PER_PROMPT]
            for i in range(0, len(group), MAX_TRIALS_PER_PROMPT)
        ]

        for chunk_idx, chunk in enumerate(chunks, start=1):
            text = instruction
            local_trial_num = 1          # restart numbering inside each chunk

            for _, row in chunk.iterrows():
                text += format_trial_fn(local_trial_num, row["stimulus"], row)
                text += "\n"
                local_trial_num += 1

            entry: dict = {
                "text":           text,
                "experiment":     exp_name,
                "participant":    f"{pid}_part{chunk_idx}",
            }
            if pd.notna(age):
                entry["age"] = int(age)
            if pd.notna(gender):
                entry["gender"] = gender

            all_prompts.append(entry)

    return all_prompts


# ── Main ──────────────────────────────────────────────────────────────────────

all_prompts: list[dict] = []

print("Processing Perception (exp1) …")
exp1 = pd.read_csv(PROC_DIR / "exp1.csv", dtype={"participant_id": str})
perception_prompts = build_prompts(
    exp1,
    INSTRUCTION_PERCEPTION,
    format_perception_trial,
    "lynott2020lancaster/perception",
)
all_prompts += perception_prompts
print(f"  → {len(perception_prompts)} prompt entries "
      f"({exp1['participant_id'].nunique()} participants)")

print("Processing Action (exp2) …")
exp2 = pd.read_csv(PROC_DIR / "exp2.csv", dtype={"participant_id": str})
action_prompts = build_prompts(
    exp2,
    INSTRUCTION_ACTION,
    format_action_trial,
    "lynott2020lancaster/action",
)
all_prompts += action_prompts
print(f"  → {len(action_prompts)} prompt entries "
      f"({exp2['participant_id'].nunique()} participants)")

# ── Write JSONL zip ───────────────────────────────────────────────────────────

tmp_jsonl = BASE / "prompts.jsonl"
with open(tmp_jsonl, "w", encoding="utf-8") as f:
    for entry in all_prompts:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(tmp_jsonl, tmp_jsonl.name)
tmp_jsonl.unlink()

print(f"\nWritten {len(all_prompts)} total prompt entries to {OUT_ZIP.name}")
print("Done.")