import os
import zipfile
import pandas as pd
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(script_dir, "original_data/ldt_raw.zip")

#### Read data ####

def parse_file(file_obj):
    text = file_obj.read().decode("utf-8")
    lines = text.splitlines()

    to_delete = []
    footer_dict = {}

    for i, line in enumerate(lines):
        # header of sessions
        if line.startswith("Univ,"):
            cols = lines[i].split(",")
            vals = lines[i+1].split(",")
            to_delete.extend([i, i+1])
            if i == 0:
                session1_dict = dict(zip(cols, vals))
                session1_dict["start_session1_date"] = session1_dict.pop("Date")
                session1_dict["start_session1_time"] = session1_dict.pop("Time")
            else:
                session2_dict = dict(zip(cols, vals))
                session2_dict["start_session2_date"] = session2_dict.pop("Date")
                session2_dict["start_session2_time"] = session2_dict.pop("Time")

        # empty lines, "==="
        if not line.strip() or line.startswith("==="):
            to_delete.extend([i])
        
        # footer
        if line.startswith(("Subject,", "numCorrect,", "presHealth,")):
            cols = lines[i].split(",")
            vals = lines[i+1].split(",")
            to_delete.extend([i, i+1])
            footer_dict.update(dict(zip(cols, vals)))

    footer_dict["start_endblock_date"] = footer_dict.pop("Date")
    footer_dict["start_endblock_time"] = footer_dict.pop("Time")

    # Build df with subject-level information
    subject_dict = {**session1_dict, **session2_dict, **footer_dict}
    subj_lvl = pd.DataFrame([subject_dict])

    # Delete rows to_delete
    for i in reversed(to_delete):
        del lines[i]

    # Build df with trial-level information
    trial_lvl = pd.DataFrame([line.split(",") for line in lines])
    trial_lvl.columns = [
        "TrialOrder",
        "ItemSerialNumber",
        "Lexicality",
        "Accuracy",
        "LDT_RT",
        "Item"
    ]

    trial_lvl["Subject"] = subject_dict.get("Subject")
    trial_lvl["session_no"] = trial_lvl["TrialOrder"].astype(int) // 2001 #  2,000 trials in first session; TrialOrder is 1-indexed

    return trial_lvl, subj_lvl

all_trials = []
all_subjects = []

# list of redundant or questionable files according to code of the authors of English Lexicon Project (see ldt_extract.jl script in original_data folder)
skiplist = [
    "9999.LDT",
    "793DATA.LDT",
    "Data999.LDT",
    "Data1000.LDT",
    "Data1010.LDT",
    "Data1016.LDT",
]

with zipfile.ZipFile(data_path, "r") as z:
    for file in z.namelist():
        if file not in skiplist:
            with z.open(file) as f:
                trial_lvl, subj_lvl = parse_file(f)

                all_trials.append(trial_lvl)
                all_subjects.append(subj_lvl)

df_trial = pd.concat(all_trials, ignore_index=True)
df_subject = pd.concat(all_subjects, ignore_index=True)

#### Preprocessing ####

## Subject-level data ##

# Fix Dates and Times, cast into date format and calculate age
df_subject["DOB"] = (
    df_subject["DOB"]
    .str.replace("\\", "/", regex=False)
    .str.replace("-", "/", regex=False)
)

def add_slashes(x):
    x = str(x)
    if "/" not in x and len(x) in {6, 8}:
        return x[:2] + "/" + x[2:4] + "/" + x[4:]
    if "/" not in x and len(x) == 5:
        return x[:1] + "/" + x[1:3] + "/" + x[3:]
    return x

df_subject["DOB"] = df_subject["DOB"].apply(add_slashes)

def add_century(x):
    x = str(x)
    if x[-3] == "/":
        return x[:-2] + "19" + x[-2:]
    return x

df_subject["DOB"] = df_subject["DOB"].apply(add_century)

def fix_time(x):
    x = str(x)
    if len(x) == 5:
        return x + ":00"
    return x

df_subject["start_session1_time"] = df_subject["start_session1_time"].apply(fix_time)
df_subject["start_session2_time"] = df_subject["start_session2_time"].apply(fix_time)
df_subject["start_endblock_time"] = df_subject["start_endblock_time"].apply(fix_time)

df_subject["start_endblock_time"] =df_subject["start_endblock_time"].replace("", None)

df_subject['start_session1_datetime'] = pd.to_datetime(
    df_subject['start_session1_date'] + ' ' + df_subject['start_session1_time'],
    format='%m-%d-%Y %H:%M:%S',
    errors="coerce"
)

df_subject['start_session2_datetime'] = pd.to_datetime(
    df_subject['start_session2_date'] + ' ' + df_subject['start_session2_time'],
    format='%m-%d-%Y %H:%M:%S',
    errors="coerce"
)

df_subject['start_endblock_datetime'] = pd.to_datetime(
    df_subject['start_endblock_date'] + ' ' + df_subject['start_endblock_time'],
    format='%m-%d-%Y %H:%M:%S',
    errors="coerce"
)

