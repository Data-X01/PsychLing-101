"""
Generate LLM prompts for de Varda et al. (2024) Cloze Probability Task

This script reads the processed cloze probability data and generates a JSONL file
with one line per participant, following the PsychLing-101 format.

Participants completed a cloze probability task where they saw sentence fragments
and wrote the next word they expected to follow.
"""

import json
import zipfile
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
PROCESSED_DATA_DIR = SCRIPT_DIR / "processed_data"
INPATH = PROCESSED_DATA_DIR / "exp1.csv"
OUTPATH = SCRIPT_DIR / "prompts.jsonl"
ZIP_OUTPATH = SCRIPT_DIR / "prompts.jsonl.zip"

INSTRUCTION_TEXT = """In this task, you will read sentence fragments and write the next word you expect to follow.

Your task is to continue each sentence by writing what you expect to be the next word. Even if you come up with several options, you should always produce one single word – the one that, in your immediate intuition, should follow what was presented. The to-be-produced word can belong to any part-of-speech, including articles and prepositions.

"""


def format_trial_description(trial_idx: int, stimulus: str, response: str) -> str:
    """
    Format a single trial into a descriptive string.
    
    Args:
        trial_idx: Trial number for display (1-indexed)
        stimulus: The sentence fragment shown to participant
        response: The word the participant wrote
        
    Returns:
        Formatted trial description string
    """
    return f"Trial {trial_idx}: '{stimulus}...' You write: <<{response}>>"


def print_example_prompts(df: pd.DataFrame, n_participants: int = 2, n_trials: int = 5):
    """Print nicely formatted example prompts for verification."""
    print("\n" + "=" * 70)
    print("EXAMPLE PROMPTS")
    print("=" * 70)
    
    participants = sorted(df["participant_id"].unique())[:n_participants]
    
    for pid in participants:
        sub_df = df[df["participant_id"] == pid].sort_values("trial_order").head(n_trials)
        
        print(f"\n{'─' * 70}")
        print(f"PARTICIPANT: {pid}")
        print(f"{'─' * 70}")
        print(INSTRUCTION_TEXT)
        
        for _, row in sub_df.iterrows():
            desc = format_trial_description(
                trial_idx=int(row["trial_order"]) + 1,
                stimulus=str(row["stimulus"]),
                response=str(row["response"]) if pd.notna(row["response"]) else ""
            )
            print(desc)
        
        print(f"... ({len(df[df['participant_id'] == pid])} trials total)")
        print()


def main():
    """Main prompt generation function."""
    print(f"Loading data from: {INPATH}")
    
    if not INPATH.exists():
        print(f"Error: Input file not found at {INPATH}")
        print("Please run preprocess_data.py first.")
        exit(1)
    
    df = pd.read_csv(INPATH, low_memory=False)
    
    # Get unique participants
    participants = sorted(df["participant_id"].unique())
    print(f"Processing data for {len(participants)} unique participants...")
    
    records_written = 0
    
    with OUTPATH.open("w", encoding="utf8") as fo:
        for pid in participants:
            # Get trials for this participant (sorted by presentation order)
            sub_df = df[df["participant_id"] == pid].sort_values("trial_order")
            
            # Build trial descriptions (using trial_order for correct presentation sequence)
            trials = []
            for _, row in sub_df.iterrows():
                desc = format_trial_description(
                    trial_idx=int(row["trial_order"]) + 1,  # 1-indexed for display
                    stimulus=str(row["stimulus"]),
                    response=str(row["response"]) if pd.notna(row["response"]) else ""
                )
                trials.append(desc)
            
            # Combine instruction and trials
            text_body = INSTRUCTION_TEXT + "\n".join(trials) + "\n"
            
            # Get optional metadata
            first_row = sub_df.iloc[0]
            
            result = {
                "participant": str(pid),
                "experiment": "devardaetal2024_cloze",
                "text": text_body
            }
            
            # Add optional demographic metadata if available
            if pd.notna(first_row.get("age")):
                result["age"] = int(first_row["age"])
            if first_row.get("gender") and str(first_row["gender"]).strip():
                result["gender"] = str(first_row["gender"])
            if first_row.get("nationality") and str(first_row["nationality"]).strip():
                result["nationality"] = str(first_row["nationality"])
            if first_row.get("first_language") and str(first_row["first_language"]).strip():
                result["first_language"] = str(first_row["first_language"])
            if first_row.get("education") and str(first_row["education"]).strip():
                result["education"] = str(first_row["education"])
            
            fo.write(json.dumps(result, ensure_ascii=False) + "\n")
            records_written += 1
    
    print(f"Successfully wrote {records_written} participant records to: {OUTPATH}")
    
    # Create zip file
    with zipfile.ZipFile(ZIP_OUTPATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUTPATH, "prompts.jsonl")
    
    print(f"Created zip archive: {ZIP_OUTPATH}")
    
    # Remove unzipped file
    OUTPATH.unlink()
    print(f"Removed unzipped file: {OUTPATH}")
    
    # Verify token count for a sample participant
    sample_participant = participants[0]
    sample_text = df[df["participant_id"] == sample_participant]
    approx_tokens = len(INSTRUCTION_TEXT.split()) + sum(len(str(r).split()) for r in sample_text["stimulus"]) * 2
    print(f"\nApproximate tokens per participant: ~{approx_tokens} (well under 32K limit)")
    
    # Print example prompts
    print_example_prompts(df)


if __name__ == "__main__":
    main()
