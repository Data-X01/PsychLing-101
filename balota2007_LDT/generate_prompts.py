import jsonlines
import pandas as pd
import numpy as np
import os

SEED = 42
_rng = np.random.RandomState(SEED)

def randomized_choice_options(num_choices):
    """Return a random selection of uppercase letters as choice labels."""
    choice_options = list(map(chr, range(65, 91)))
    return _rng.choice(choice_options, num_choices, replace=False)

#### Read data ####
script_dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(script_dir, "processed_data/exp1.csv")
df = pd.read_csv(file)

# Group the data by participant
groups = df.groupby("participant_id")

all_prompts = []

# Process each experimental session
for participant_id, df_participant in groups:
    # Sort trials by session then by trial number
    df_participant = df_participant.sort_values(by=["session_no", "trial_id"])    

    # Randomize the button names for this participant
    choice_options = randomized_choice_options(
        num_choices=2
    )

    # Global instructions (freely written)
    instructions = (
        f"In this task, you will see either a word or a nonword. Please press <<{choice_options[0]}>> when a word appears and <<{choice_options[1]}>> when a nonwords appears. Respond within 4 seconds."
    )

    # subject-level meta data
    university = df_participant["university"].iloc[0]
    day_of_birth = df_participant["day_of_birth"].iloc[0]
    age = int(df_participant["age"].iloc[0])
    gender = df_participant["gender"].iloc[0]
    years_of_education = int(df_participant["years_of_education"].iloc[0])
    years_of_education_corrected = int(df_participant["years_of_education_corrected"].iloc[0])
    first_language = df_participant["first_language"].iloc[0]
    meq_score = float(df_participant["meq_score"].iloc[0])
    shipley_numCorrect = float(df_participant["shipley_numCorrect"].iloc[0])
    shipley_rawScore = float(df_participant["shipley_rawScore"].iloc[0])
    shipley_vocabAge = float(df_participant["shipley_vocabAge"].iloc[0])
    present_health_score = float(df_participant["present_health_score"].iloc[0])
    past_health_score = float(df_participant["past_health_score"].iloc[0])
    vision_score = float(df_participant["vision_score"].iloc[0])
    hearing_score = float(df_participant["hearing_score"].iloc[0])
    start_endblock = df_participant["start_endblock"].iloc[0]

    # Group the data by session
    sessions = df_participant.groupby("session_no")

    for session_no, df_session in sessions:

        start_session = df_session["start_time"].iloc[0]

        # Create rest count to track number of given rests
        rest_count = 0

        # Split prompts into batches of max. 1,000 trials (2 batches per session)
        # Reset index for df_session
        df_session = df_session.reset_index(drop=True)

        # Create batches
        batch_size = 1000
        df_session["batch"] = df_session.index // batch_size
        # Get the unique batch no.
        batches = sorted(df_session["batch"].unique())

        for batch in batches:
            df_batch = df_session[df_session["batch"] == batch]

            # trial-level meta data
            RTs_per_batch = []
            accuracy_per_batch = []

            # Start building the prompt text
            prompt_text = instructions + "\n\n"

            prompt_text += (
            f"Session {int(session_no+1)}, Batch {int(batch+1)}:\n\n"
            )

            # Iterate over trials in the batch
            for i, (_, row) in enumerate(df_batch.iterrows()):
                trial_num = i+1+batch_size*batch

                # reconstruct pressed button
                # choice_options[0] = word; choice_options[1] = nonword
                # Logic: if accuracy == 1 and lexicality == 1 or accuracy == 0 and lexicality == 0, word was pressed, else nonword was pressed
                if (row["accuracy"] == 1 and row["lexicality"] == 1) or (row["accuracy"] == 0 and row["lexicality"] == 0):
                    chosen_button = choice_options[0]
                else:
                    chosen_button = choice_options[1]

                # trial input in NL
                trial_line = f"Trial {trial_num}: You see '{row['stimulus']}'. You press <<{chosen_button}>>."

                if row["accuracy"] == 0:
                    trial_line += " Incorrect!"

                prompt_text += trial_line + "\n"

                rt = float(row["rt"])
                RTs_per_batch.append(rt)

                accuracy = int(row["accuracy"])
                accuracy_per_batch.append(accuracy)

                # Rest after every 250 trials; every third rest was longer
                if trial_num % 250 == 0 and trial_num != max(df_session["trial_id"])+1:
                    rest_count += 1

                    prompt_text += "\n"

                    block_accuracy = pd.Series(accuracy_per_batch[-250:]).mean()
                    block_rt = pd.Series(RTs_per_batch[-250:]).mean()

                    if block_accuracy < .8:
                        feedback_accuracy = "Please increase your level of accuracy"
                    else:
                        feedback_accuracy = "Please maintain this level of accuracy"

                    if block_rt > 1000:
                        feedback_rt = "Please decrease your response time"
                    else:
                        feedback_rt = "Please maintain this reaction time"

                    if rest_count % 3 == 0:
                        prompt_text += (
                            "3 minute break. Please use this time to get a drink, stretch, or walk around.\n"+
                            f"Your accuracy in the last 250 trials was {int(block_accuracy*100)} %. {feedback_accuracy}.\n"+
                            f"Your average reaction time in the last 250 trials was {int(block_rt)} ms. {feedback_rt}."
                        )
                    else:
                        prompt_text += (
                            "1 minute break.\n"+
                            f"Your accuracy in the last 250 trials was {int(block_accuracy*100)} %. {feedback_accuracy}.\n"+
                            f"Your average reaction time in the last 250 trials was {int(block_rt)} ms. {feedback_rt}."
                        )

                    prompt_text += "\n\n"

            prompt_text += "End of batch.\n\n"

            # Create the prompt dictionary
            prompt_dict = {
                "text": prompt_text,
                "experiment": "balota2007_LDT_exp1",
                "participant_id": participant_id,
                "session_no": int(session_no+1),
                "batch_no": int(batch+1),
                "rt": RTs_per_batch,
                "accuracy": accuracy_per_batch,
                "age": age,
                "day_of_birth": day_of_birth,        
                "gender": gender,
                "years_of_education": years_of_education,
                "years_of_education_corrected": years_of_education_corrected,
                "first_language": first_language,
                "meq_score": meq_score,
                "shipley_numCorrect": shipley_numCorrect,
                "shipley_rawScore": shipley_rawScore,
                "shipley_vocabAge": shipley_vocabAge,
                "present_health_score": present_health_score,
                "past_health_score": past_health_score,
                "vision_score": vision_score,
                "hearing_score": hearing_score,
                "university": university,
                "start_time": start_session,
                "start_endblock": start_endblock
            }
            all_prompts.append(prompt_dict)

output_file = os.path.join(script_dir, "prompts.jsonl")
with jsonlines.open(output_file, mode='w') as writer:
    writer.write_all(all_prompts)

print(f"Created {len(all_prompts)} prompt(s) in {output_file}.")