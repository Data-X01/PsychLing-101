"""
Preprocessing script for de Varda et al. (2024) Cloze Probability Task

This script reads the raw cloze probability data from 8 lists, extracts participant
responses and demographics, and outputs a standardized CSV file.

Participants completed a cloze probability task where they saw sentence fragments
and wrote the next word they expected to follow.

NOTE: All identifying information (Prolific IDs) is anonymized with random uppercase strings.
"""

import pandas as pd
import numpy as np
import re
import random
import string
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
ORIGINAL_DATA_DIR = SCRIPT_DIR / "original_data"
PROCESSED_DATA_DIR = SCRIPT_DIR / "processed_data"

# Comprehension check target answers (participants must get 8/10 to be included)
TRGT_COMPREHENSION = [
    'get off the ground suddenly',
    'will not wait happily',
    'child that is determined to do what it wants',
    'small dogs with long ears',
    'stuck through with a sharp instrument',
    'an integrated human-machine system',
    'at its peak of success',
    'the faint color of her skin',
    'sliding box',
    'worried and puzzled'
]

# Global mapping for anonymization (to ensure consistency across files)
ANON_MAPPING = {}


def generate_anon_id(original_id: str) -> str:
    """Generate a consistent anonymous ID (6 uppercase letters) for a given original ID."""
    original_id_str = str(original_id).strip()
    if original_id_str not in ANON_MAPPING:
        # Generate 6 random uppercase letters
        ANON_MAPPING[original_id_str] = ''.join(random.choices(string.ascii_uppercase, k=6))
    return ANON_MAPPING[original_id_str]


def clean_cloze_question(question_text: str) -> str:
    """Extract the sentence fragment from the question text."""
    q = re.sub(r'\s*-\s*Write the next word of the sentence:\s*\n*\s*\[Field-1\]\.\.\.', "", question_text)
    return q.strip()


def load_prolific_data(list_num: int) -> pd.DataFrame:
    """Load prolific demographic data for a given list."""
    prolific_file = ORIGINAL_DATA_DIR / f"prolific_list{list_num}.csv"
    if prolific_file.exists():
        prolific = pd.read_csv(prolific_file)
        
        if 'participant_id' in prolific.columns:
            prolific['prolific_id'] = prolific['participant_id']
        
        cols_to_keep = ['prolific_id', 'age', 'Sex', 'Highest education level completed',
                       'First Language', 'First language', 'Nationality', 
                       'Country of Birth', 'Current Country of Residence']
        cols_available = [c for c in cols_to_keep if c in prolific.columns]
        prolific = prolific[cols_available].copy()
        
        prolific = prolific.rename(columns={
            'age': 'age',
            'Sex': 'gender',
            'Highest education level completed': 'education',
            'First Language': 'first_language',
            'First language': 'first_language',
            'Nationality': 'nationality',
            'Country of Birth': 'country_of_birth',
            'Current Country of Residence': 'country_of_residence'
        })
        return prolific
    return pd.DataFrame()


def process_list(list_num: int, item_set: pd.DataFrame) -> pd.DataFrame:
    """Process a single list file and return trial-level data."""
    file_path = ORIGINAL_DATA_DIR / f"list{list_num}.xls"
    df = pd.read_excel(file_path)
    
    # Extract questions from first row (in presentation order)
    questions = df.iloc[0, 28:].tolist()
    sentence_fragments = [clean_cloze_question(str(q)) for q in questions]
    
    # Get participant data (skip first row which has question text)
    participants_df = df.iloc[1:, :].copy()
    
    # Apply comprehension check exclusion
    part_comprehension = participants_df.iloc[:, 17:28]
    correctness = part_comprehension.iloc[:, 1:] == TRGT_COMPREHENSION
    part_comprehension_score = correctness.sum(axis=1)
    to_exclude = set(part_comprehension[part_comprehension_score < 8].iloc[:, 0])
    
    participants_df = participants_df[~participants_df.iloc[:, 17].isin(to_exclude)]
    
    print(f"List {list_num}: {len(to_exclude)} participants excluded, {len(participants_df)} remaining")
    
    prolific_df = load_prolific_data(list_num)
    
    # Get item info for this list - create mapping from sentence to item_id
    list_items = item_set[item_set['list'] == list_num].copy()
    sentence_to_item_id = dict(zip(list_items['sentence'].str.strip(), list_items['item_id']))
    sentence_to_target = dict(zip(list_items['sentence'].str.strip(), list_items['word'].str.strip()))
    
    all_trials = []
    
    for idx, row in participants_df.iterrows():
        original_participant_id = row['Q3']
        anon_participant_id = generate_anon_id(original_participant_id)
        
        demo = {}
        if not prolific_df.empty and 'prolific_id' in prolific_df.columns:
            match = prolific_df[prolific_df['prolific_id'] == original_participant_id]
            if not match.empty:
                demo = match.iloc[0].to_dict()
        
        # Process each trial in presentation order
        for trial_order, (col, sentence_frag) in enumerate(zip(df.columns[28:], sentence_fragments)):
            response = row[col]
            
            if pd.notna(response) and str(response).strip():
                response_clean = str(response).split()[0].lower()
                response_clean = re.sub("'", "'", response_clean)
            else:
                response_clean = ""
            
            # Get trial_id from item_id (same item = same trial_id across participants)
            trial_id = sentence_to_item_id.get(sentence_frag, -1)
            target_word = sentence_to_target.get(sentence_frag, "")
            
            trial_data = {
                'participant_id': anon_participant_id,
                'list': list_num,
                'trial_id': trial_id,  # Item-based ID (same for all participants seeing this item)
                'trial_order': trial_order,  # Presentation order (0-indexed)
                'stimulus': sentence_frag,
                'target_word': target_word,
                'response': response_clean,
                'age': demo.get('age', np.nan),
                'gender': demo.get('gender', ''),
                'education': demo.get('education', ''),
                'first_language': demo.get('first_language', ''),
                'nationality': demo.get('nationality', ''),
                'country_of_birth': demo.get('country_of_birth', ''),
                'country_of_residence': demo.get('country_of_residence', '')
            }
            all_trials.append(trial_data)
    
    return pd.DataFrame(all_trials)


