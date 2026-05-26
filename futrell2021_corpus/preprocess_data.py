import pandas as pd
from pathlib import Path

base_dir = Path(__file__).parent.resolve()
orig_dir = base_dir / "original_data"

df = pd.read_csv(orig_dir / "processed_RTs.tsv", sep="\t")

participants = sorted(df["WorkerId"].unique())
id_map = {p: i + 1 for i, p in enumerate(participants)}
df["participant_id"] = df["WorkerId"].map(id_map)

out = (
    df[["participant_id", "item", "zone", "word", "RT", "correct"]]
    .rename(columns={"zone": "word_position", "RT": "rt", "correct": "comprehension_correct"})
    .sort_values(["participant_id", "item", "word_position"])
    .reset_index(drop=True)
)

out.to_csv(base_dir / "processed_data" / "exp1.csv", index=False)
print(f"exp1.csv: {len(out):,} rows, {out['participant_id'].nunique()} participants, "
      f"{out['item'].nunique()} stories")
