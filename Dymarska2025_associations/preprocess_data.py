import pandas as pd
from pathlib import Path

def preprocess():
    base_dir = Path(".")
    original_dir = base_dir / "original_data"
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)

    # 1. Read all CSVs in original_data/
    csv_files = list(original_dir.glob("*.csv"))
    if not csv_files:
        print("Error: No CSV files found in original_data/")
        return

    frames = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(frames, ignore_index=True)

    # 2. Rename and Clean Columns
    # Mapping based on typical headers found in your data
    rename_map = {
        'Ps.number': 'participant_id',
        'Cue.number': 'cue_id',
        'cues': 'stimulus',
        'Response_corrected': 'response'
    }
    df = df.rename(columns=rename_map)

    # 3. Pivot to Wide Format (One row per participant × stimulus)
    wide = df.pivot_table(
        index=['participant_id', 'cue_id', 'stimulus'],
        columns='Response.number',
        values=['response', 'first_key_RT'],
        aggfunc='first'
    )

    # Standardize column names (e.g., response1, first_key_RT1)
    wide.columns = [f'{val}{int(num)}' for val, num in wide.columns]
    wide = wide.reset_index()
    wide['trial_id'] = wide.groupby('participant_id').cumcount() + 1

    # Ensure all columns response1 through response20 exist (even if blank)
    for i in range(1, 21):
        col = f'response{i}'
        if col not in wide.columns:
            wide[col] = ""
    
    # Final column ordering
    
    final_cols = ['participant_id', 'trial_id', 'cue_id', 'stimulus'] + [f'response{i}' for i in range(1, 21)] + [f'first_key_RT{i}' for i in range(1, 21)]
    df_final = wide[final_cols].fillna("")

    # 4. Save Processed Data
    output_path = processed_dir / "exp1.csv"
    df_final.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    preprocess()