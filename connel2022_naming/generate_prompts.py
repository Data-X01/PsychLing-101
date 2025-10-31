import json
from pathlib import Path
from typing import Optional, Any
import pandas as pd

## --- Configuration ---
INPATH = Path("/Users/tikhomirova/PsychLing-101/connel2022_naming/processed_data/exp1.csv")
OUTPATH = Path("prompts.jsonl")

## --- Data Loading and Initial Preparation ---
print(f"Loading data from: {INPATH}")
try:
    df = pd.read_csv(INPATH, low_memory=False)
except FileNotFoundError:
    print(f"Error: Input file not found at {INPATH}")
    exit(1)

COLUMN_NAME_MAP = {
    "ppn": "participant_id",
    "patricipant_id": "participant_id",
    "patricipantid": "participant_id",
    "recognition_rt": "rt",
    "image": "image_filename",
    "response_corrected": "response_corrected",
    "response": "response",
    "object": "object",
    "choice": "response",
}

cols_map = {}
for c in df.columns:
    lc = c.lower()
    if lc in COLUMN_NAME_MAP:
        cols_map[c] = COLUMN_NAME_MAP[lc]

if cols_map:
    df = df.rename(columns=cols_map)

## --- Data Cleaning and Standardization ---

if "participant_id" not in df.columns:
    print("Warning: 'participant_id' not found. Generating dummy IDs based on index.")
    df["participant_id"] = pd.Categorical(df.index.astype(str)).codes

if "trial_id" not in df.columns:
    df["trial_id"] = df.groupby("participant_id").cumcount().astype(int)
else:
    df["trial_id"] = pd.to_numeric(df["trial_id"], errors="coerce").fillna(0).astype(int)

df["rt"] = pd.to_numeric(df.get("rt"), errors="coerce")

for col in ["response", "response_corrected", "image_filename", "object", "is_invalid", "is_rt_outlier"]:
    if col not in df.columns:
        if col in ["is_invalid", "is_rt_outlier"]:
            df[col] = False
        else:
            df[col] = pd.NA

## --- Helper Functions for Prompt Generation ---

def is_dk(resp: Any) -> bool:
    """Checks if a response string is a 'Don't Know' (DK) variant."""
    if pd.isna(resp):
        return False
    s = str(resp).strip().lower()
    return s in ("dk", "don't know", "dont know", "do not know")

def format_trial_description_row(row: pd.Series) -> str:
    """
    Formats a single trial row into a descriptive string for the prompt text body.

    Args:
        row: A pandas Series representing one trial (one row of the DataFrame).

    Returns:
        A single string describing the trial event, response, and object.
    """
    rt: Optional[float] = row["rt"]
    image: str = row["image_filename"] or "the image"
    raw_response: Any = row["response"]
    corrected_response: Any = row["response_corrected"]
    obj: Any = row["object"]
    is_invalid: bool = bool(row["is_invalid"])
    is_rt_outlier: bool = bool(row["is_rt_outlier"])

    raw_str = "" if pd.isna(raw_response) else str(raw_response).strip()
    corr_str = "" if pd.isna(corrected_response) else str(corrected_response).strip()

    # 1. Opening Line (Image and RT)
    if pd.isna(rt) or rt is None:
        open_line = f"The image <{image}> appeared on the screen."
    else:
        open_line = f"The image <{image}> appeared on the screen; you pressed the SPACEBAR after {int(float(rt))} ms."

    # 2. Response Handling Line
    if is_dk(raw_response):
        response_line = "You did not know the name of the shown object."
    elif is_invalid or raw_str == "" or raw_str.lower() in ("na", "n/a", "null"):
        response_line = "You typed invalid answer."
    else:
        if corr_str != "":
            response_line = f"After pressing SPACEBAR the image was replaced by a text box. You typed <<{corr_str}>>."
        else:
            response_line = f"After pressing SPACEBAR the image was replaced by a text box. You typed <<{raw_str}>>."

    # 3. Final Object Line (What the object was)
    if pd.isna(obj):
        object_line = "The object on the photograph is unknown."
    else:
        object_line = f"The object on the photograph is {str(obj)}."


    return f"{open_line} {response_line} {object_line}"

## --- Main Processing and Output ---

INSTRUCTION_TEXT = (
    "You will be shown a series of photographs. Each photograph depicts a single object.\n"
    "Press the SPACEBAR as soon as a name for the pictured object comes to mind, and then type that exact name into the text box that appears.\n"
    "If you do not know what the object is, please type 'DK' for 'don't know'.\n"
    "Please answer as quickly and accurately as you can.\n\n"
)

participants = sorted(df["participant_id"].unique())

print(f"Processing data for {len(participants)} unique participants...")

with OUTPATH.open("w", encoding="utf8") as fo:
    for pid in participants:
        sub_df = df[df["participant_id"] == pid].sort_values("trial_id")

        trials = []
        for idx, row in enumerate(sub_df.itertuples(index=False), start=1):
            desc = format_trial_description_row(pd.Series(row._asdict()))
            trials.append(f"Trial {idx}:\n{desc}")

        text_body = INSTRUCTION_TEXT + "\n\n".join(trials) + "\n"

        result = {
            "participant": str(pid),
            "experiment": "connel2022_naming_exp1",
            "text": text_body
        }

        fo.write(json.dumps(result, ensure_ascii=False) + "\n")

print(f" Successfully wrote {len(participants)} participant records to: {OUTPATH}")
