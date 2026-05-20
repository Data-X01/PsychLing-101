# Generating prompts for hsieh2025_rating

import pandas as pd
import jsonlines

# Load data
df = pd.read_csv("/Users/cyhsieh/PsychLing-101/hsieh2025_rating/processed_data:/rating.csv")

# create empty list to store all prompts
all_prompts = []

# Instructions

instruction = "此份問卷每道題目皆為由兩個中文字所構成的詞語，其中大多數的詞彙您可能從未見過。請您根據直覺判斷能否想到該詞語可能的意義，若認為「幾乎無法」，請填答1；若認為「非常容易」，請填答5。以下有三個範例僅供參考（無需填答），其中有些可能對您來說很容易聯想到某個意思，有些可能很難，不過並沒有標準答案，您可以憑自身語感試著賦予這些詞彙意義。 "

# Generate individual prompts for participants
participant_list = df['participant_id'].unique()
trial_list = df['trial_id'].unique()

for participant in participant_list:
    exp_participant = df[df['participant_id'] == participant]
    #age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction
    for trial in trial_list:
        exp_trial = exp_participant.loc[exp_participant['trial_id'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            response = exp_trial['response'].iloc[0]
            datapoint = f'Trial {trial}: The word is {stimulus}. You enter <<{response}>>. \n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'hsieh2025_rating/dataA', 'participant_id': int(participant)})

# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
