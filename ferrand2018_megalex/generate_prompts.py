import pandas as pd
import hashlib
import json
import os
import random
import re
import string
import zipfile

# One MEGALEX session is ~27,000 trials, far over the 32K-token limit, so each
# participant is split into chunks of consecutive blocks. Every chunk opens
# with the instruction and says which blocks it covers.
#
# The prompts follow the procedure of the experiment (Ferrand et al., 2018,
# Method): there was no feedback after individual trials, only a feedback
# screen at the end of each block with the mean correct reaction time and the
# percentage of errors for words. Each block began with ten practice trials,
# which are not in the data; trials are numbered by their position in the block.

EXPERIMENT = 'ferrand2018_megalex/exp1'
BLOCKS_PER_CHUNK = 5
TOKEN_LIMIT = 32000
CHAR_LIMIT = 100000  # scripts/validate_submission.py rejects longer prompts

# Reconstructed from the Method section of Ferrand et al. (2018); the original
# instruction text is not part of the OSF deposit. The authors' W/N button
# names are replaced by the participant's randomised labels.
INSTRUCTION = (
    'In this experiment you will see letter strings presented one at a time in the '
    'centre of the screen. Some are real French words, others are pseudowords '
    '(invented strings that look like French words but do not exist). Decide, as '
    'quickly and as accurately as possible, whether each letter string is a French '
    'word or not. Press {word_key} for a real word and {nonword_key} for a '
    'pseudoword. Each trial starts with a fixation point, then the letter string, '
    'which stays on screen until you respond or for a maximum of 2 seconds. At the '
    'end of each block you will see your mean reaction time and error rate for '
    'words. The experiment consists of 109 blocks of about 260 items, completed '
    'over several weeks.'
)
CHUNK_NOTE = ('The trials below are from {blocks} of the experiment. Each block '
              'begins with ten practice trials, which were not recorded; trials '
              'are numbered by their position in the block.')
TRIAL = "Trial {number}: The letter string is '{stimulus}'. You press <<{key}>>."
# Shown at the end of every block in the experiment: mean correct RT and
# percentage of errors for words, recomputed here from the recorded trials.
BLOCK_FEEDBACK = ('End of block {block}. Mean reaction time for correct responses '
                  'to words: {rt} ms. Errors on words: {errors:.1f}%.')
# The one trial whose response is missing (a probable timeout, see README.md).
NO_RESPONSE = 'nothing'


def get_token_counter():
    """Exact cl100k_base counts when tiktoken is installed, else a generous estimate."""
    try:
        import tiktoken
        encoder = tiktoken.get_encoding('cl100k_base')
        return (lambda text: len(encoder.encode(text))), 'tiktoken cl100k_base'
    except ImportError:
        # Word/punctuation pieces inflated by a fifth, or one token per 3 characters
        # (French with accents splits more finely than English), whichever is larger.
        def estimate(text):
            pieces = len(re.findall(r'\w+|[^\w\s]', text))
            return int(max(pieces * 1.2, len(text) / 3)) + 1
        return estimate, 'estimate (tiktoken not installed)'


def participant_keys(participant_id):
    """Two distinct button labels, fixed per participant and reproducible across runs."""
    digest = hashlib.sha256(str(participant_id).encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], 'big'))
    word_key, nonword_key = rng.sample(string.ascii_uppercase, 2)
    return word_key, nonword_key


def block_label(blocks):
    if len(blocks) == 1:
        return f'block {blocks[0]}'
    return f'blocks {blocks[0]}-{blocks[-1]}'


def block_feedback(block):
    words = block[block['stimulus_type'] == 'word']
    correct_rt = words.loc[words['accuracy'] == 1, 'rt']
    return BLOCK_FEEDBACK.format(block=int(block['phase_id'].iloc[0]),
                                 rt=round(correct_rt.mean()),
                                 errors=100 * (1 - words['accuracy'].mean()))


