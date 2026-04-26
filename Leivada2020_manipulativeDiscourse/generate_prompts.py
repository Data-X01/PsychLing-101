import pandas as pd
import json

df1 = pd.read_csv("processed_data/exp1.csv", quotechar='"', dtype=str)
df2 = pd.read_csv("processed_data/exp2.csv", quotechar='"', dtype=str)

# Assign experiment labels
df1['experiment'] = 'exp1'
df2['experiment'] = 'exp2'


# Combine them into a single DataFrame
df = pd.concat([df1, df2], ignore_index=True)

# Group by participant (if multiple rows per participant)
grouped = df.groupby('participant_id')

jsonl_lines = []

for participant_id, group in grouped:
    # Start building the text field
    text_parts = [
        "Instruction:\nRate how correct each sentence sounds.\nOptions: correct / neither correct nor wrong / wrong.\n"
    ]

    # Enumerate sentences
    for i, row in enumerate(group.itertuples(), start=1):
        # Capitalize the response to match format
        response = str(row.response).capitalize()
        text_parts.append(
            f"Sentence {i}:\n{row.stimulus}\nYour response: <<{response}>>"
        )

    # Combine all sentences into one string
    text_field = "\n\n".join(text_parts)

    # Build JSON object
    json_obj = {
        "participant": participant_id,
        "text": text_field,
        "experiment": group['experiment'].iloc[0],  # automatically pick exp1 or exp2
        "age": int(group['age'].iloc[0]),          # convert numpy int to Python int

    }

    # Convert to JSON string (single line)
    jsonl_lines.append(json.dumps(json_obj, ensure_ascii=False))

# Write to JSONL file
with open("prompts.jsonl", "w", encoding="utf-8") as f:
    for line in jsonl_lines:
        f.write(line + "\n")

print("JSONL file created successfully from both CSVs!")