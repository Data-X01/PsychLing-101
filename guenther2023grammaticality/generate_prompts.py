import pandas as pd
import jsonlines
import random
import string
from pathlib import Path

# Randomize choice options: function to draw n random letters from the alphabet without replacement
def random_letters(n):
    return ''.join(random.sample(string.ascii_lowercase, n))


# load data
base_dir = Path(__file__).parent.resolve()
df = pd.read_csv(base_dir / "processed_data" / "exp1.csv")

# Sort dataframe by participant ID and trial order
df = df.sort_values(by=['participant_id', 'trial_id'])

# Remap participant IDs to sequential integers starting from 1
df['participant_id'] = df['participant_id'].map({p: i+1 for i, p in enumerate(df.participant_id.unique())})

# Get unique participants and trial indices
participants = df['participant_id'].unique()
trials = range(df['trial_id'].max() + 1)



# Generate individual prompts for each participant
all_prompts = []
for participant in participants:
    # Get data for current participant
    df_participant = df[df['participant_id'] == participant]
    participant = participant.item()
    age = df_participant['age'].iloc[0].item()

    # generate two choice options
    choices = random_letters(2)
    
    # Update response column using loc
    df_participant.loc[df_participant["response"] == "c", "response"] = choices[0]
    df_participant.loc[df_participant["response"] == "n", "response"] = choices[1]
    
    # instruction text
    prompt = f"""
    In the following study, you will see 110 sentences. Your task is to indicate whether these sentences are grammatically correct in English.\n
    Press the {choices[0]}  key on your keyboard if the sentence is grammatically correct, and the {choices[1]} key if it is not grammatically correct.\n
    \n
    You can work at your own pace, and make pauses whenever you want to.\n
    \n
    Is this sentence grammatically correct in English?\n
    \n
    Press {choices[0]} if it is correct, and {choices[1]} if it is not correct."""
    
    rt_list = []
    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_id'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            word = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            datapoint = f'Sentence "{word}" appears on the screen. You press <<{response}>>.\n '
            prompt += datapoint
            
            # store reaction time
            rt = df_trial['rt'].iloc[0].item()
            rt_list.append(rt)
    prompt += '\n'
    
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2023Grammaticality',
        'participant_id': participant,
        'age': age,
        'rt': rt_list
    })

# Save all prompts to JSONL file
with jsonlines.open(base_dir / 'prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
