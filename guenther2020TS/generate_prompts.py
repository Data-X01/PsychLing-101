import pandas as pd
import jsonlines
import random
import string
from pathlib import Path


# Randomize choice options: function to draw n random letters from the alphabet without replacement
def random_letters(n):
    return ''.join(random.sample(string.ascii_lowercase, n))

# Load data
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
    rt_list = []
    
    # generate two choice options
    choices = random_letters(2)
    
    # Update response column using loc
    df_participant.loc[df_participant["response"] == "c", "response"] = choices[0]
    df_participant.loc[df_participant["response"] == "n", "response"] = choices[1]
    
    # instruction text
    prompt = f"""In the following study, you will see complex words such as airport or warzone in the browser window. You will have to judge for each word whether it has a sensible interpretation or not. \n
    For example, airport has a sensible interpretation, while saddleolive would be considered nonsensical by most persons. Please rely on your own intuition while making these judgements; there are no definitive correct or wrong answers. \n
    However, we sincerely want to ask you to be as diligent as possible in making these judgements. For our study, we cannot analyse data only consisting of random answers. \n
    You will see these words one after another. If you feel that a word has a sensible interpretation, press the {choices[0]} key on your keyboard. If you feel that a word does not make sense, press the {choices[1]} key. You are free to write these button assignments down if it helps you remembering them. \n
    The study will not continue unless you give a response. Thus, if you want to pause the study, you can delay your response until you want to continue. \n
    By pressing the ESC key, you will end the fullscreen mode. This does not hinder you from continuing the experiment, but you cannot switch back to fullscreen mode. If possible, we want to ask you to stay in fullscreen mode for the whole duration of the experiment. \n"""
    
    
    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_id'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            word = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            datapoint = f'The word "{word}" appears on the screen. You press <<{response}>>.\n '
            prompt += datapoint
            
            # Store reaction time
            rt = df_trial['rt'].iloc[0].item()
            rt_list.append(rt)
            
    prompt += '\n'
    
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2020TS',
        'participant_id': participant,
        'age': age,
        'rt': rt_list
    })

# Save all prompts to JSONL file
with jsonlines.open(base_dir / 'prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)
