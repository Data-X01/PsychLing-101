import pandas as pd
import jsonlines
from pathlib import Path

# load data
base_dir = Path(__file__).parent.resolve()
exp1 = pd.read_csv(base_dir / "processed_data" / "exp1.csv")
exp2 = pd.read_csv(base_dir / "processed_data" / "exp2.csv")

# sort exp by participant and trial index
exp1 = exp1.sort_values(by=['participant_id', 'trial_id'])
exp2 = exp2.sort_values(by=['participant_id', 'trial_id'])

# create trial index variable for each participant
exp1['trial_id'] = exp1.groupby('participant_id').cumcount()+1
exp2['trial_id'] = exp2.groupby('participant_id').cumcount()+1

# map participant number to 1:len(exp.participant.value_counts())
exp1['participant_id'] = exp1['participant_id'].map({p: i+1 for i, p in enumerate(exp1.participant_id.unique())})
exp2['participant_id'] = exp2['participant_id'].map({p: i+1 for i, p in enumerate(exp2.participant_id.unique())})


# create empty list to store all prompts
all_prompts = []


################
# Experiment 1 #
################
# Define number of participants and trials
participants_exp1 = exp1["participant_id"].unique()
trials_exp1 = range(exp1["trial_id"].max() + 1)

# define initial prompt
instruction1 = """
In the following study, you will see 66 sentences with questions. Your task is to read these sentences carefully and then answer the questions. Please answer using only one word. \n
You can work at your own pace, and make pauses whenever you want to. \n
"""


# Experiment1: Generate individual prompts for participants
for participant in participants_exp1:
    exp1_participant = exp1[exp1["participant_id"] == participant]
    participant = participant.item()
    individual_prompt = instruction1
    age = exp1_participant['age'].iloc[0].item()
    for trial in trials_exp1:
        exp1_trial = exp1_participant.loc[exp1_participant["trial_id"] == trial]
        if not exp1_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp1_trial["stimulus"].iloc[0]
            response = exp1_trial["response"].iloc[0]
            datapoint = f"{stimulus}. You enter <<{response}>>.\n "
            individual_prompt += datapoint
    individual_prompt += "\n"
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024comprehension/condition1",
            "participant_id": participant,
            "age": age,
        }
    )
    
    
################
# Experiment 2 #
################
# Define number of participants and trials for experiment 2
participants_exp2 = exp2["participant_id"].unique()
trials_exp2 = range(exp2["trial_id"].max() + 1)

# Define initial prompt for experiment 2
instruction2 = """
In the following study, you will see 66 sentences with questions. Your task is to read these sentences carefully and then answer the questions. \n
You can work at your own pace, and make pauses whenever you want to. \n
"""

# Experiment2: Generate individual prompts for participants
for participant in participants_exp2:
    exp2_participant = exp2[exp2["participant_id"] == participant]
    participant = participant.item()
    individual_prompt = instruction2
    age = exp2_participant['age'].iloc[0].item()
    for trial in trials_exp2:
        exp2_trial = exp2_participant.loc[exp2_participant["trial_id"] == trial]
        if not exp2_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp2_trial["stimulus"].iloc[0]
            response = exp2_trial["response"].iloc[0]
            datapoint = f"{stimulus}. You enter <<{response}>>.\n "
            individual_prompt += datapoint
    individual_prompt += "\n"
    all_prompts.append(
        {
            "text": individual_prompt,
            "experiment": "guenther2024comprehension/condition2",
            "participant_id": participant,
            "age": age,
        }
    )


# Save all prompts to JSONL file
with jsonlines.open(base_dir / 'prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
