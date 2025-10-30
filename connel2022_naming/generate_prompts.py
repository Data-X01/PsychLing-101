# Single-file JSONL (one line per participant) generator
# Minimal change from your original: writes a single output file with one JSON object per line.
import json
from pathlib import Path
import pandas as pd

INPATH = Path("/Users/tikhomirova/PsychLing-101/connel2022_naming/processed_data/exp1.csv")  # adjust if needed
OUTPATH = Path("prompts.jsonl")   # single output file (one JSON object per line)

df = pd.read_csv(INPATH, low_memory=False)

# Normalize column names
cols_map = {}
for c in df.columns:
    lc = c.lower()
    if lc in ("ppn", "patricipant_id", "patricipantid"):
        cols_map[c] = "participant_id"
    if lc == "recognition_rt":
        cols_map[c] = "rt"
    if lc == "image":
        cols_map[c] = "image_filename"
    if lc == "response_corrected":
        cols_map[c] = "response_corrected"
    if lc == "response":
        cols_map[c] = "response"
    if lc == "object":
        cols_map[c] = "object"
if cols_map:
    df = df.rename(columns=cols_map)

# Ensure participant_id exists
if "participant_id" not in df.columns:
    df["participant_id"] = pd.Categorical(df.index.astype(str)).codes

# Ensure trial_id exists
if "trial_id" not in df.columns:
    df["trial_id"] = df.groupby("participant_id").cumcount().astype(int)
else:
    df["trial_id"] = pd.to_numeric(df["trial_id"], errors="coerce").fillna(0).astype(int)

# Convert rt to numeric
df["rt"] = pd.to_numeric(df.get("rt"), errors="coerce")

def is_dk(resp):
    if pd.isna(resp):
        return False
    s = str(resp).strip().lower()
    return s in ("dk", "don't know", "dont know", "do not know")

def format_trial_description_row(row):
    rt = row.get("rt")
    image = row.get("image_filename") or row.get("image") or "the image"
    raw = row.get("response") if "response" in row.index else row.get("choice") if "choice" in row.index else ""
    corr = row.get("response_corrected") if "response_corrected" in row.index else ""
    obj = row.get("object") if "object" in row.index else None
    is_invalid = bool(row.get("is_invalid", False))
    is_rt_outlier = bool(row.get("is_rt_outlier", False))
    raw_str = "" if pd.isna(raw) else str(raw).strip()

    # opening line
    if pd.isna(rt):
        open_line = f"The image <{image}> appeared on the screen."
    else:
        open_line = f"The image <{image}> appeared on the screen; you pressed the SPACEBAR after {int(float(rt))} ms."

    # response handling
    if is_dk(raw):
        response_line = "You did not know the name of the shown object."
    elif is_invalid or raw_str == "" or raw_str.lower() in ("", "na", "n/a", "null"):
        response_line = "You typed invalid answer."
    else:
        if corr is not None and str(corr).strip() != "":
            response_line = f"After pressing SPACEBAR the image was replaced by a text box. You typed <<{str(corr).strip()}>>."
        else:
            response_line = f"After pressing SPACEBAR the image was replaced by a text box. You typed <<{raw_str}>>."

    # final object line
    if obj is None or (isinstance(obj, float) and pd.isna(obj)):
        object_line = "The object on the photograph is unknown."
    else:
        object_line = f"The object on the photograph is {obj}."

    flags = []
    if is_rt_outlier:
        flags.append("RT outlier")
    if is_invalid:
        flags.append("invalid response")
    flags_line = (" Note: " + "; ".join(flags) + ".") if flags else ""

    return f"{open_line} {response_line} {object_line}{flags_line}"

# Instruction string (concise)
instruction = (
    "You will be shown a series of photographs. Each photograph depicts a single object.\n"
    "Press the SPACEBAR as soon as a name for the pictured object comes to mind, and then type that exact name into the text box that appears.\n"
    "If you do not know what the object is, please type 'DK' for 'don't know'.\n"
    "Please answer as quickly and accurately as you can.\n\n"
)

participants = sorted(df["participant_id"].unique())

# Write a single JSONL file: one line (JSON object) per participant
with OUTPATH.open("w", encoding="utf8") as fo:
    for pid in participants:
        sub = df[df["participant_id"] == pid].sort_values("trial_id")
        trials = []
        for idx, (_, row) in enumerate(sub.iterrows(), start=1):
            desc = format_trial_description_row(row)
            trials.append(f"Trial {idx}:\n{desc}")
        text_body = instruction + "\n\n".join(trials) + "\n"
        result = {
            "participant": str(pid),
            "experiment": "vanHoef2024_naming",
            "text": text_body
        }
        # write one JSON object per line (compact, single-line per participant)
        fo.write(json.dumps(result, ensure_ascii=False) + "\n")

print(f"Wrote {len(participants)} participant records to: {OUTPATH}")

