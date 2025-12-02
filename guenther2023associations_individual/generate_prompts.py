import pandas as pd
import jsonlines
from pathlib import Path

# load data
base_dir = Path(__file__).parent.resolve()
exp = pd.read_csv(base_dir / "processed_data" / "exp1.csv")

# New code to replace the current concatenation line
response_cols = [f"response{i}" for i in range(1, 11)]

# drop missing responses
exp["response"] = (
    exp[response_cols]
    .apply(lambda row: ", ".join([x for x in row if pd.notna(x)]), axis=1)
)

# Define number of participants and trials
participants_exp = exp['participant_id'].unique()
trials_exp = range(exp['trial_id'].max() + 1)

# define initial prompt
instruction = 'On the top of the screen a word will appear. Enter the first 10 words that come to mind when reading this word.\n'\
    'Please enter 10 different words for each word presented to you.\n'\
    'Please take this task seriously, and enter actual words. We kindly ask you to ensure that these words are spelled correctly.\n'\
    'Some hints\n'\
    'Only give associations to the word on top of the screen (not to your previous responses!)\n'\
    'Please only enter single words; otherwise, you will receive an error message.\n'

# define trial instruction
trial_instruction = 'Please enter the first 10 different words that come to your mind.'

# create empty list to store all prompts
all_prompts = []

# Generate individual prompts for participants
for participant in participants_exp:
    exp_participant = exp[exp['participant_id'] == participant]
    participant = participant.item()
    age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction
    for trial in trials_exp:
        exp_trial = exp_participant.loc[exp_participant['trial_id'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            response = exp_trial['response'].iloc[0]
            datapoint = f'{stimulus}. {trial_instruction} You enter <<{response}>>.\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'guenther2024associations_individual', 'participant_id': participant, 'age': age})

# Save all prompts to JSONL file
with jsonlines.open(base_dir / "prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
