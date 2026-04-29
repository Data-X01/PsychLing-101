import pandas as pd
import jsonlines
import random
import string
import zipfile
import chardet

def random_letters(n):
    return ''.join(random.sample(string.ascii_uppercase, n))

with open('processed_data/exp1.csv', 'rb') as f:
    result = chardet.detect(f.read())
print(result)


# Load data
df = pd.read_csv('processed_data/exp1.csv', encoding='utf-8', encoding_errors='replace')
df['response'] = df['response'].astype(str)

# Sort dataframe by participant ID, phase_id, and trial order
df = df.sort_values(by=['participant_id', 'phase_id', 'trial_order'])

# Remap participant IDs to sequential integers starting from 1
df['participant_id'] = df['participant_id'].map(
    {p: i + 1 for i, p in enumerate(df['participant_id'].unique())}
)

participants = df['participant_id'].unique()

# Phase ID order: single-alphabet phase first, mixed-alphabet phase second
PHASE_ORDER = ['block_1_single_alph', 'block_2_mixed_alph']

all_prompts = []
for participant_id in participants:
    df_part = df[df['participant_id'] == participant_id].copy()
    participant_id = participant_id.item()
    rt_list = []

    # Generate two choice options
    choices = random_letters(2)

    # Remap button responses
    df_part.loc[df_part['response'] == '1', 'response'] = choices[0]
    df_part.loc[df_part['response'] == '3', 'response'] = choices[1]
    df_part.loc[df_part['response'] == 'c',   'response'] = choices[0]
    df_part.loc[df_part['response'] == 'm',   'response'] = choices[1]

    # Determine which script variant to use based on the participant's list
    participant_list = df_part['list'].iloc[0]
    use_R = participant_list in ('ALFA-3_R_a', 'ALFA-3_R_b')  # else C

    # Instruction texts
    prompt_R1 = (
        'Na ekranu će vam se prikazati niz slova, a vaš zadatak je da odgovorite da li je to reč ili nije reč.<br />'
        ' Ukoliko se na ekranu pojavi niz slova koji je reč, pritisnite taster ' + choices[0] + ',<br />'
        ' a ukoliko nije reč, pritisnite taster ' + choices[1] + '.<br />'
        'Reči se mogu javiti u različitim padežima.<br />'
        'Trudite se da radite što brže i što tačnije.'
    )
    prompt_C1 = (
        'На екрану ће вам се приказати низ слова, а ваш задатак је да одговорите да ли је то реч или није реч.<br />'
        'Уколико се на екрану појави низ слова који је реч, притисните тастер ' + choices[0] + ',<br />'
        ' а уколико није реч, притисните тастер ' + choices[1] + '.<br />'
        'Речи се могу јавити у различитим падежима.<br />'
        'Трудите се да радите што брже и што тачније.'
    )
    prompt_R2 = (
        'Vaš zadatak će biti potupno isti kao do sada, <br /><br />'
        's tim što će <br /><br />'
        'NEKE REČI I PSEUDOREČI BITI NAPISANE ĆIRILICOM, <br /><br />'
        'A NEKE LATINICOM. <br /><br />'
        'Ukoliko u bilo kom od ta dva pisma <br />reč može da se pročita tako da ima značenje, <br />odgovorite potvrdno. <br /><br />'
        ' Primeri potvrdnih odgovora: <br />НАНА (reč napisana ćirilicom), РАРА (reč napisana latinicom).  <br /><br />'
        ' Ukoliko ni u ćiriličnoj, ni u latiničnoj varijanti <br />reč ne može da se pročita kao reč vašeg jezika, <br />odgovorite odrično.<br /><br />'
        'Trudite se da budete što brži, ali i što tačniji u isto vreme.'
    )
    prompt_C2 = (
        'Ваш задатак ће бити потпуно исти као до сада, <br /><br />'
        'с тим што ће <br /><br />'
        'НЕКЕ РЕЧИ И ПСЕУДОРЕЧИ БИТИ НАПИСАНЕ ЋИРИЛИЦОМ, <br /><br />'
        'А НЕКЕ ЛАТИНИЦОМ. <br /><br />'
        'Уколико у било ком од та два писма <br />реч може да се прочита тако да има значење, <br />одговорите потврдно. <br /><br />'
        ' Примери потврдних одговора: <br />НАНА (реч написана ћирилицом), РАРА (реч написана латиницом). <br /><br />'
        'Уколико ни у ћириличној, ни у латиничној варијанти <br />реч не може да се прочита као реч Вашег језика, <br />одговорите одрично.<br /><br />'
        'Трудите се да будете што бржи, али и што тачнији у исто време.'
    )

    # Map each phase to its instruction
    phase_instructions = {
        'block_1_single_alph': prompt_R1 if use_R else prompt_C1,
        'block_2_mixed_alph':  prompt_R2 if use_R else prompt_C2,
    }

    prompt = ''

    # Iterate phases in defined order, then trials ordered by trial_order
    for phase_id in PHASE_ORDER:
        df_phase = df_part[df_part['phase_id'] == phase_id]
        if df_phase.empty:
            continue

        # Insert the phase instruction before the first trial of each phase
        prompt += phase_instructions[phase_id] + '\n\n'

        for trial in sorted(df_phase['trial_order'].unique()):
            df_trial = df_phase[df_phase['trial_order'] == trial]
            word     = df_trial['stimulus'].iloc[0]
            response = df_trial['response'].iloc[0]
            accuracy = df_trial['accuracy'].iloc[0]

            #if pd.isna(df_trial['response'].iloc[0]) or response.strip() == '':
            if response.strip() in ('', 'nan'):
                datapoint = f'{word}. You press nothing.\n'
            else:
                feedback  = 'Correct.' if accuracy == 1 else 'Incorrect.'
                datapoint = f'{word}. You press <<{response}>>. {feedback}\n'

            prompt += datapoint

            rt = df_trial['rt'].iloc[0].item()
            rt_list.append(rt)

        prompt += '\n'

    all_prompts.append({
        'text': prompt,
        'experiment': 'FilipovicDurdevicFeldman2024_bialphabeticVLD.csv',
        'participant_id': participant_id,
        'rt': rt_list
    })

# Save to JSONL and zip
with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)

with zipfile.ZipFile('prompts.jsonl.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('prompts.jsonl')