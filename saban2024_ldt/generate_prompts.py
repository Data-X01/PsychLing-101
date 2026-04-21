###Experiment 1 with colour associate pseudowords
import pandas as pd
import jsonlines
import random
import string
from pathlib import Path

path = Path("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Preparation of data/Experiment 1 - colour associates") / "prompts-LDT Exp1.jsonl"

#df = pd.read_excel("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/merge27 - filtering necessary columns.xlsx")
df = pd.read_csv("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Saban-Italian LDT Exp1.csv", sep=';')

# Get unique participants and trial indices
participants = df['participant_id'].unique() #This puts each participant in a separate column
trials = range(df['trial_id'].max() + 1)

#Recode response keys
df["key"] = df["key"].map({1: "a", 2: "l"})

# Generate individual prompts for each participant
all_prompts = []

#Define response options/choices
choices = ("a", "l")  # fixed keys

for participant in participants:
    df_participant = df[df['participant_id'] == participant]

    if df_participant.empty:
        continue  # safety

    participant = participant.item()
    age = df_participant['age'].iloc[0].item()

    rt_list = []

    prompt = f"""In this study you will be shown various stimuli on the screen. Your task is to determine whether each one is a real Italian word or not.\n 
If you think it is a real Italian word, press the {choices[0]} key on your keyboard. If you think it is not a real Italian word, press the {choices[1]} key.\n
Ignore the colour of the stimulus and focus on whether or not the word exists in Italian.\n"""

    for _, row in df_participant.iterrows():
        word = row['stimuli']
        response = row['key']

        prompt += f'The word "{word}" appears on the screen. You press <<{response}>>.\n'
        rt_list.append(row['rt'])

    all_prompts.append({
        'text': prompt,
        'experiment': 'Saban_ItalianLDT-Exp1',
        'participant_id': participant,
        'age': age,
        'rt': rt_list,
    })

#Save all prompts to JSONL file
with jsonlines.open(path, mode='w') as writer:
    writer.write_all(all_prompts)


### Experiment 2 with colour word pseudowords
import pandas as pd
import jsonlines
import random
import string
from pathlib import Path

path = Path("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Preparation of data/Experiment 2 - colour words") / "prompts-LDT Exp2.jsonl"

#df = pd.read_excel("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/merge27 - filtering necessary columns.xlsx")
df = pd.read_csv("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Saban-Italian LDT Exp2.csv", sep=';')

# Get unique participants and trial indices
participants = df['participant_id'].unique() #This puts each participant in a separate column
trials = range(df['trial_id'].max() + 1)

#Recode response keys
df["key"] = df["key"].map({1: "a", 2: "l"})

# Generate individual prompts for each participant
all_prompts = []

#Define response options/choices
choices = ("a", "l")  # fixed keys

for participant in participants:
    df_participant = df[df['participant_id'] == participant]

    if df_participant.empty:
        continue  # safety

    participant = participant.item()
    age = df_participant['age'].iloc[0].item()

    rt_list = []

    prompt = f"""In this study you will be shown various stimuli on the screen. Your task is to determine whether each one is a real Italian word or not.\n 
If you think it is a real Italian word, press the {choices[0]} key on your keyboard. If you think it is not a real Italian word, press the {choices[1]} key.\n
Ignore the colour of the stimulus and focus on whether or not the word exists in Italian.\n"""

    for _, row in df_participant.iterrows():
        word = row['stimuli']
        response = row['key']

        prompt += f'The word "{word}" appears on the screen. You press <<{response}>>.\n'
        rt_list.append(row['rt'])

    all_prompts.append({
        'text': prompt,
        'experiment': 'Saban_ItalianLDT-Exp2',
        'participant_id': participant,
        'age': age,
        'rt': rt_list,
    })

#Save all prompts to JSONL file
with jsonlines.open(path, mode='w') as writer:
    writer.write_all(all_prompts)