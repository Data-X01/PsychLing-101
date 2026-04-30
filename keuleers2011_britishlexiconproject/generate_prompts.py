import pandas as pd
import jsonlines
import random
import math
import os
import zipfile

def generate_prompts():
    print("Loading preprocessed dataset")
    df = pd.read_csv('processed_data/exp1.csv', low_memory=False)

    all_prompts = []

    base_instruction = (
        'In this task, you will see a string of letters on the screen. '
        'If the string is a REAL ENGLISH word, press the button "{word_key}". '
        'If the string is a non-sense word, press the button "{nonword_key}".\n\n'
    )

    print("Grouping trials by participant and block")
    grouped = df.groupby(['participant_id', 'phase_id'])

    prompt_count = 0

    for (participant_id, phase_id), group in grouped:

        group = group.sort_values('trial_order')

        word_key, nonword_key = random.choice([('a', 'l'), ('l', 'a')])

        individual_prompt = base_instruction.format(word_key=word_key, nonword_key=nonword_key)

        rt_list = []
        trial_counter = 1

        for _, row in group.iterrows():
            stimulus = row['stimulus']
            resp = row['response']
            acc = row['accuracy']
            rt = row['rt']

            if resp == 'W':
                pressed_key = word_key
            elif resp == 'N':
                pressed_key = nonword_key
            else:
                pressed_key = 'timeout'

            feedback = "Correct." if acc == 1.0 else "Incorrect."

            if pd.isna(rt):
                rt_list.append(None)
            else:
                rt_list.append(float(rt))

            datapoint = f"Trial {trial_counter}: The string is '{stimulus}'. You press <<{pressed_key}>>. {feedback}\n"
            individual_prompt += datapoint
            
            trial_counter += 1
        
        all_prompts.append({
            'text': individual_prompt,
            'experiment': 'keuleers2011_britishlexiconproject/exp1',
            'participant_id': f"{participant_id}_block_{int(phase_id)}", 
            'rt': rt_list
        })

        prompt_count += 1
        if prompt_count % 500 == 0:
            print(f"Generated {prompt_count} block prompts")

    output_file = "prompts.jsonl"
    zip_file = "prompts.jsonl.zip"
    
    print(f"Writing all {len(all_prompts)} prompts to {output_file}")
    with jsonlines.open(output_file, "w") as writer:
        writer.write_all(all_prompts)

    print(f"Compressing to {zip_file}")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(output_file, arcname=output_file)

    print(f"Removing uncompressed {output_file}")
    os.remove(output_file)

    print("Prompt generation and compression complete.")

if __name__ == "__main__":
    generate_prompts()