def build_chunk(participant, chunk_blocks, instruction, key_of):
    """Text and reaction times of one chunk of consecutive blocks."""
    lines = [instruction, '', CHUNK_NOTE.format(blocks=block_label(chunk_blocks))]
    rt_list = []
    for phase_id in chunk_blocks:
        block = participant[participant['phase_id'] == phase_id]
        lines += ['', f'Block {phase_id}:']
        for row in block.itertuples(index=False):
            key = key_of[row.response] if row.response else NO_RESPONSE
            lines.append(TRIAL.format(number=row.trial_in_block,
                                      stimulus=row.stimulus, key=key))
            rt_list.append(float(row.rt))
        lines.append(block_feedback(block))
    return '\n'.join(lines), rt_list


def build_prompts(df, blocks_per_chunk=BLOCKS_PER_CHUNK):
    all_prompts = []
    for participant_id, participant in df.groupby('participant_id'):

        word_key, nonword_key = participant_keys(participant_id)
        key_of = {'word': word_key, 'nonword': nonword_key}
        instruction = INSTRUCTION.format(word_key=word_key, nonword_key=nonword_key)

        blocks = sorted(participant['phase_id'].unique())
        for start in range(0, len(blocks), blocks_per_chunk):
            chunk_blocks = [int(b) for b in blocks[start:start + blocks_per_chunk]]
            text, rt_list = build_chunk(participant, chunk_blocks, instruction, key_of)
            all_prompts.append({
                'text': text,
                'experiment': EXPERIMENT,
                'participant_id': str(participant_id),
                'blocks': chunk_blocks,
                'rt': rt_list,
            })
    return all_prompts


def load_trials():
    df = pd.read_csv('processed_data/exp1.csv', keep_default_na=False,
                     dtype={'stimulus': str, 'response': str})
    return df.sort_values(['participant_id', 'trial_order'])


def generate_prompts():
    print("Loading preprocessed dataset")
    df = load_trials()

    print("Grouping trials by participant and block")
    all_prompts = build_prompts(df)

    count_tokens, token_method = get_token_counter()
    max_tokens, max_chars = 0, 0
    for prompt in all_prompts:
        text = prompt['text']
        # Responses are the only thing wrapped in << >>, one per trial.
        assert text.count('<<') == text.count('>>') == len(prompt['rt'])
        assert '<' not in text.replace('<<', '') and '>' not in text.replace('>>', '')
        n_tokens = count_tokens(text)
        assert n_tokens < TOKEN_LIMIT, (prompt['participant_id'], prompt['blocks'], n_tokens)
        assert len(text) < CHAR_LIMIT, (prompt['participant_id'], prompt['blocks'], len(text))
        max_tokens = max(max_tokens, n_tokens)
        max_chars = max(max_chars, len(text))

    n_trials = sum(len(p['rt']) for p in all_prompts)
    assert n_trials == len(df), (n_trials, len(df))

    output_file = "prompts.jsonl"
    zip_file = "prompts.jsonl.zip"

    print(f"Writing all {len(all_prompts)} prompts to {output_file}")
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        for prompt in all_prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')

    print(f"Compressing to {zip_file}")
    # Fixed timestamp so that re-running the script gives a byte-identical archive.
    entry = zipfile.ZipInfo(output_file, date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o644 << 16
    with zipfile.ZipFile(zip_file, 'w') as zf, open(output_file, 'rb') as f:
        zf.writestr(entry, f.read())

    print(f"Removing uncompressed {output_file}")
    os.remove(output_file)

    print(f"{len(all_prompts)} prompts for {df['participant_id'].nunique()} participants, "
          f"{n_trials} trials")
    print(f"Largest prompt: {max_tokens} tokens ({token_method}), {max_chars} characters; "
          f"limits {TOKEN_LIMIT} tokens, {CHAR_LIMIT} characters")
    print("Prompt generation and compression complete.")


if __name__ == "__main__":
    generate_prompts()
