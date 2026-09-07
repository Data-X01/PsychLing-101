"""Preprocessing script for Lally & Rastle (2022) Letter Identification.

Study
-----
Lally, C., & Rastle, K. (2022). Orthographic and feature-level contributions to
letter identification. Quarterly Journal of Experimental Psychology, 75(9).

Reicher-Wheeler task: a letter string is flashed, masked, and then two candidate
letters appear above and below one position of the mask. Participants report
which of the two occurred in the string, so chance performance is 50%. The design
is 3 (orthographic status: word, pseudoword, consonant string) x 2 (visual
overlap between the two candidate letters: high, low), fully within participants.
72 participants x 144 trials = 10368 observations over 48 items, each item built
in three orthographic versions.

Reads
-----
original_data/Data & Analyses/FeatureCuesResults.csv
    Trial-level results. Two DMDX conventions matter here: the reaction time of
    an incorrect response is stored with a negative sign, and the five-digit item
    code packs the whole design into its digits -- list, orthographic status,
    visual overlap, item number (see check_results).
original_data/Stimuli & Experiments/FeatureCuesStimuli.xlsx
    Sheet "StimuliSummary": the 48 items in their three orthographic versions,
    each with a high- and a low-overlap alternative string, plus letter-similarity
    ratings. Worksheet row order is the item number (first row = item 1).

Writes
------
processed_data/exp1.csv
    One row per trial, in the columns documented in CODEBOOK.csv.

Nothing inside original_data/ is written to or modified. Every consistency check
below raises before anything is written, so a partial or silently wrong output
file cannot be produced.
"""

import hashlib
import os
import re
from pathlib import Path

import pandas as pd

# All paths are relative: the script is meant to be run from this contribution
# folder, so that it works unchanged from a fresh clone of the repository.
ORIGINAL_DATA_DIR = Path("original_data")
PROCESSED_DATA_DIR = Path("processed_data")

RESULTS_FILE = ORIGINAL_DATA_DIR / "Data & Analyses" / "FeatureCuesResults.csv"
STIMULI_FILE = ORIGINAL_DATA_DIR / "Stimuli & Experiments" / "FeatureCuesStimuli.xlsx"
STIMULI_SHEET = "StimuliSummary"
# The workbook also ships the full letter-by-letter similarity matrices the item
# table was built from, which makes them an independent check on the ratings.
SIMILARITY_SHEETS = {
    "letter_similarity_human": "LetterSimilarity_SpeakerRatings",
    "letter_similarity_hmax": "LetterSimilarity_HMAXRatings",
}
OUT_FILE = PROCESSED_DATA_DIR / "exp1.csv"

# Expected shape of the data set, from the method section of the paper.
N_TRIALS = 10368
N_PARTICIPANTS = 72
N_TRIALS_PER_PARTICIPANT = 144
N_ITEMS = 48
N_PER_DESIGN_CELL = 1728  # 10368 trials spread over 3 x 2 = 6 design cells

# That the worksheet row order is the item number is the one thing this script
# cannot derive from the results file, and getting it wrong would relabel every
# item without tripping any other check. It was validated against the DMDX
# experiment script shipped next to the workbook: across all 144 trials of list 1,
# the strings presented under item code ...NN are the strings on worksheet row NN.
# This fingerprint of the ordered word targets (item 1 "snow" ... item 48 "sake")
# pins that order, so a re-sorted or edited worksheet fails loudly instead.
ITEM_ORDER_FINGERPRINT = "6b3967c075f7d6a6c8d3b749db340652628cf953"

