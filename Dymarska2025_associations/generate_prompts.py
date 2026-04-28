import pandas as pd
import json
from pathlib import Path

def generate_prompts():
    base_dir = Path(".")
    processed_file = base_dir / "processed_data" / "exp1.csv"
    output_file = base_dir / "prompts.jsonl"

    if not processed_file.exists():
        print(f"Error: {processed_file} not found. Run preprocess_data.py first.")
        return

    # 1. Read the standardized data
    df = pd.read_csv(processed_file)

    # 2. Define instructions
    instructions = (
           "In this task, you will see a cue word, and you will be asked to type "
    "any associated words which come to mind, one by one.\n\n"
    )

    prompts = []

    # 3. Group by participant to represent an entire session per prompt
    for p_id, group in df.groupby("participant_id"):
        # Sort by trial_id to ensure chronological order
        group = group.sort_values("trial_id")
        
        prompt_text = instructions
        
        # 4. Build trial-by-trial data
        for _, row in group.iterrows():
            trial_str = f"Trial {row['trial_id'] + 1}:\n"
            trial_str += f"  Stimulus: '{row['stimulus']}'\n"
            
            # Gather all 20 responses
            responses = []
            for i in range(1, 21):
                resp = row[f'response{i}']
                if pd.notna(resp) and str(resp).strip() != "":
                    responses.append(f"<<{str(resp).strip()}>>")
            
            resp_string = ", ".join(responses)
            trial_line = f"{row['stimulus']}. You enter {resp_string}.\n"
            prompt_text += trial_line




        # 5. Create JSONL entry
        entry = {
            "text": prompt_text.strip(),
            "experiment": "word_association_exp1",
            "participant_id": str(p_id)
        }
        prompts.append(entry)

    # 6. Write to JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for p in prompts:
            f.write(json.dumps(p) + '\n')

    print(f"Successfully generated {len(prompts)} participant prompts in {output_file}")

if __name__ == "__main__":
    generate_prompts()
