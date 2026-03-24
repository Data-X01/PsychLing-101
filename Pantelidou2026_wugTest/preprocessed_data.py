import pandas as pd
import chardet
import csv

def detect_encoding(file_path):
    """Try to detect encoding, with fallbacks for common European encodings."""
    with open(file_path, 'rb') as f:
        rawdata = f.read()

    # Try chardet first
    detected = chardet.detect(rawdata)
    if detected and detected.get('encoding'):
        print(f"  Chardet detected: {detected['encoding']} (confidence: {detected.get('confidence', 'unknown')})")
        # If confidence is low or it's ASCII, try alternatives
        if detected.get('confidence', 0) > 0.7 and detected['encoding'].upper() != 'ASCII':
            return detected['encoding']

    # Try common encodings manually for files with accented characters
    # PRIORITIZE latin-1 for Catalan text
    for encoding in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
        try:
            rawdata.decode(encoding)
            print(f"  Successfully decoded with: {encoding}")
            return encoding
        except (UnicodeDecodeError, AttributeError):
            continue

    # Default to latin-1 as it's most permissive for Western European text
    print(f"  Defaulting to: latin-1")
    return 'latin-1'

def transform_to_target(input_csv, target_columns, column_mapping=None, drop_columns=None):
    encoding = detect_encoding(input_csv)
    print(f"Detected encoding for {input_csv}: {encoding}")

    # Force everything to string from the start
    df = pd.read_csv(
        input_csv,
        engine='python',
        encoding=encoding,
        on_bad_lines='skip',
        dtype=str,           # prevents .0 values
        skip_blank_lines=True
    )

    # Rename columns
    if column_mapping:
        df = df.rename(columns=column_mapping)

    # Drop unwanted columns
    if drop_columns:
        df = df.drop(columns=[c for c in drop_columns if c in df.columns], errors='ignore')

    # Create all target columns first
    for col in target_columns:
        if col not in df.columns:
            df[col] = ""

    # Keep only target columns in fixed order
    df = df[target_columns]

    # Replace NaN with empty string
    df = df.fillna("")

    # Remove .0 endings if any slipped through
    df = df.replace(r"\.0$", "", regex=True)

    # Strip whitespace
    df = df.apply(lambda col: col.str.strip())

    # Remove completely empty rows (major cause of ,,,,,,,)
    df = df[~(df == "").all(axis=1)]

    return df


target_columns = [
    'trial_id','participant_id','age','gender','first_language','other_languages',
    'clinical_diagnoses','stimulus','response','accuracy'
]

drop_columns = [
    'speech therapy help',
    'Speech Therapy Help',
    'speech_therapy_help'
]

mapping = {
    'QuestionNumber':'trial_id',
    'ParticipantNumber': 'participant_id',
    'Age': 'age',
    'Gender': 'gender',
    'Native Language': 'first_language',
    'Other languages': 'other_languages',
    'Medical history': 'clinical_diagnoses',
    'Prompt':'stimulus',
    'Responses': 'response',
    'Response':'response',
    'Accuracy': 'accuracy',
}

input_files = [
    "original_data/input1.csv",
    "original_data/input2.csv",
    "original_data/input3.csv",
    "original_data/input4.csv",
]

for i, file in enumerate(input_files, start=1):
    df_out = transform_to_target(file, target_columns, mapping, drop_columns)
    output_name = f"exp{i}.csv"

    df_out.to_csv(
        output_name,
        index=False,
        quoting=csv.QUOTE_MINIMAL
    )

    print(f"Saved {output_name}")