"""
generate_prompts.py
-------------------
Reads processed_data/exp1.csv and writes prompts.jsonl with one entry
per participant. Each prompt represents a full session:
  - Starts with task instructions
  - Followed by one line per cue trial
  - Human responses marked with << >>
"""

import json
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Task instructions (use original wording where available)
# ---------------------------------------------------------------------------

INSTRUCTIONS = (
    "In this task, you will see a cue word, and you will be asked to type "
    "any associated words which come to mind, one by one.\n\n"
)

EXPERIMENT_ID = "exp1/word_associations"


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def generate_prompts(base_dir: Path) -> None:
    exp1_path = base_dir / "processed_data" / "exp1.csv"
    if not exp1_path.exists():
        raise FileNotFoundError(f"Could not find {exp1_path}. Run preprocess_data.py first.")

    df = pd.read_csv(exp1_path)

    # Identify response columns (response1 … response20)
    response_cols = [c for c in df.columns if c.startswith("response") and c[8:].isdigit()]
    response_cols = sorted(response_cols, key=lambda c: int(c[8:]))

    all_prompts = []

    for participant_id, participant_df in df.groupby("participant_id"):
        participant_df = participant_df.sort_values("trial_id")

        prompt_text = INSTRUCTIONS

        for _, row in participant_df.iterrows():
            stimulus = row["stimulus"]

            # Collect non-empty responses in order
            responses = [
                str(row[col]).strip()
                for col in response_cols
                if pd.notna(row[col]) and str(row[col]).strip() not in ("", "nan")
            ]

            if not responses:
                continue

            # Format: cue word followed by responses in << >>
            responses_formatted = ", ".join(f"<<{r}>>" for r in responses)
            prompt_text += f"Cue: {stimulus}. You respond: {responses_formatted}.\n"

        entry = {
            "text":        prompt_text,
            "experiment":  EXPERIMENT_ID,
            "participant": int(participant_id),
        }
        all_prompts.append(entry)

    # Write JSONL
    out_path = base_dir / "prompts.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for entry in all_prompts:
            f.write(json.dumps(entry) + "\n")

    print(f"  Written: {out_path.name}  ({len(all_prompts)} participants)")

    # Print one example prompt
    print("\n--- Example prompt (participant 1) ---\n")
    print(all_prompts[0]["text"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    base = Path(__file__).parent.resolve()
    print(f"\nGenerating prompts in: {base}\n")
    generate_prompts(base)
    print("Done.\n")
