import jsonlines
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.resolve()

SPR_INSTRUCTION = (
    "You will read each sentence word-by-word; press SPACE to reveal the next word. "
    "Try to read naturally. "
    "After some sentences, a yes/no comprehension question will be shown.\n\n"
)

ET_INSTRUCTION = (
    "You will read each sentence displayed on a screen. "
    "Your eye movements are tracked as you read naturally. "
    "After some sentences, a yes/no comprehension question will be shown.\n\n"
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
        prompt = instruction

        for trial_num, (_, df_sent) in enumerate(df_p.groupby("trial_order", sort=True), start=1):
            df_sent = df_sent.sort_values("word_position")
            prompt += f"Trial {trial_num}:\n"

            for _, row in df_sent.iterrows():
                rt_val = row["rt"]
                word_num = int(row["word_position"])
                if pd.isna(rt_val):
                    prompt += f"  Word {word_num}: '{row['word']}'  <<not fixated>>\n"
                else:
                    rt_int = int(rt_val)
                    prompt += f"  Word {word_num}: '{row['word']}'  <<{rt_int}>> ms\n"
                    rt_list.append(rt_int)

            question = df_sent["question"].iloc[0]
            response = df_sent["response"].iloc[0]
            if pd.notna(question) and pd.notna(response):
                prompt += f"  Question: '{question}' You answer <<{response}>>.\n"

            prompt += "\n"

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

with jsonlines.open(base_dir / "prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)

print(f"prompts.jsonl: {len(all_prompts)} participants total "
      f"({len(prompts_spr)} SPR, {len(prompts_et)} ET)")