# The stimuli sheet spreads its header over two rows of merged cells and separates
# the blocks with unnamed spacer columns, so the 19 columns are named by position.
# Reading by position is only safe if the sheet really is laid out as expected, so
# the header pandas does see is checked first. The four rating columns come from
# two merged blocks that both read "High_Overlap" / "Low_Overlap", which is why
# pandas suffixes the second pair and why they have to be told apart by position.
STIMULI_HEADER = [
    "Position", "Manipulation", "Length",
    "WW_Target", "WW_High", "WW_Low", "Unnamed: 6",
    "PW_Target", "PW_High", "PW_Low", "Unnamed: 10",
    "CS_Target", "CS_High", "CS_Low", "Unnamed: 14",
    "High_Overlap", "Low_Overlap", "High_Overlap.1", "Low_Overlap.1",
]
STIMULI_COLUMNS = [
    "Position", "Manipulation", "Length",
    "WW_Target", "WW_High", "WW_Low", "spacer_1",
    "PW_Target", "PW_High", "PW_Low", "spacer_2",
    "CS_Target", "CS_High", "CS_Low", "spacer_3",
    "Spk_High", "Spk_Low", "HMAX_High", "HMAX_Low",
]
STIMULUS_STRING_COLUMNS = [prefix + "_" + suffix
                           for prefix in ("WW", "PW", "CS")
                           for suffix in ("Target", "High", "Low")]

# OrthographicStatus maps to a tidy label and to the column prefix of the matching
# block in the stimuli sheet. Keys are the raw labels reduced to bare letters, so
# that "Pseudo-Word" (as spelled in the results file) and "Pseudoword" both match.
ORTHOGRAPHIC_STATUS = {
    "word": ("word", "WW"),
    "pseudoword": ("pseudoword", "PW"),
    "consonantstring": ("consonant_string", "CS"),
}
VISUAL_OVERLAP = {"High": "high", "Low": "low"}

# Digits 2 and 3 of the DMDX item code repeat the two design factors, which makes
# them a free cross-check on the OrthographicStatus and VisualOverlap columns.
DMDX_CONTEXT_DIGIT = {"1": "word", "2": "pseudoword", "3": "consonant_string"}
DMDX_OVERLAP_DIGIT = {"1": "low", "2": "high"}

# Value domains that the source files are expected to stay inside.
EXPOSURE_DURATIONS = [33, 50, 67, 83]  # milliseconds, thresholded per participant
POSITION_TYPES = ["internal", "external"]
HMAX_RANGE = (0.0, 1.0)  # the HMAX model reports a correlation-like similarity
SPEAKER_RATING_RANGE = (1.0, 7.0)  # the human ratings use a seven-point scale

COLUMN_ORDER = [
    "participant_id", "trial_id", "dmdx_item_code", "trial_order",
    "exposure_duration_ms", "list",
    "stimulus_type", "condition", "stimulus", "stimulus_length",
    "letter_position", "position_type", "target_letter", "distractor_letter",
    "letter_similarity_human", "letter_similarity_hmax",
    "response", "accuracy", "rt",
]


def require(condition, message):
    """Abort with an explicit message when a consistency check fails."""
    if not condition:
        raise ValueError("Consistency check failed: " + message)


def orthographic_key(raw_status):
    """Reduce an OrthographicStatus label to its lookup key ("Pseudo-Word" -> "pseudoword")."""
    key = re.sub("[^a-z]", "", str(raw_status).lower())
    require(key in ORTHOGRAPHIC_STATUS, "unknown OrthographicStatus %r" % raw_status)
    return key


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load_results():
    """Read the trial-level results file.

    Identifier-like columns are read as strings so that the zero padding of Item
    ("06") and the individual digits of the DMDX code survive intact.
    """
    if not RESULTS_FILE.exists():
        raise FileNotFoundError("Missing input file: %s" % RESULTS_FILE)

    try:
        results = pd.read_csv(
            RESULTS_FILE,
            dtype={"SubID": str, "List": str, "DMDX": str, "Item": str},
        )
    except Exception as error:
        raise ValueError("Could not read %s (%s). Restore it from the OSF repository."
                         % (RESULTS_FILE, error)) from error
    expected = ["SubID", "Exposure", "List", "Trial", "DMDX",
                "Item", "OrthographicStatus", "VisualOverlap", "Acc", "RT"]
    require(list(results.columns) == expected,
            "unexpected columns in %s: %r" % (RESULTS_FILE.name, list(results.columns)))
    results["item_number"] = results["Item"].astype(int)
    return results


