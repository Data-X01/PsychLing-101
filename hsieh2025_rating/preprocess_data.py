# Preprocessing data of hsieh2025_rating

# Load Libraries
import pandas as pd

# Read the raw data
df = pd.read_csv("/Users/cyhsieh/PsychLing-101/hsieh2025_rating/original_data/meaningfulness_rating.csv")

# Rename varaibles based on the codebook
rename_map = {
    "participant": "participant_id",
    "item": "stimulus",
    "num": "trial_id",
    "rating": "response"
}

df_cleaned = df.rename(columns=rename_map)

# Export the cleaned file
df_cleaned.to_csv("/Users/cyhsieh/PsychLing-101/hsieh2025_rating/processed_data/exp1.csv", index=False)
