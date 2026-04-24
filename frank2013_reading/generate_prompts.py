import random
import string
import zipfile
import jsonlines
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.resolve()

MAX_CHARS = 50_000

SPR_INSTRUCTION = (
    "You will read each sentence word-by-word; press SPACE to reveal the next word. "
    "Try to read naturally. "
    "After some sentences, a yes/no comprehension question will be shown. "
    "Press '{yes_key}' for YES and '{no_key}' for NO.\n\n"
    "We will measure response times.\n\n"
)

ET_INSTRUCTION = (
    "You will read each sentence displayed on a screen. "
    "Your eye movements are tracked as you read naturally. "
    "After some sentences, a yes/no comprehension question will be shown. "
    "Press '{yes_key}' for YES and '{no_key}' for NO.\n\n"
    "We will measure fixation durations.\n\n"
)


def build_prompts(df: pd.DataFrame, instruction: str, exp_name: str) -> list[dict]:
    df = df.copy()
    id_map = {p: i + 1 for i, p in enumerate(sorted(df["participant_id"].unique()))}
    df["participant_id"] = df["participant_id"].map(id_map)

    all_prompts = []
    for pid, df_p in df.groupby("participant_id"):
        age = float(df_p["age"].iloc[0])
        gender = df_p["gender"].iloc[0]
        first_language = df_p["first_language"].iloc[0]
        rt_list = []

        # Randomly assign J/F key mapping per participant
        yes_key, no_key = random.sample(string.ascii_lowercase, 2)

        prompt = instruction.format(yes_key=yes_key, no_key=no_key)

        for trial_num, (_, df_sent) in enumerate(df_p.groupby("trial_order", sort=True), start=1):
            df_sent = df_sent.sort_values("word_position")
            trial_text = f"Trial {trial_num}:\n"

            trial_rt = []
            for _, row in df_sent.iterrows():
                rt_val = row["rt"]
                word_num = int(row["word_position"])
                if pd.isna(rt_val):
                    trial_text += f"  Word {word_num}: '{row['word']}'  <<not fixated>>\n"
                else:
                    rt_int = int(rt_val)
                    trial_text += f"  Word {word_num}: '{row['word']}'  <<{rt_int}>> ms\n"
                    trial_rt.append(rt_int)

            question = df_sent["question"].iloc[0]
            response = df_sent["response"].iloc[0]
            if pd.notna(question) and pd.notna(response):
                key = yes_key if response == "y" else no_key
                trial_text += f"  Question: '{question}' You answer <<{key}>>.\n"

            trial_text += "\n"

            if len(prompt) + len(trial_text) > MAX_CHARS:
                break

            prompt += trial_text
            rt_list.extend(trial_rt)

        entry = {
            "text": prompt,
            "experiment": exp_name,
            "participant_id": int(pid),
            "age": age,
            "rt": rt_list,
        }
        if pd.notna(gender):
            entry["gender"] = gender
        if pd.notna(first_language):
            entry["first_language"] = first_language
        all_prompts.append(entry)

    return all_prompts


df1 = pd.read_csv(base_dir / "processed_data" / "exp1.csv")
df2 = pd.read_csv(base_dir / "processed_data" / "exp2.csv")

prompts_spr = build_prompts(df1, SPR_INSTRUCTION, "frank2013_reading/self_paced_reading")
prompts_et = build_prompts(df2, ET_INSTRUCTION, "frank2013_reading/eye_tracking")

all_prompts = prompts_spr + prompts_et

jsonl_path = base_dir / "prompts.jsonl"
with jsonlines.open(jsonl_path, "w") as writer:
    writer.write_all(all_prompts)

zip_path = base_dir / "prompts.jsonl.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(jsonl_path, "prompts.jsonl")
jsonl_path.unlink()

print(f"prompts.jsonl.zip: {len(all_prompts)} participants total "
      f"({len(prompts_spr)} SPR, {len(prompts_et)} ET)")