def load_stimuli():
    """Read the 48 items from the stimuli workbook.

    The real header sits on the second row. Everything below the last item is a
    block of summary statistics (MIN, MAX, MEAN, ...) that carries no target
    string and is dropped. Worksheet row order is the item number; this is
    confirmed by the DMDX experiment script shipped alongside the workbook, whose
    trial for item code ...NN presents exactly the strings on worksheet row NN.
    """
    if not STIMULI_FILE.exists():
        raise FileNotFoundError("Missing input file: %s" % STIMULI_FILE)

    try:
        stimuli = pd.read_excel(STIMULI_FILE, sheet_name=STIMULI_SHEET, header=1)
    except Exception as error:
        raise ValueError("Could not read sheet %r of %s (%s). Restore it from the OSF "
                         "repository." % (STIMULI_SHEET, STIMULI_FILE, error)) from error

    # The columns are addressed by position below, so the layout is checked first:
    # a re-exported sheet with a moved or renamed column would otherwise be read
    # as if nothing had changed, silently swapping e.g. the high- and low-overlap
    # alternatives on every single trial.
    require([str(column) for column in stimuli.columns] == STIMULI_HEADER,
            "unexpected layout in sheet %r: the header reads %r, expected %r"
            % (STIMULI_SHEET, [str(column) for column in stimuli.columns], STIMULI_HEADER))
    stimuli.columns = STIMULI_COLUMNS

    stimuli = stimuli[stimuli["WW_Target"].notna()].reset_index(drop=True)
    require(len(stimuli) == N_ITEMS,
            "expected %d items in sheet %r, found %d" % (N_ITEMS, STIMULI_SHEET, len(stimuli)))

    require(stimuli["WW_Target"].map(lambda value: isinstance(value, str)).all(),
            "column WW_Target holds a value that is not a string")
    fingerprint = hashlib.sha1("|".join(stimuli["WW_Target"]).encode()).hexdigest()
    require(fingerprint == ITEM_ORDER_FINGERPRINT,
            "the items in sheet %r are not in their expected order: the word targets run "
            "%r ... %r with fingerprint %s, expected %s. Item numbers are read off the row "
            "order, so the sheet must not be re-sorted or edited."
            % (STIMULI_SHEET, stimuli["WW_Target"].iloc[0], stimuli["WW_Target"].iloc[-1],
               fingerprint, ITEM_ORDER_FINGERPRINT))

    stimuli["item_number"] = stimuli.index + 1
    stimuli["Manipulation"] = stimuli["Manipulation"].astype(int)
    stimuli["Length"] = stimuli["Length"].astype(int)
    return stimuli.drop(columns=["spacer_1", "spacer_2", "spacer_3"])


# --------------------------------------------------------------------------- #
# Reconstructing the trials
# --------------------------------------------------------------------------- #

def reconstruct_trial(row):
    """Rebuild what a single trial looked like.

    Neither the presented string nor the two candidate letters are stored in the
    results file, but both follow from the item and the two design factors. The
    orthographic status picks one of the three versions of the item, and the
    visual-overlap level picks the alternative string the distractor comes from.
    Target and alternative differ in exactly one letter, the probed one.

    The participant's response is not recorded either. The choice was between two
    letters only, so a correct trial means the target letter was reported and an
    incorrect trial means the distractor was.
    """
    stimulus_type, prefix = ORTHOGRAPHIC_STATUS[orthographic_key(row["OrthographicStatus"])]
    overlap = row["VisualOverlap"]

    stimulus = row[prefix + "_Target"]
    alternative = row[prefix + "_" + overlap]
    index = row["Manipulation"] - 1  # Manipulation counts positions from one

    target_letter = stimulus[index]
    distractor_letter = alternative[index]

    return pd.Series({
        "stimulus_type": stimulus_type,
        "condition": VISUAL_OVERLAP[overlap],
        "stimulus": stimulus,
        "target_letter": target_letter,
        "distractor_letter": distractor_letter,
        "response": target_letter if row["Acc"] == 1 else distractor_letter,
        "letter_similarity_human": row["Spk_" + overlap],
        "letter_similarity_hmax": row["HMAX_" + overlap],
    })


