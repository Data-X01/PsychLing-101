import pandas as pd
import random
import string
import numpy as np
import csv

### Experiment 1 - colour associates-looking pseudowords

#Load the original dataset
df = pd.read_csv("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Exp1 - original.csv", sep=';', header=None)

#Remove training trials
df = df[df.iloc[:, 0] != "training"]

#Remove columns irrelevant for this project (e.g., stem frequency, affix, colour)
columns_to_drop = [0,2,3,5,6,7,8,9,10,11,12,13,14]
df_cleaned = df.drop(df.columns[columns_to_drop], axis=1)

#Assign names to the columns
df_cleaned.columns=["stimuli", "type", "key", "accuracy", "rt"]

#Remove rows that contain missing values (i.e., the pause between two blocks)
df_cleaned = df_cleaned.dropna()

#Add a trial_id column
df_cleaned["trial_id"] = np.arange(len(df_cleaned)) % 366 + 1

#Add a participant_id column
df_cleaned["participant_id"] = (df_cleaned["trial_id"] == 1).cumsum()

#Reordering columns in the required order
df_final = df_cleaned.loc[:, ['participant_id', 'stimuli', 'type', 'key', 'accuracy', 'rt', 'trial_id']]

#"Age" taken from the survey files from psytoolkit

#Remove decimal values from some columns
columns_to_int = ['type', 'key', 'accuracy', 'rt']
df_final = df_final.astype({col:'int' for col in columns_to_int})

#Export to csv
df_final.to_csv("Saban-Italian LDT Exp1.csv")


### Experiment 2 - colour words-looking pseudowords

#Load the original dataset
df = pd.read_csv("C:/Users/ivasa/Documents/PsyLing101/My contribution - Italian LDT with colour words/Exp2 - original.csv", sep=';', header=0)

#Remove columns irrelevant for this project (e.g., stem frequency, affix, colour)
columns_to_drop = ["task", "stem", "affix", "fs", "length", "zipf", "r", "g", "b", "ld", "congruency", "correct"]
df_cleaned = df.drop(columns=columns_to_drop)

#Rename column "participant" to "participant_id"
df_cleaned = df_cleaned.rename(columns={'participant': 'participant_id'})

#Add a trial_id column
df_cleaned["trial_id"] = df_cleaned.groupby("participant_id").cumcount() + 1

#"Age" taken from the survey files from psytoolkit

#Export to csv
df_cleaned.to_csv("Saban-Italian LDT Exp2.csv")