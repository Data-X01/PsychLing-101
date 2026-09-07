"""Preprocess the Provo Corpus (Luke & Christianson, 2018) for PsychLing-101.

Reads the two source files in original_data/ and writes a single tidy,
trial-level CSV to processed_data/exp1.csv, with column names following
CODEBOOK.csv.

One row = one word (interest area) read by one participant.

Notes on source-data quirks handled here
----------------------------------------
* Both source files are Windows-1252 encoded, not UTF-8.
* ``IA_LABEL`` (what was actually drawn on screen) is used as the stimulus
  rather than ``Word``. The ``Word`` column comes from the cloze-norming
  spreadsheet and contains spreadsheet artefacts (e.g. the word "true" stored
  as the boolean "TRUE") as well as sentence punctuation attached to the token.
* ``Word_Number`` is missing for the first word of every passage, because the
  cloze norms only cover words that have a preceding context. ``IA_ID`` is
  complete and contiguous, so it is used for word position.
* ``IA_SKIP`` marks first-pass skipping, so a word with IA_SKIP == 1 may still
  have been fixated later during a regression. Whether a word was fixated at
  all is therefore derived from ``IA_DWELL_TIME > 0``.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.resolve()
ORIGINAL_DIR = BASE_DIR / "original_data"
PROCESSED_DIR = BASE_DIR / "processed_data"

EYETRACKING_FILE = ORIGINAL_DIR / "Provo_Corpus-Eyetracking_Data.csv"
NORMS_FILE = ORIGINAL_DIR / "Provo_Corpus-Predictability_Norms.csv"

SOURCE_ENCODING = "cp1252"

# Source column -> CODEBOOK column
COLUMN_MAP = {
    "Text_ID": "text_id",
    "IA_ID": "word_position",
    "Sentence_Number": "sentence_number",
    "Word_In_Sentence_Number": "word_in_sentence_number",
    "Word_Length": "word_length",
    "Word_POS": "part_of_speech",
    "Word_Content_Or_Function": "word_class",
    "OrthographicMatch": "cloze_predictability",
    "POSMatch": "pos_predictability",
    "Certainty": "cloze_certainty",
    "IA_DWELL_TIME": "rt",
    "IA_FIRST_FIXATION_DURATION": "first_fixation_duration",
    "IA_FIRST_RUN_DWELL_TIME": "gaze_duration",
    "IA_REGRESSION_PATH_DURATION": "go_past_time",
    "IA_FIXATION_COUNT": "fixation_count",
    "IA_RUN_COUNT": "run_count",
    "IA_SKIP": "is_first_pass_skipped",
    "IA_REGRESSION_IN": "is_regressed_into",
    "IA_REGRESSION_OUT": "is_regressed_out_of",
}

# Order of columns in the output file
OUTPUT_COLUMNS = [
    "participant_id",
    "trial_order",
    "text_id",
    "word_position",
    "sentence_number",
    "word_in_sentence_number",
    "stimulus",
    "word_length",
    "part_of_speech",
    "word_class",
    "cloze_predictability",
    "pos_predictability",
    "cloze_certainty",
    "rt",
    "first_fixation_duration",
    "gaze_duration",
    "go_past_time",
    "fixation_count",
    "run_count",
    "is_fixated",
    "is_first_pass_skipped",
    "is_regressed_into",
    "is_regressed_out_of",
]

INTEGER_COLUMNS = [
    "participant_id",
    "trial_order",
    "text_id",
    "word_position",
    "sentence_number",
    "word_in_sentence_number",
    "word_length",
    "rt",
    "fixation_count",
    "run_count",
    "is_fixated",
    "is_first_pass_skipped",
    "is_regressed_into",
    "is_regressed_out_of",
]


def check_norms_coverage(df: pd.DataFrame) -> None:
    """Sanity-check the processed data against the cloze-norming source file.

    The cloze predictability values in the eye-tracking file are derived from
    the norming study distributed alongside it. The norms are aggregated over
    norming participants (response counts per word), so they are not a
    trial-level experiment in their own right and are not exported separately;
    they are used here only to verify that the passages line up.
    """
    norms = pd.read_csv(
        NORMS_FILE,
        encoding=SOURCE_ENCODING,
        usecols=["Text_ID", "Word_Number"],
        low_memory=False,
    )
    expected_passages = set(norms["Text_ID"].unique())
    actual_passages = set(df["text_id"].unique())
    if expected_passages != actual_passages:
        raise ValueError(
            "Passage IDs in the eye-tracking data do not match the norms file: "
            f"{sorted(expected_passages ^ actual_passages)}"
        )
    print(f"  norms check: {len(actual_passages)} passages match the norming file")


def main() -> None:
    PROCESSED_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(EYETRACKING_FILE, encoding=SOURCE_ENCODING, low_memory=False)

    df = df.rename(columns=COLUMN_MAP)

    # Participant IDs ("Sub01") -> sequential integers starting at 1.
    participant_order = sorted(df["Participant_ID"].unique())
    id_map = {p: i + 1 for i, p in enumerate(participant_order)}
    df["participant_id"] = df["Participant_ID"].map(id_map)

    # TRIAL_INDEX is the order in which this participant saw the passages.
    # Passage order was randomised per participant, so this is not the same as
    # text_id. It already runs 1..55.
    df["trial_order"] = df["TRIAL_INDEX"].astype(int)

    # What was actually displayed on screen, without DataViewer's trailing pad.
    df["stimulus"] = df["IA_LABEL"].astype(str).str.strip()

    # A word counts as fixated if it accrued any dwell time.
    df["is_fixated"] = (df["rt"] > 0).astype(int)

    check_norms_coverage(df)

    df = df.sort_values(["participant_id", "trial_order", "word_position"])

    out = df[OUTPUT_COLUMNS].copy()

    for column in INTEGER_COLUMNS:
        out[column] = out[column].astype("Int64")

    output_path = PROCESSED_DIR / "exp1.csv"
    out.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"  rows:         {len(out):,}")
    print(f"  participants: {out['participant_id'].nunique()}")
    print(f"  passages:     {out['text_id'].nunique()}")
    print(f"  fixated:      {out['is_fixated'].mean():.1%} of words")


if __name__ == "__main__":
    main()
