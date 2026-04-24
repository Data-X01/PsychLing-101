import zipfile
import jsonlines
import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.resolve()

MAX_CHARS = 50_000

INSTRUCTION = (
    "You will read a story word-by-word; press SPACE to reveal the next word. "
    "Try to read naturally. "
    "Reaction times are recorded.\n\n"
)


def build_prompts(df: pd.DataFrame) -> list[dict]:
    all_prompts = []

    for (pid, item), df_s in df.groupby(["participant_id", "item"]):
        df_s = df_s.sort_values("word_position")
        comp = int(df_s["comprehension_correct"].iloc[0])

        story_text = f"Story {int(item)}:\n"
        for _, row in df_s.iterrows():
            story_text += f"  Word {int(row['word_position'])}: '{row['word']}' <<{int(row['rt'])}>> ms\n"
        story_text += f"  Comprehension: {comp}/6 correct\n"

        prompt = INSTRUCTION + story_text

        if len(prompt) > MAX_CHARS:
            cut = prompt[:MAX_CHARS].rfind("\n")
            prompt = prompt[:cut + 1]

        entry = {
            "text": prompt,
            "experiment": "futrell2021_corpus/self_paced_reading",
            "participant_id": int(pid),
            "item": int(item),
            "comprehension_correct": comp,
            "rt": df_s["rt"].tolist(),
        }
        all_prompts.append(entry)

    return all_prompts


df = pd.read_csv(base_dir / "processed_data" / "exp1.csv")
all_prompts = build_prompts(df)

jsonl_path = base_dir / "prompts.jsonl"
with jsonlines.open(jsonl_path, "w") as writer:
    writer.write_all(all_prompts)

zip_path = base_dir / "prompts.jsonl.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(jsonl_path, "prompts.jsonl")
jsonl_path.unlink()

n_participants = df["participant_id"].nunique()
print(f"prompts.jsonl.zip: {len(all_prompts)} entries "
      f"({n_participants} participants × up to 10 stories)")