def build_trials(results, stimuli):
    """Join the results to the item table and rebuild every trial."""
    trials = results.merge(stimuli, on="item_number", how="left", validate="many_to_one")
    require(len(trials) == len(results), "the merge with the stimuli changed the row count")
    require(trials["WW_Target"].notna().all(), "some trials found no matching item")

    trials = pd.concat([trials, trials.apply(reconstruct_trial, axis=1)], axis=1)

    trials["participant_id"] = trials["SubID"]
    trials["dmdx_item_code"] = trials["DMDX"]
    # The leading digit of the DMDX code is the counterbalancing list, so keeping it
    # would give the same trial two identifiers depending on which list a participant
    # was in. trial_id drops it and names the trial itself: orthographic status,
    # visual overlap and item.
    trials["trial_id"] = trials["DMDX"].str[1:5]
    # Presentation order is recorded from one in the source; the codebook wants 0-indexing.
    trials["trial_order"] = trials["Trial"] - 1
    trials["exposure_duration_ms"] = trials["Exposure"]
    trials["list"] = trials["List"].astype(int)
    trials["stimulus_length"] = trials["Length"]
    trials["letter_position"] = trials["Manipulation"]
    trials["position_type"] = trials["Position"].str.lower()
    trials["accuracy"] = trials["Acc"]
    # DMDX signs the reaction times of incorrect responses negative; keep magnitudes.
    trials["rt"] = trials["RT"].abs()
    return trials


# --------------------------------------------------------------------------- #
# Consistency checks
# --------------------------------------------------------------------------- #

def check_results(results):
    """Check the raw results file on its own terms."""
    require(len(results) == N_TRIALS,
            "expected %d rows in the results file, found %d" % (N_TRIALS, len(results)))
    require(results["SubID"].nunique() == N_PARTICIPANTS,
            "expected %d participants, found %d" % (N_PARTICIPANTS, results["SubID"].nunique()))

    per_participant = results.groupby("SubID")["Trial"].agg(["size", "nunique", "min", "max"])
    require((per_participant["size"] == N_TRIALS_PER_PARTICIPANT).all(),
            "not every participant has exactly %d trials" % N_TRIALS_PER_PARTICIPANT)
    require((per_participant["nunique"] == N_TRIALS_PER_PARTICIPANT).all(),
            "some participants have duplicated trial numbers")
    require((per_participant["min"] == 1).all()
            and (per_participant["max"] == N_TRIALS_PER_PARTICIPANT).all(),
            "trial numbers are not a gapless 1..%d run for every participant"
            % N_TRIALS_PER_PARTICIPANT)

    require(results["Acc"].isin([0, 1]).all(), "Acc holds values other than 0 and 1")
    require(results["Exposure"].isin(EXPOSURE_DURATIONS).all(),
            "Exposure holds durations outside %r" % EXPOSURE_DURATIONS)
    # The exposure was thresholded once per participant, before the experiment.
    require((results.groupby("SubID")["Exposure"].nunique() == 1).all(),
            "some participants have more than one exposure duration")

    # DMDX stores the reaction time of an incorrect response as a negative number,
    # so the negative values have to be exactly the error trials.
    is_negative_rt = results["RT"] < 0
    is_error = results["Acc"] == 0
    require(is_negative_rt.sum() == is_error.sum(),
            "%d negative reaction times but %d incorrect responses"
            % (is_negative_rt.sum(), is_error.sum()))
    require(is_negative_rt.equals(is_error),
            "the negative reaction times are not exactly the incorrect responses")

    # The five-digit DMDX code reads as list | orthographic status | visual overlap |
    # item, so all four of its fields must agree with the columns that spell the
    # same thing out. This is what makes a scrambled results file detectable.
    code = results["DMDX"]
    require((code.str.len() == 5).all(), "not every DMDX code has five digits")
    tidy_status = results["OrthographicStatus"].map(
        lambda status: ORTHOGRAPHIC_STATUS[orthographic_key(status)][0])
    require(code.str[1].map(DMDX_CONTEXT_DIGIT).equals(tidy_status),
            "the second DMDX digit disagrees with OrthographicStatus")
    require(code.str[2].map(DMDX_OVERLAP_DIGIT).equals(results["VisualOverlap"].map(VISUAL_OVERLAP)),
            "the third DMDX digit disagrees with VisualOverlap")
    require(code.str[0].equals(results["List"]),
            "the first DMDX digit disagrees with List")
    require((code.str[3:5] == results["Item"]).all(),
            "the last two DMDX digits disagree with Item")


