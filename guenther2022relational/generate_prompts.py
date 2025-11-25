import pandas as pd
import jsonlines
from pathlib import Path

# load data
base_dir = Path(__file__).parent.resolve()
df = pd.read_csv(base_dir / "processed_data" / "exp1.csv")

# Sort dataframe by participant ID and trial order
df = df.sort_values(by=['participant_id', 'trial_id'])

# Remap participant IDs to sequential integers starting from 1
df['participant_id'] = df['participant_id'].map(
    {p: i + 1 for i, p in enumerate(df.participant_id.unique())}
)

# Get unique participants and trial indices
participants = df['participant_id'].unique()
trials = range(df['trial_id'].max() + 1)

# ---- Instructions (unchanged) ----
instruction = """
Instructions\n
\n
In the following study, you will see 55 different expressions such as face room. Please indicate, for each expression, what you think it means.\n
More specifically, your task is to choose, for each expression, one of sixteen different relations connecting the two words. You can use the following table to get familiar with these relations and some examples:\n
\n
Relation\tExample\tExample with relation\n
word2 ABOUT word1\tnewsflash\tflash ABOUT news\n
word2 BY word1\thandclap\tclap BY hand(s)\n
word2 CAUSES word1\tjoyride\tride CAUSES joy\n
word2 CAUSED BY word1\tsunbeam\tbeam CAUSED BY sun\n
word2 DERIVED FROM word1\tseafood\tfood DERIVED FROM sea\n
word2 DURING word1\tnightlife\tlife DURING night\n
word2 FOR word1\tmealtime\ttime FOR meal\n
word2 HAS word1\tbookstore\tstore HAS book(s)\n
word1 HAS word2\tdoorframe\tdoor HAS frame\n
word2 LOCATION IS word1\tfarmyard\tyard LOCATION IS farm\n
word1 LOCATION IS word2\tneckline\tneck LOCATION IS line\n
word2 MADE OF word1\tsnowman\tman MADE OF snow\n
word2 MAKES word1\thoneybee\tbee MAKES honey\n
word2 IS word1\tgirlfriend\tfriend IS girl\n
word2 USES word1\tsteamboat\tboat USES steam\n
word2 USED BY word1\ttwitchcraft\tcraft USED BY witch(es)\n
\n
For example, you could interpret face room as, among others, room HAS face (a magical room with a large living face on its wall), or room FOR face (the make-up artist room at a film set). Please only select one possible interpretation for each expression - the one that seems most likely to you. Of course, there are no correct or wrong answers in this task.\n
If you want to have a look at this table during the study, you can open it in a new tab using the following link:\n
Reference Sheet\n
You will not be able to return to earlier answers.\n
\n
### Reference sheet\n
\n
Reference Sheet\n
\n
Relation\tExample\tExample with relation\n
word2 ABOUT word1\tnewsflash\tflash ABOUT news\n
word2 BY word1\thandclap\tclap BY hand(s)\n
word2 CAUSES word1\tjoyride\tride CAUSES joy\n
word2 CAUSED BY word1\tsunbeam\tbeam CAUSED BY sun\n
word2 DERIVED FROM word1\tseafood\tfood DERIVED FROM sea\n
word2 DURING word1\tnightlife\tlife DURING night\n
word2 FOR word1\tmealtime\ttime FOR meal\n
word2 HAS word1\tbookstore\tstore HAS book(s)\n
word1 HAS word2\tdoorframe\tdoor HAS frame\n
word2 LOCATION IS word1\tfarmyard\tyard LOCATION IS farm\n
word1 LOCATION IS word2\tneckline\tneck LOCATION IS line\n
word2 MADE OF word1\tsnowman\tman MADE OF snow\n
word2 MAKES word1\thoneybee\tbee MAKES honey\n
word2 IS word1\tgirlfriend\tfriend IS girl\n
word2 USES word1\tsteamboat\tboat USES steam\n
word2 USED BY word1\ttwitchcraft\tcraft USED BY witch(es)\n
\n
"""

def build_response_options(word1: str, word2: str) -> str:
    """Return a text block listing all 16 relations for this word pair."""
    options = [
        f'You have the following options for "{word1} {word2}":',
        f'{word2} ABOUT {word1}',
        f'{word2} BY {word1}',
        f'{word2} CAUSES {word1}',
        f'{word2} CAUSED BY {word1}',
        f'{word2} DERIVED FROM {word1};',
        f'{word2} DURING {word1};',
        f'{word2} FOR {word1};',
        f'{word2} HAS {word1};',
        f'{word1} HAS {word2};',
        f'{word2} LOCATION IS {word1};',
        f'{word1} LOCATION IS {word2};',
        f'{word2} MADE OF {word1};',
        f'{word2} MAKES {word1};',
        f'{word2} IS {word1};',
        f'{word2} USES {word1};',
        f'{word2} USED BY {word1};',
    ]
    return "\n".join(options)

# Generate individual prompts for each participant
all_prompts = []
for participant in participants:
    df_participant = df[df['participant_id'] == participant]
    participant = participant.item()
    age = df_participant['age'].iloc[0].item()
    
    # Start with instruction text
    prompt = instruction
    
    # Add each trial's word, all options, and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_id'] == trial]
        if not df_trial.empty:
            word = df_trial['stimulus'].iloc[0]
            parts = word.split(" ")
            if len(parts) != 2:
                # fallback: skip or handle differently if stimulus isn't exactly two words
                continue
            word1, word2 = parts[0], parts[1]
            response = df_trial['response'].iloc[0]
            
            options_text = build_response_options(word1, word2)
            datapoint = (
                f'\nYou see the following expression on the screen: "{word}"\n'
                f'{options_text}\n'
                f'You choose <<{response}>>.\n'
            )
            prompt += datapoint
    
    prompt += '\n'
    
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2022Relational',
        'participant_id': participant,
        'age': age
    })

# Save all prompts to JSONL file
with jsonlines.open(base_dir / 'prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)