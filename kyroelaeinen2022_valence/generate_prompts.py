import jsonlines
import pandas as pd
import os

#### Read data ####
script_dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(script_dir, "processed_data/exp1.csv")
df = pd.read_csv(file)

# Group the data by participant
groups = df.groupby("participant_id")

all_prompts = []

# Process each experimental session
for participant_id, df_part in groups:
    # Sort trials by session then by trial number
    df_part = df_part.sort_values(by=["session_no", "trial_id"])

    # Global instructions (reconstructed from information from manuscript (see below))

    # The instructions informed the participant that the purpose of the study was to investigate emotion. The instructions asked participants to “respond to different types of words, by providing a rating on a scale of 1 (unhappy) to 9 (happy) of how you felt while reading each word. If you feel completely neutral you should rate a 5”.

    # In case the word was unknown to them, they were instructed to press the letter ‘n’.

    instructions = (
        "The purpose of this study is to investigate emotion. You will have to respond to different types of words, by providing a rating on a scale of 1 (unhappy) to 9 (happy) of how you felt while reading each word. If you feel completely neutral you should rate a 5. In case the word is unknown to you, press the letter 'n'."
    )

    # Start building the prompt text
    prompt_text = instructions + "\n\n"

    RTs_per_session = []
    age = int(df_part["age"].unique()[0])
    gender = df_part["gender"].unique()[0]
    education = df_part["education"].unique()[0]
    country_of_birth = df_part["country_of_birth"].unique()[0]
    country_of_residence = df_part["country_of_residence"].unique()[0]
    number_of_sessions = int(df_part["session_no"].max()+1)
    first_language = df_part["first_language"].unique()[0]

    sessions = sorted(df_part["session_no"].unique())

    for session in sessions:
        df_session = df_part[df_part["session_no"] == session]

        prompt_text += f"Session {int(session+1)}:\n"

        # Iterate over trials in the block
        for i, (_, row) in enumerate(df_part.iterrows()):
            trial_num = int(row["trial_id"])+1

            if pd.isna(row["response"]):
                action = "You press <<n>>."
            else:
                action = f"You answer <<{int(row["response"])}>>."

            # trial input in NL
            trial_line = (
                f"Trial {trial_num}: You see '{row["stimulus"]}'. {action}\n"
            )

            prompt_text += trial_line

            rt = float(row["rt"])
            RTs_per_session.append(rt)
    
    prompt_text += "\n"
            
    prompt_text += "End of session.\n"

    # Create the prompt dictionary
    prompt_dict = {
        "text": prompt_text,
        "experiment": "kyroelaeinen2022_valence_exp1",
        "participant_id": participant_id,
        "rt": RTs_per_session,
        "age": age,
        "gender": gender,
        "education": education,
        "first_language": first_language,
        "country_of_birth": country_of_birth,
        "country_of_residence": country_of_residence,
        "number_of_sessions": number_of_sessions
    }
    all_prompts.append(prompt_dict)

output_file = os.path.join(script_dir, "prompts.jsonl")
with jsonlines.open(output_file, mode='w') as writer:
    writer.write_all(all_prompts)

print(f"Created {len(all_prompts)} prompt(s) in {output_file}.")