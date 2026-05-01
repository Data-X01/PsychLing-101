import pandas as pd
import jsonlines
import random
import string
import zipfile


# Randomize choice options: function to draw n random letters from the alphabet without replacement
def random_letters(n):
    return ''.join(random.sample(string.ascii_uppercase, n))


# load data
df = pd.read_csv('processed_data/exp1.csv')
df['response'] = df['response'].astype(str)

# Sort dataframe by participant ID and trial order
df = df.sort_values(by=['participant_id', 'trial_order'])

# Remap participant IDs to sequential integers starting from 1
df['participant_id'] = df['participant_id'].map({p: i+1 for i, p in enumerate(df.participant_id.unique())})


# Get unique participants and trial indices
participants = df['participant_id'].unique()
trials = range(df['trial_order'].max() + 1)



# Generate individual prompts for each participant
all_prompts = []
for participant_id in participants:
    # Get data for current participant
    df_participant_id = df[df['participant_id'] == participant_id].copy()
    participant_id = participant_id.item()
    rt_list = []

    # generate two choice options
    choices = random_letters(2)

    # Update response column using loc
    df_participant_id.loc[df_participant_id["response"] == "1.0", "response"] = choices[0]
    df_participant_id.loc[df_participant_id["response"] == "3.0", "response"] = choices[1]


    # instruction text
    prompt = 'Na ekranu će biti izlagani nizovi slova u formi reči. Neki od njih će zaista biti reči vašeg jezika, dok će neki drugi samo ličiti na reči.\n'\
    'Vaš zadatak će biti da, za svaki prikazani niz, prepoznate da li predstavlja reč vašeg jezika, odnosno da li za vas nosi značenje kakvo nose reči.\n'\
        'Ukoliko smatrate da prikazani niz predstavlja reč vašeg jezika, pritisnite ' + choices[0] + ' a pritisnite ' + choices[1] + ' ukoliko vam prikazani niz samo liči na reč, ali nema značenje, odnosno ukoliko smatrate da je prikazani niz pseudoreč.\n'\
        'Obratite pažnju na to da reči mogu biti prikazane u različitim glagolskim oblicima.\n'\
        'Trudite se da radite što brže i što tačnije, ali ništa od ta dva po svaku cenu.\n'\
        'Da li je ovo reč vašeg jezika?\n'\
        'Pritisnite ' + choices[0] + ' ako je reč, a ' + choices[1] + ' ako je pseudoreč.\n'


    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant_id.loc[df_participant_id['trial_order'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            word = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            accuracy = df_trial['accuracy'].iloc[0]
            if pd.isna(df_trial['response'].iloc[0]) or response.strip() == '':
                datapoint = f'{word}. You press nothing.\n'
            else:
                feedback = 'Correct.' if accuracy == 1 else 'Incorrect.'
                datapoint = f'{word}. You press <<{response}>>. {feedback}\n'
            prompt += datapoint
            # reaction time
            rt = df_trial['rt'].iloc[0].item()
            rt_list.append(rt)

    prompt += '\n'
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'FilipovicDurdevicMilin2019_adjective_forms_VLD',
        'participant_id': participant_id,
        'rt': rt_list
    })

# Save all prompts to JSONL file
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)


with zipfile.ZipFile('prompts.jsonl.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('prompts.jsonl')