def anonymize_excel_files():
    """Anonymize participant IDs in the Excel files."""
    print("\nAnonymizing Excel data files...")
    
    for list_num in range(1, 9):
        file_path = ORIGINAL_DATA_DIR / f"list{list_num}.xls"
        if file_path.exists():
            df = pd.read_excel(file_path)
            
            for idx in range(1, len(df)):
                original_id = df.iloc[idx, df.columns.get_loc('Q3')]
                if pd.notna(original_id):
                    anon_id = generate_anon_id(original_id)
                    df.iloc[idx, df.columns.get_loc('Q3')] = anon_id
            
            csv_path = file_path.with_suffix('.csv')
            df.to_csv(csv_path, index=False)
            file_path.unlink()
            print(f"  Anonymized list{list_num}.xls -> list{list_num}.csv")


def anonymize_prolific_files():
    """Remove identifying columns from prolific files."""
    print("\nAnonymizing Prolific export files...")
    
    for list_num in range(1, 9):
        prolific_file = ORIGINAL_DATA_DIR / f"prolific_list{list_num}.csv"
        if prolific_file.exists():
            df = pd.read_csv(prolific_file)
            
            id_cols = ['session_id', 'participant_id', 'entered_code', 'reviewed_at_datetime',
                      'started_datetime', 'completed_date_time', 'IPAddress']
            
            cols_to_drop = [c for c in id_cols if c in df.columns]
            df_anon = df.drop(columns=cols_to_drop, errors='ignore')
            
            df_anon.to_csv(prolific_file, index=False)
            print(f"  Anonymized prolific_list{list_num}.csv (removed: {len(cols_to_drop)} columns)")


def main():
    """Main preprocessing function."""
    # Set random seed for reproducibility
    random.seed(42)
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    item_set = pd.read_csv(ORIGINAL_DATA_DIR / "item-set.csv")
    item_set["sentence"] = item_set["sentence"].str.strip()
    
    all_data = []
    for list_num in range(1, 9):
        list_data = process_list(list_num, item_set)
        all_data.append(list_data)
    
    full_df = pd.concat(all_data, ignore_index=True)
    
    cols = ['participant_id', 'list', 'trial_id', 'trial_order', 'stimulus', 
            'target_word', 'response', 'age', 'gender', 'education', 
            'first_language', 'nationality', 'country_of_birth', 'country_of_residence']
    full_df = full_df[cols]
    
    output_path = PROCESSED_DATA_DIR / "exp1.csv"
    full_df.to_csv(output_path, index=False)
    
    unique_participants = full_df['participant_id'].nunique()
    unique_trials = full_df['trial_id'].nunique()
    
    print(f"\nWrote processed CSV: {output_path}")
    print(f"Total rows: {len(full_df)}")
    print(f"Total participants: {unique_participants}")
    print(f"Unique trial_ids (items): {unique_trials}")
    
    anonymize_excel_files()
    anonymize_prolific_files()
    
    # Print example data
    print("\n" + "="*80)
    print("EXAMPLE DATA (first 5 rows):")
    print("="*80)
    print(full_df.head().to_string())
    print("\n" + "="*80)
    print("VERIFICATION: Same item -> same trial_id across participants:")
    print("="*80)
    # Show that same stimulus has same trial_id
    sample_stimulus = full_df['stimulus'].iloc[0]
    same_item = full_df[full_df['stimulus'] == sample_stimulus][['participant_id', 'trial_id', 'stimulus', 'response']].head(3)
    print(same_item.to_string())
    print("="*80)


if __name__ == "__main__":
    main()
