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

# Generate individual prompts for participants with batching

participant_list = df['participant_id'].unique()
trial_num = range(df['trial_id'].max() + 1)
max_chars = 50000

for participant in participant_list:
    exp_participant = df[df['participant_id'] == participant]
    #############################
    # Randomise options per participant
    #############################
    keys = ['j', 'f']
    np.random.shuffle(keys)
    real_word_key = keys[0]
    fake_word_key = keys[1]
    # Participant-specific instruction
    instruction = (
        f"每次试验包括一个注视标记和一个刺激（真字或假字）。"
        f"首先，屏幕中央呈现注视标记500毫秒，120毫秒后呈现刺激。"
        f"如果你认为该刺激是真字，请按 {real_word_key} 键；"
        f"如果认为是假字，请按 {fake_word_key} 键。"
        f"虽然没有反应时间限制，但请尽可能快速并尽最大准确性作答。"
        f"如果你曾经见过或认识这些刺激，那么它很有可能是真字；"
        f"如果你没有见过，那么它很可能不是真字。\n"
    )
    batch_text = instruction
    batch_num = 1
    last_rt = None
    for trial in trial_num:
        exp_trial = exp_participant.loc[
            exp_participant['trial_id'] == trial
        ]
        if not exp_trial.empty:
            image = exp_trial['image_filename'].iloc[0]
            response = exp_trial['response'].iloc[0]
            trial_id = exp_trial['trial_id'].iloc[0]
            accuracy = exp_trial['accuracy'].iloc[0]
            rt = exp_trial['rt'].iloc[0]
            #############################
            # Convert response using participant mapping
            #############################
            if response == 'j':
                randomized_response = real_word_key
            elif response == 'f':
                randomized_response = fake_word_key
            else:
                randomized_response = response
            datapoint = (
                f'试次{trial_id}：{image}。'
                f'你按下了 <<{randomized_response}>> 键。'
                f'{accuracy}。'
                f'反应时间为 {rt} 毫秒。\n'
            )
            #############################
            # Batch by character length
            #############################
            if len(batch_text) + len(datapoint) > max_chars:
                all_prompts.append({
                    'text': batch_text,
                    'experiment': 'wang2025_lexicaldecision',
                    'participant_id': participant,
                    'batch': batch_num,
                    'rt': last_rt
                })
                batch_num += 1
                batch_text = instruction + datapoint
            else:
                batch_text += datapoint
            last_rt = rt
    # Save remaining text in final batch
    if batch_text != instruction:
        all_prompts.append({
            'text': batch_text,
            'experiment': 'wang2025_lexicaldecision',
            'participant_id': participant,
            'batch': batch_num,
            'rt': last_rt
        })

# Save all prompts to JSONL file
with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)