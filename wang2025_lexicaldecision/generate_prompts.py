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

instruction = "A trial consisted of a fixation sign and a stimulus (character or pseudocharacter). First, a fixation sign was presented in the center of the screen for 500 ms, followed 120 ms later by a stimulus. Pressed the button j if you think the stimulus is a real character and f if it is a pseudocharacter. There was no time limit for the response but you should respond as quickly as possible with your best shot at accuracy. If you have ever seen or known these stimuli, there is a higher chance that it is a character. If you have not, it has a higher chance of not being a character."

# Generate individual prompts for participants
for participant in participant_list:
    exp_participant = df[df['participant_id'] == participant]
    #age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction
    for trial in trial_num:
        exp_trial = exp_participant.loc[exp_participant['trial_id'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            response = exp_trial['response'].iloc[0]
            #trial_instruction = exp_trial['trial_instruction'].iloc[0]
            trial_id = exp_trial['trial_id'].iloc[0]
            accuracy = exp_trial['accuracy'].iloc[0]
            rt = exp_trial['rt'].iloc[0]
            datapoint = f'Trial {trial_id}: The character is {stimulus}. You enter <<{response}>>. {accuracy}. Reaction time is {rt} ms\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'wang2025_lexicaldecision', 'participant_id': participant, 'rt': rt})

# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)
