# Generate prompts for wang2025_lexicaldecision

# Load libararies
import pandas as pd
import jsonlines

# Load data
df = pd.read_csv("/Users/cyhsieh/PsychLing-101/wang2025_lexicaldecision/processed_data/exp1.csv")

# create empty list to store all prompts
all_prompts = []

###########################
# Megastudy #
###########################

participant_list = df['participant_id'].unique()
trial_num = range(df['trial_id'].max() + 1)

# Instructions

instruction = "每次试验包括一个注视标记和一个刺激（真字或假字）。首先，屏幕中央呈现注视标记500毫秒，120毫秒后呈现刺激。如果你认为该刺激是真字，请按j键；如果认为是假字，请按f键。虽然没有反应时间限制，但请尽可能快速并尽最大准确性作答。如果你曾经见过或认识这些刺激，那么它很有可能是真字；如果你没有见过，那么它很可能不是真字。"

# Generate individual prompts for participants
for participant in participant_list:
    exp_participant = df[df['participant_id'] == participant]
    #age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction
    for trial in trial_num:
        exp_trial = exp_participant.loc[exp_participant['trial_id'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            image = exp_trial['image_filename'].iloc[0]
            response = exp_trial['response'].iloc[0]
            #trial_instruction = exp_trial['trial_instruction'].iloc[0]
            trial_id = exp_trial['trial_id'].iloc[0]
            accuracy = exp_trial['accuracy'].iloc[0]
            rt = exp_trial['rt'].iloc[0]
            datapoint = f'试验{trial_id}：{image}。你按下了<<{response}>>键。{accuracy}。反应时间为 {rt} 毫秒。\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'wang2025_lexicaldecision', 'participant_id': participant, 'rt': rt})

# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
