# Preprocessing raw data of wang2025_lexicaldecision

# Load Libraries
import pandas as pd
import numpy as np

# Read the raw data
df = pd.read_csv("/Users/cyhsieh/PsychLing-101/wang2025_lexicaldecision/original_data/fullresult.csv", encoding="utf-8", index_col=0)

# Create variable "trial_id"
df["trial_id"] = pd.factorize(df["item"])[0] + 1

# Map numeric values to strings in the variable "accuracy" 
df["accuracy"] = df["accuracy"].map({1: "Correct", 0: "Incorrect"})

# Create response based on "lexicality" and "accuracy"
conditions = [
    (df["lexicality"] == "character") & (df["accuracy"] == "Correct"),
    (df["lexicality"] == "pseudocharacter") & (df["accuracy"] == "Incorrect"),
    (df["lexicality"] == "pseudocharacter") & (df["accuracy"] == "Correct"),
    (df["lexicality"] == "character") & (df["accuracy"] == "Incorrect"),
]

choices = ["j", "j", "f", "f"]

df["response"] = np.select(conditions, choices, default=np.nan)

# Rename varaibles based on the codebook
rename_map = {
    "subject": "participant_id",
    "block": "phase_id",
    "item": "stimulus",
    "lexicality": "condition",
    "accuracy": "accuracy",
    "rt": "rt",
    "respons": "response"
}

df_cleaned = df.rename(columns=rename_map)

# Make "phase_id" a string variable
df_cleaned["phase_id"] = df_cleaned["phase_id"].astype("string")

# Export the cleaned file
df_cleaned.to_csv("/Users/cyhsieh/PsychLing-101/wang2025_lexicaldecision/processed_data/exp1.csv", index=False)