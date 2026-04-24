import os
import zipfile
from pathlib import Path
import pandas as pd
import jsonlines


INSTRUCTIONS = (
    "¡Hola! En este test verás 100 secuencias de letras, algunas de las cuales son "
    "palabras existentes en español y otras son pseudopalabras inventadas. "
    "Indica para cada secuencia de letras si es una palabra que conoces o no "
    "presionando la tecla F o J.\n"
    "J: SÍ, conozco esta palabra\n"
    "F: NO, no conozco esta palabra\n"
    "¡Consejo! No digas sí a palabras que no conoces, porque las respuestas afirmativas "
    "a pseudopalabras se penalizan fuertemente.\n\n"
)


def generate_prompts(base_dir: Path) -> None:
    processed_path = base_dir / "processed_data" / "exp1.csv"
    df = pd.read_csv(processed_path)

    df = df.sort_values(by=["participant_id", "trial_order"])

    all_prompts = []

    for participant_id, participant_df in df.groupby("participant_id"):
        first_row = participant_df.iloc[0]

        def get(col):
            val = first_row.get(col)
            return None if pd.isna(val) else val

        prompt = INSTRUCTIONS
        rt_list = []

        for i, (_, row) in enumerate(participant_df.iterrows(), start=1):
            stimulus = row["stimulus"]
            condition = row["condition"]
            accuracy = row["accuracy"]
            rt = row["rt"]

            if pd.notna(accuracy) and accuracy == 1:
                response = "SÍ" if condition == "W" else "NO"
            elif pd.notna(accuracy) and accuracy == 0:
                response = "NO" if condition == "W" else "SÍ"
            else:
                response = "NA"

            feedback = "Correcto." if (pd.notna(accuracy) and accuracy == 1) else "Incorrecto."

            prompt += (
                f"Ensayo {i}: La secuencia de letras es '{stimulus}'. "
                f"Presionas <<{response}>>. {feedback}\n"
            )

            rt_list.append(rt if pd.notna(rt) else None)

        entry = {
            "text": prompt,
            "experiment": "aguasvivas2018_spalex",
            "participant_id": int(participant_id),
            "age": int(get("age")) if get("age") is not None else None,
            "gender": get("gender"),
            "education": get("education"),
            "best_foreign_language": get("best_foreign_language"),
            "num_foreign_languages": int(get("num_foreign_languages")) if get("num_foreign_languages") is not None else None,
            "country_of_birth": get("country_of_birth"),
            "rt": rt_list,
        }

        all_prompts.append(entry)

    jsonl_path = base_dir / "prompts.jsonl"
    with jsonlines.open(jsonl_path, "w") as writer:
        writer.write_all(all_prompts)


    zip_path = base_dir / "prompts.jsonl.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(jsonl_path, "prompts.jsonl")

    print(f"Generated {len(all_prompts)} prompts -> {zip_path}")


if __name__ == "__main__":
    generate_prompts(Path(__file__).parent.resolve())