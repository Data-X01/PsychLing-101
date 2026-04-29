import pandas as pd
import jsonlines
import random
import string
from pathlib import Path

#Define the path
path = Path("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Preparation of data/Experiment 1 - colour associates") / "prompts.jsonl"

#Load preprocessed files from Exp1 and Exp2
df1 = pd.read_csv("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Fixing the errors/processed_data/exp1.csv", sep=';')
df2 = pd.read_csv("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Fixing the errors/processed_data/exp2.csv", sep=';')

#Merge the two dataframes
df = pd.concat([df1, df2], ignore_index=True)

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

    prompt = f"""In questo studio vi verranno mostrati diversi stimoli sullo schermo. Il vostro compito è quello di determinare se si tratta di una parola italiana esistente o meno.\n 
Se pensate che sia una parola italiana esistente, premete il tasto {choices[0]}, mentre se pensate che non sia una parola italiana esistente, premete il tasto {choices[1]}.\n
Ignorate il colore dello stimolo e concentratevi sull'esistenza o meno della parola in italiano.\n"""

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
