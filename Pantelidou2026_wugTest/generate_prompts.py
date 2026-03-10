import pandas as pd
import jsonlines

# --------------------------
# Load CSV files
# --------------------------

exp1 = pd.read_csv("processed_data/exp1.csv", encoding="utf-8", engine="python", on_bad_lines="skip")
exp2 = pd.read_csv("processed_data/exp2.csv", encoding="utf-8", engine="python", on_bad_lines="skip")
exp3 = pd.read_csv("processed_data/exp3.csv", encoding="utf-8", engine="python", on_bad_lines="skip")
exp4 = pd.read_csv("processed_data/exp4.csv", encoding="utf-8", engine="python", on_bad_lines="skip")

# --------------------------
# Instruction blocks
# --------------------------

instruction_block1_exp1 = (
    "Benvingut/da!\n"
    "La teva tasca és completar les oracions omplint els espais en blanc amb la paraula correcta.\n"
    "Si us plau, llegeix cada oració amb atenció i escriu la teva resposta a la caixa de text.\n"
    "Hi ha 30 oracions. Pren-te el teu temps, però intenta respondre amb la màxima precisió possible.\n"
    "Atenció! Un cop premi's 'Següent', no podràs tornar a l'oració anterior.\n"
    "Bona sort i gràcies per la teva participació!\n"
)

instruction_block2_exp1 = (
    "Per completar l'enquesta, premeu el botó 'Finalitzar'\n"
    "Gràcies per la teva participació!\n"
)

instruction_block1_exp2 = (
    "Καλώς ήρθατε!\n"
    "Στόχος είναι να ολοκληρώσετε τις προτάσεις συμπληρώνοντας τα κενά με τη σωστή λέξη.\n"
    "Παρακαλώ διαβάστε προσεκτικά κάθε πρόταση και πληκτρολογήστε την απάντησή σας στο πλαίσιο κειμένου.\n"
    "Υπάρχουν 30 προτάσεις. Πάρτε τον χρόνο σας, αλλά προσπαθήστε να απαντήσετε με όσο το δυνατόν μεγαλύτερη ακρίβεια.\n"
    "Προσοχή! Μόλις πατήσετε 'Επόμενο', δεν θα μπορείτε να επιστρέψετε στην προηγούμενη πρόταση.\n"
    "Καλή τύχη και ευχαριστούμε για τη συμμετοχή σας!\n"
)

instruction_block2_exp2 = (
    "Για να ολοκληρώσετε την έρευνα, πατήστε το κουμπί «Ολοκλήρωση».\n"
    "Ευχαριστούμε για τη συμμετοχή σας!\n"
)

instruction_block1_exp3 = (
    "Welcome!\n"
    "Your task is to complete the sentences by filling in the blanks with the correct word.\n"
    "Please read each sentence carefully and type your answer in the text box.\n"
    "Take your time, but try to respond as accurately as possible.\n"
    "Attention! Once you press 'Next', you cannot go back to the previous sentence.\n"
    "Good luck, and thank you for your participation!\n"
)

instruction_block2_exp3 = (
    "To complete the survey, press the 'Finish' button.\n"
    "Thank you for participating!\n"
)

instruction_block1_exp4 = (
    "¡Bienvenido/a!\n"
    "Tu tarea es completar las oraciones llenando los espacios en blanco con la palabra correcta.\n"
    "Por favor, lee cada oración con atención y escribe tu respuesta en el cuadro de texto.\n"
    "Hay 30 oraciones. Tómate tu tiempo, pero intenta responder con la mayor precisión posible.\n"
    "¡Atención! Una vez que presiones 'Siguiente', no podrás volver a la oración anterior.\n"
    "¡Buena suerte y gracias por tu participación!\n"
)

instruction_block2_exp4 = (
    "Para completar la encuesta, pulse el botón 'Completar'.\n"
    "¡Gracias por tu participación!\n"
)

# --------------------------
# Prompt generator
# --------------------------

all_prompts = []

def generate_prompts(exp_df, instruction_block1, instruction_block2, experiment_name, max_tokens=32000):

    # Clean IDs and numeric columns
    if "participant_id" in exp_df.columns:
        exp_df["participant_id"] = (
            exp_df["participant_id"]
            .astype(str)
            .str.strip()
        )
        exp_df["participant_id"] = pd.to_numeric(exp_df["participant_id"], errors="coerce")

    if "trial_id" in exp_df.columns:
        exp_df["trial_id"] = pd.to_numeric(exp_df["trial_id"], errors="coerce")

    if "age" in exp_df.columns:
        exp_df["age"] = pd.to_numeric(exp_df["age"], errors="coerce")

    participants = exp_df["participant_id"].dropna().unique()

    print(f"{experiment_name}: {len(participants)} participants")

    for participant in participants:

        exp_participant = exp_df[exp_df["participant_id"] == participant]

        # Convert age to integer
        age = None
        if "age" in exp_participant.columns:
            age_val = exp_participant["age"].iloc[0]
            if pd.notna(age_val):
                age = int(age_val)

        individual_prompt = instruction_block1
        trial_accuracies = []

        trials = exp_participant["trial_id"].dropna().unique()

        for trial in trials:

            exp_trial = exp_participant.loc[exp_participant["trial_id"] == trial]

            if not exp_trial.empty:

                stimulus = exp_trial["stimulus"].iloc[0]
                response = exp_trial["response"].iloc[0]

                trial_instruction = ""
                if "trial_instruction" in exp_trial.columns:
                    trial_instruction = exp_trial["trial_instruction"].iloc[0]

                # Get accuracy
                # Get accuracy
                accuracy = None
                if "accuracy" in exp_trial.columns:
                    acc_val = exp_trial["accuracy"].iloc[0]
                    if pd.notna(acc_val):
                        accuracy = int(acc_val)

                # Add accuracy to list
                trial_accuracies.append(accuracy)

                trial_index = int(exp_trial["trial_id"].iloc[0])

                # Build datapoint string WITHOUT accuracy
                if trial_index == 21:
                    datapoint = f"{instruction_block2} {stimulus} {trial_instruction} You enter <<{response}>>.\n"
                else:
                    datapoint = f"{stimulus} {trial_instruction} You enter <<{response}>>.\n"
                individual_prompt += datapoint

                if len(individual_prompt) > max_tokens:
                    individual_prompt = individual_prompt[:max_tokens]
                    break

        all_prompts.append({
            "participant": int(participant),
            "text": individual_prompt,
            "accuracy": trial_accuracies,  # new field
            "experiment": experiment_name,
            "age": age
        })

# --------------------------
# Run all experiments
# --------------------------

generate_prompts(exp1, instruction_block1_exp1, instruction_block2_exp1, "experiment1")
generate_prompts(exp2, instruction_block1_exp2, instruction_block2_exp2, "experiment2")
generate_prompts(exp3, instruction_block1_exp3, instruction_block2_exp3, "experiment3")
generate_prompts(exp4, instruction_block1_exp4, instruction_block2_exp4, "experiment4")


# --------------------------
# Save JSONL
# --------------------------

with jsonlines.open("prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)

print("Saved prompts.jsonl with", len(all_prompts), "participants.")