def check_stimuli(stimuli):
    """Check the item set itself, independently of any participant."""
    require(stimuli["Manipulation"].between(1, stimuli["Length"]).all(),
            "the probed position falls outside the string for some item")
    require(stimuli["Position"].str.lower().isin(POSITION_TYPES).all(),
            "the Position column holds something other than %r: %r"
            % (POSITION_TYPES, sorted(stimuli["Position"].unique())))

    for column in ("Spk_High", "Spk_Low"):
        require(stimuli[column].between(*SPEAKER_RATING_RANGE).all(),
                "column %s falls outside the %r rating scale" % (column, SPEAKER_RATING_RANGE))
    for column in ("HMAX_High", "HMAX_Low"):
        require(stimuli[column].between(*HMAX_RANGE).all(),
                "column %s falls outside %r" % (column, HMAX_RANGE))

    for column in STIMULUS_STRING_COLUMNS:
        require(stimuli[column].map(lambda value: isinstance(value, str) and value.isalpha()).all(),
                "column %s holds something that is not a letter string" % column)
        require((stimuli[column].str.len() == stimuli["Length"]).all(),
                "column %s disagrees with the Length column" % column)

    # A target and its alternative must differ in exactly one letter, and that one
    # letter must sit at the probed position; this is what makes the task two-choice.
    for _, item in stimuli.iterrows():
        expected_index = item["Manipulation"] - 1
        for prefix in ("WW", "PW", "CS"):
            for overlap in ("High", "Low"):
                target, alternative = item[prefix + "_Target"], item[prefix + "_" + overlap]
                differing = [index for index, (a, b) in enumerate(zip(target, alternative)) if a != b]
                require(differing == [expected_index],
                        "item %d (%s, %s overlap): %r and %r differ at positions %r, "
                        "expected position %d only"
                        % (item["item_number"], prefix, overlap.lower(),
                           target, alternative, differing, expected_index))


def check_letter_similarities(output):
    """Re-derive the two similarity columns from the letter-by-letter matrices.

    The workbook ships the full similarity matrix over the alphabet for both the
    human ratings and the HMAX model, and the item table was built from them. Look
    up each (target, distractor) pair in those matrices and the ratings carried by
    every trial have to come back. That checks the two rating columns, the pair of
    letters and the overlap condition at once, against a part of the workbook the
    item table was never read from -- so it also catches a re-exported sheet whose
    high- and low-overlap columns have been transposed.

    Only one half of each matrix is filled in, since similarity is symmetric.
    """
    pairs = output[["target_letter", "distractor_letter",
                    "letter_similarity_human", "letter_similarity_hmax"]].drop_duplicates()

    for column, sheet in SIMILARITY_SHEETS.items():
        matrix = pd.read_excel(STIMULI_FILE, sheet_name=sheet, header=0, index_col=0)
        matrix.index = [str(letter) for letter in matrix.index]
        matrix.columns = [str(letter) for letter in matrix.columns]

        for pair in pairs.itertuples(index=False):
            target, distractor = pair.target_letter, pair.distractor_letter
            require(target in matrix.index and distractor in matrix.columns,
                    "letter pair %r/%r is missing from sheet %r" % (target, distractor, sheet))
            expected = matrix.at[target, distractor]
            if pd.isna(expected):
                expected = matrix.at[distractor, target]
            found = getattr(pair, column)
            require(pd.notna(expected) and abs(expected - found) < 1e-9,
                    "%s for %r/%r is %r, but sheet %r gives %r"
                    % (column, target, distractor, found, sheet, expected))


