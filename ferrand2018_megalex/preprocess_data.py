import pandas as pd
import os

# MEGALEX (Ferrand et al., 2018), visual lexical decision, trial level.
# All 2,596,095 trials in the author file are kept; no RT, participant or block
# exclusions are applied here (see README.md).

N_TRIALS = 2596095


def preprocess():

    input_file = 'original_data/Visual.WpuispW.essais_ElTec.txt'
    output_dir = 'processed_data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'exp1.csv')

    print("Loading raw dataset")
    # The header names 9 columns but every data row has 10 fields: the first one
    # is the unnamed row index R writes with write.table(). It is read as
    # 'r_index' and dropped. Numbers are space-padded, hence skipinitialspace.
    # keep_default_na=False keeps letter strings such as 'nan' or 'null' as text.
    cols = ['target', 'numinit', 'subject', 'block', 'trial_num_block',
            'category', 'correct', 'rt', 'repetition']
    df = pd.read_csv(input_file, sep=';', header=None, skiprows=1,
                     names=['r_index'] + cols, skipinitialspace=True,
                     encoding='utf-8', keep_default_na=False,
                     dtype={'target': str, 'category': str})
    df = df.drop(columns='r_index')

    assert len(df) == N_TRIALS, f"expected {N_TRIALS} trials, found {len(df)}"
    assert set(df['category']) == {'w', 'p'}
    assert set(df['correct']) == {0, 1}
    assert df['numinit'].is_unique

    # Chronological order: numinit runs through the whole session of each
    # participant (block and trial_num_block increase along it).
    df = df.sort_values(['subject', 'numinit']).reset_index(drop=True)

    df = df.rename(columns={
        'subject': 'participant_id',
        'numinit': 'trial_id',
        'block': 'phase_id',
        'trial_num_block': 'trial_in_block',
        'target': 'stimulus',
        'correct': 'accuracy',
    })

    df['trial_order'] = df.groupby('participant_id').cumcount()

    is_word = df['category'] == 'w'
    df['stimulus_type'] = is_word.map({True: 'word', False: 'pseudoword'})

    # The file has no response column. In a two-choice task it follows from the
    # stimulus type and the accuracy of the response.
    said_word = is_word == (df['accuracy'] == 1)
    df['response'] = said_word.map({True: 'word', False: 'nonword'})

    # The letter string stayed on screen for at most 2 s. An incorrect trial at
    # or past that deadline may be a timeout, in which case no button was
    # pressed and the derived response would be an artefact; it is left empty.
    # (A correct trial past 2 s must be a real, late press.)
    timeout = (df['rt'] >= 2000) & (df['accuracy'] == 0)
    df.loc[timeout, 'response'] = ''

    df = df[[
        'participant_id',
        'trial_id',
        'trial_order',
        'phase_id',
        'trial_in_block',
        'stimulus_type',
        'stimulus',
        'response',
        'accuracy',
        'rt',
        'repetition',
    ]]

    print(f"Exporting preprocessed dataset to {output_file}")
    df.to_csv(output_file, index=False)
    print(f"Preprocessing complete: {len(df)} trials, "
          f"{df['participant_id'].nunique()} participants.")


if __name__ == "__main__":
    preprocess()