df_subject["DOB"] = pd.to_datetime(
    df_subject["DOB"],
    dayfirst=False,
)

df_subject["start_session1_date"] = pd.to_datetime(
    df_subject["start_session1_date"],
    dayfirst=False,
    errors="coerce"
)

def compute_age(row):
    current = row["start_session1_date"]
    dob = row["DOB"]

    if pd.isna(current) or pd.isna(dob):
        return None

    age = current.year - dob.year - (
        (current.month, current.day) < (dob.month, dob.day)
    )

    return age

df_subject["age"] = df_subject.apply(compute_age, axis=1)

df_subject["DOB"] = df_subject["DOB"].dt.strftime("%Y-%m-%d")
df_subject["start_session1_datetime"] = df_subject["start_session1_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
df_subject["start_session2_datetime"] = df_subject["start_session2_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
df_subject["start_endblock_datetime"] = df_subject["start_endblock_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Cast num varaiables to num
for col in ["Univ", "Subject", "Education", "MEQ", "numCorrect", "rawScore", "vocabAge", "shipTime", "readTime", "presHealth", "pastHealth", "vision", "hearing"]:
    df_subject[col] = pd.to_numeric(df_subject[col], errors="coerce")

## Data cleaning according to code of authors of English Lexicon Project (see ldt_extract.jl script in original_data folder) ##

# recode gender x to NA
df_subject["Gender"] = df_subject["Gender"].replace("x", None)

# Shipley Institute of Living Scale recode to NA
cols_to_NA_shipley = ["numCorrect", "rawScore", "vocabAge", "shipTime", "readTime"]
df_subject[cols_to_NA_shipley] = df_subject[cols_to_NA_shipley].replace(999, None)

# Health Scale recode to NA
cols_to_NA_health = ["presHealth", "pastHealth", "vision", "hearing", "firstLang"]
df_subject[cols_to_NA_health] = df_subject[cols_to_NA_health].replace(["","Unknown", -1], None)

# Recode values < Threshold to NA
df_subject.loc[df_subject['rawScore'] < 3, 'rawScore'] = None
df_subject.loc[df_subject['numCorrect'] < 3, 'numCorrect'] = None
df_subject.loc[df_subject['vocabAge'] < 3, 'vocabAge'] = None
df_subject.loc[df_subject['readTime'] < 0, 'readTime'] = None
df_subject.loc[df_subject['MEQ'] < 3, 'MEQ'] = None

# Comment: recoding of dates and times, e.g., 00-00-0000 to NA, happened implicitely while type casting (see above)

## Further preprocessing ##

# Map names of universities
univ_mapping = {
    1: "morehead_state_university",
    2: "suny_albany",
    3: "university_of_kansas",
    4: "university_of_south_florida",
    5: "washington_university",
    6: "wayne_state_university"
}

df_subject["Univ"] = df_subject["Univ"].map(univ_mapping)

# increase readability of gender values
df_subject["Gender"] = df_subject["Gender"].replace({
    "m": "male",
    "f": "female"
})

df_subject["firstLang"] = df_subject["firstLang"].replace("English", "english")

# create Education_corrected
# The value was supposed to be years of education but some are recorded as years of university. Assumption: years of education before collage are regularly 12 years.
df_subject["Education_corrected"] = np.where(
    df_subject["Education"] < 12,
    df_subject["Education"] + 12,
    df_subject["Education"]
)

# remove single dates and times
df_subject = df_subject.drop(columns=[
    "start_session1_date",
    "start_session1_time",
    "start_session2_date",
    "start_session2_time",
    "start_endblock_date",
    "start_endblock_time"
])

# Reorder cols
cols = list(df_subject.columns)
front_cols = ["Subject", "Univ", "DOB", "age", "Gender", "Education", "Education_corrected", "firstLang"]

rest_cols = [c for c in cols if c not in front_cols]
df_subject = df_subject[front_cols + rest_cols]

# Drop shipTime and readTime due to no information about what variables measure
df_subject = df_subject.drop(columns=["shipTime", "readTime"])

# remove task because it is a constant
df_subject = df_subject.drop(columns = [
    "Task"
])

## trial-level data ##

# cast num variables to num
for col in ["TrialOrder", "ItemSerialNumber", "Lexicality", "Accuracy", "LDT_RT", "Subject"]:
    df_trial[col] = pd.to_numeric(df_trial[col], errors="coerce")

# In accurary: remove trials with accuracy other than 0 or 1; removes 1,370 values
valid_values = [0, 1]
df_trial = df_trial[df_trial["Accuracy"].isin(valid_values)]

# remove trials with faulty rts
# note: after 4000 ms, the stimulus was removed from the screen and the words "too slow" were presented
df_trial = df_trial[df_trial['LDT_RT'].between(0, 4000)]

# TrialOrder 0-indexing and reset to 0 for session 2
df_trial["TrialOrder"] = df_trial["TrialOrder"]-1

df_trial["TrialOrder"] = np.where(
    df_trial["session_no"] == 1,
    df_trial["TrialOrder"]-2000,
    df_trial["TrialOrder"]
)

## merge trial_df and subject_df ##
df = df_trial.merge(df_subject, on="Subject", how="left")

# create variable with session start time and remove other time variables
df["start_time"] = np.where(
    df["session_no"] == 0,
    df["start_session1_datetime"],
    df["start_session2_datetime"]
)

df = df.drop(columns = [
    "start_session1_datetime",
    "start_session2_datetime",
])

## Rename and reorder variables
df = df.rename(columns={
    "Subject": "participant_id",
    "TrialOrder": "trial_id",
    "ItemSerialNumber": "stimulus_id",
    "Lexicality": "lexicality",
    "Accuracy": "accuracy",
    "LDT_RT": "rt",
    "Item": "stimulus",
    "Univ": "university",
    "DOB": "day_of_birth",
    "Gender": "gender",
    "Education": "years_of_education",
    "Education_corrected": "years_of_education_corrected",
    "firstLang": "first_language",
    "MEQ": "meq_score",
    "numCorrect": "shipley_numCorrect",
    "rawScore": "shipley_rawScore",
    "vocabAge": "shipley_vocabAge",
    "presHealth": "present_health_score",
    "pastHealth": "past_health_score",
    "vision": "vision_score",
    "hearing": "hearing_score",
    "start_endblock_datetime": "start_endblock"
})

cols = list(df.columns)
front_cols = ["participant_id", "session_no", "trial_id"]
if "rt" in cols:
    front_cols.append("rt")

rest_cols = [c for c in cols if c not in front_cols]
df = df[front_cols + rest_cols]

#### Codebook ####
codebook = pd.read_csv(os.path.join(script_dir,"../CODEBOOK.csv"))

# Drop rows in codebook that aren't in the df
codebook = codebook[codebook["Recommended Column Name"].isin(df.columns)]

# Add variables to CODEBOOK.csv
add_to_codebook = pd.DataFrame([
    ["stimulus_id", "Unique identifier assigned to each stimulus. Note: There are two versions of each stimulus: a word and a nonword. Whether a certain stimulus is a word or a nonword is indicated by the variable 'lexicality'."],
    ["lexicality", "Binary indicator of whether a stimulus is a word or a nonword."],
    ["session_no", "Sequential index indicating the session number within each participant. The first session contained 2,000 trials and the second either 1,372 or 1,374."],
    ["university", "University from whose research participant pool the participant was recruited."],
    ["day_of_birth", "Participant's day of birth (YYYY-MM-DD)."],
    ["years_of_education", "Participant's number of years of education."],
    ["years_of_education_corrected", "Corrected variable years_of_education. The value was supposed to be years of education but some are recorded as years of university, so values smaller 12 were replaced with value plus 12 to approximate the correct value."],
    ["meq_score", "Participant's score on the Morningness-Eveningness Questionaire, a circadian rythm questionnare (Horne & Ostberg, 1976)."],
    ["shipley_numCorrect", "Number of correct answers given by the participant on the vocabulary test of the Shipley Institute of Living Scale, a self-administering scale for measuring intellectual impairment and deterioration (Shipley, 1940)."],
    ["shipley_rawScore", "Participant's raw score on the vocabulary test of the Shipley Institute of Living Scale, a self-administering scale for measuring intellectual impairment and deterioration (Shipley, 1940)."],
    ["shipley_vocabAge", "Vocabulary age of the participant according to the vocabulary test of the Shipley Institute of Living Scale, a self-administering scale for measuring intellectual impairment and deterioration (Shipley, 1940)."],
    ["present_health_score", "Participant's present health score on a general health questionnaire."],
    ["past_health_score", "Participant's past health score on a general health questionnaire."],
    ["vision_score", "Participant's vision score on a general health questionnaire."],
    ["hearing_score", "Participant's hearing score on a general health questionnaire."],
    ["start_endblock", "Timestamp when the participant started the final block of the survey. The block contained gender, the MEQ, the Shipley vocabulary test, and the general health questionnaire (YYYY-MM-DD HH:MM:SS)."]],
    columns = ["Recommended Column Name", "Description"]
)

codebook = pd.concat([codebook, add_to_codebook], ignore_index=True)

# sort codebook
codebook = (
    codebook
    .set_index('Recommended Column Name')
    .reindex(df.columns)
    .reset_index()
    .rename(columns = {"index":"Recommended Column Name"})
)

#### Save data ####

# Save codebook
codebook.to_csv(os.path.join(script_dir,"CODEBOOK.csv"), index=False)

# Save processed data
folder = os.path.join(script_dir, "processed_data")
os.makedirs(folder, exist_ok=True)
df.to_csv(os.path.join(script_dir,"processed_data/exp1.csv"), index=False)