def check_output(output, results):
    """Check the tidy table that is about to be written."""
    require(len(output) == N_TRIALS,
            "expected %d rows in the output, found %d" % (N_TRIALS, len(output)))
    require(list(output.columns) == COLUMN_ORDER,
            "unexpected output columns: %r" % list(output.columns))

    missing = output.isna().sum()
    require(missing.sum() == 0,
            "missing values in the output: %r" % missing[missing > 0].to_dict())

    require((output["rt"] >= 0).all(), "the output still holds negative reaction times")
    require(output["rt"].equals(results["RT"].abs()),
            "rt is not the magnitude of the RT column of the results file")
    require((output["target_letter"] != output["distractor_letter"]).all(),
            "some trials have identical target and distractor letters")
    require(output.apply(
        lambda row: row["stimulus"][row["letter_position"] - 1] == row["target_letter"],
        axis=1).all(),
        "the target letter is not the letter at the probed position of the stimulus")
    require((output["response"] == output["target_letter"]).equals(output["accuracy"] == 1),
            "the reconstructed response does not follow the accuracy column")

    # trial_id has to name the trial and nothing else: the same item in the same two
    # conditions must carry the same identifier for every participant who saw it,
    # whichever counterbalancing list they were in.
    require((output["dmdx_item_code"].str.len() == 5).all()
            and (output["trial_id"].str.len() == 4).all()
            and (output["trial_id"] == output["dmdx_item_code"].str[1:5]).all(),
            "trial_id is not the DMDX code without its leading list digit")
    trial = output[["stimulus_type", "condition", "stimulus"]].agg("|".join, axis=1)
    require(trial.groupby(output["trial_id"]).nunique().eq(1).all(),
            "one trial_id covers more than one distinct trial")
    require(trial.nunique() == output["trial_id"].nunique(),
            "%d distinct trials share only %d trial_id values"
            % (trial.nunique(), output["trial_id"].nunique()))
    require((output.groupby("participant_id")["trial_id"].nunique()
             == N_TRIALS_PER_PARTICIPANT).all(),
            "trial_id is not unique within every participant's session")

    cells = pd.crosstab(output["stimulus_type"], output["condition"])
    require(cells.shape == (3, 2) and (cells.to_numpy() == N_PER_DESIGN_CELL).all(),
            "the design is not balanced, cell counts are:\n%s" % cells)
    return cells


# --------------------------------------------------------------------------- #

def main():
    results = load_results()
    check_results(results)

    stimuli = load_stimuli()
    check_stimuli(stimuli)

    trials = build_trials(results, stimuli)
    output = trials[COLUMN_ORDER].copy()
    cells = check_output(output, results)
    check_letter_similarities(output)

    # Write through a temporary file so that a run interrupted mid-write leaves the
    # previous exp1.csv in place rather than a truncated one that still parses.
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    partial_file = OUT_FILE.with_name(OUT_FILE.name + ".partial")
    try:
        output.to_csv(partial_file, index=False, lineterminator="\n")
        os.replace(partial_file, OUT_FILE)
    finally:
        if partial_file.exists():
            partial_file.unlink()

    print("Lally & Rastle (2022) letter identification")
    print("Wrote processed CSV: %s" % OUT_FILE)
    print("Shape: %d rows x %d columns" % output.shape)
    print("Participants: %d, trials per participant: %s, items: %d"
          % (output["participant_id"].nunique(),
             sorted(output.groupby("participant_id").size().unique().tolist()), N_ITEMS))
    print("Exposure durations (ms): %s" % sorted(output["exposure_duration_ms"].unique().tolist()))
    print("Trials per list: %s" % output["list"].value_counts().sort_index().to_dict())
    print("Missing values: %d" % int(output.isna().sum().sum()))
    print("Accuracy: %.3f, RT (ms): mean %.1f, median %.1f, range %.2f-%.2f"
          % (output["accuracy"].mean(), output["rt"].mean(), output["rt"].median(),
             output["rt"].min(), output["rt"].max()))
    print(cells)
    print("All consistency checks passed.")


if __name__ == "__main__":
    main()
