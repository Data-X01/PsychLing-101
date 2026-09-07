"""Turn the processed Lally & Rastle (2022) trials into one prompt per participant.

Reads
-----
processed_data/exp1.csv
    The tidy trial table written by preprocess_data.py.

Writes
------
prompts.jsonl.zip
    One JSON object per line, one line per participant, with the fields text,
    experiment, participant_id, rt and exposure_duration_ms. The uncompressed
    prompts.jsonl is written first and removed once it has been compressed.

Rendering the task in text
--------------------------
The instruction lines are reproduced verbatim from the experiment script,
including the button box and the spacebar: the prompt describes the situation
the participant was actually in. Only the blank lines between them are inferred,
from the <ln> screen geometry described at INSTRUCTION_LINES below. Nothing is
added to the wording, and the exposure duration, which the instructions never
mention, is carried as a field of the record rather than written into the text.

The letter string is given in full, as it was displayed. The prompt is a
transcript of what was on the screen, not of what the participant managed to
take in: 'snow' really was presented, and that it went by too fast to read is a
fact about their perception rather than about the display. This is the same
reasoning that keeps the button box and the spacebar in the instructions.

Both measured quantities are marked with << >>: the letter the participant
chose and the time they took. The exposure duration is constant within a
session, so it is stated once between the instruction and the first trial
instead of being repeated on every line.

No feedback is shown after a trial. The DMDX script sets <nfb>, so participants
were never told whether a response was correct, and the prompts must not tell a
model either. This departs from the worked example in the repository README,
whose experiment did give feedback.

Which candidate letter appeared above and which below is not recorded in the
results file, so the order the two options are offered in is randomised per
participant, from a seed derived from the participant identifier. Re-running the
script therefore reproduces the archive byte for byte.

All paths are relative: run the script from this contribution folder.
"""

import hashlib
import json
import random
import re
import zipfile
from pathlib import Path

import pandas as pd

PROCESSED_DATA_DIR = Path("processed_data")
TRIALS_FILE = PROCESSED_DATA_DIR / "exp1.csv"
PROMPTS_FILE = Path("prompts.jsonl")
ARCHIVE_FILE = Path("prompts.jsonl.zip")

EXPERIMENT = "lally2022_letter_identification/exp1"

N_PARTICIPANTS = 72
N_TRIALS_PER_PARTICIPANT = 144
N_TRIALS = N_PARTICIPANTS * N_TRIALS_PER_PARTICIPANT
TOKEN_LIMIT = 32000

# Both measured quantities are marked: the letter chosen and the time taken.
TRIAL_TEMPLATE = ("Trial %d: The letter string was '%s'. The letters '%s' and '%s' "
                  "appeared above and below the %s position. You press <<%s>>. "
                  "RT: <<%d>> ms.")
MARKERS_PER_TRIAL = 2
# The probed position is named in words, the way the display would be described.
# The table covers every position a 4- to 6-letter string has, not only the ones
# this data set happens to probe (positions 2 to 5), so that the lookup stays
# total and ordinal() raises on anything outside that range instead of guessing.
ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth")

# The instruction screen of the experiment, verbatim from the DMDX script in
# original_data/Stimuli & Experiments/FeatureCues_ExampleScript.rtf, reproduced
# without alteration. The <ln> offsets there run -5, -4, -2, -1, 0, 1, 2, 3, 4,
# 6, 7, which puts a blank line after the second and after the ninth line; those
# gaps are kept. The exposure duration is not mentioned on this screen and is
# not added to it; it travels with the record as its own field instead.
INSTRUCTION_LINES = (
    "In this experiment, you will be asked to make a decision",
    "about which letter appeared in a letter string.",
    "",
    "You will be presented with one letter string at a time.",
    "Before and after the letter string,",
    "each letter will be covered like this: #####.",
    "A letter will then appear above and below one of the # symbols.",
    "Your task is to decide which letter appeared in this position,",
    "as QUICKLY and as ACCURATELY as possible.",
    "You will have 5 seconds to make a response.",
    "",
    "Use the button box to indicate which letter appeared within the letter string.",
    "Press the SPACEBAR to begin the experiment.",
)
INSTRUCTION = "\n".join(INSTRUCTION_LINES)

# Exposure duration is constant within a session and differs between participants,
# so it is stated once after the instruction rather than repeated on every trial.
# It is kept out of the instruction itself because the original screen never
# mentions it, and that screen is reproduced unaltered.
EXPOSURE_NOTE = "In this session each letter string was shown for %d ms."


def require(condition, message):
    """Abort with an explicit message when a consistency check fails."""
    if not condition:
        raise ValueError("Consistency check failed: " + message)


def load_trials():
    """Read the processed trials, ordered as the participants saw them."""
    if not TRIALS_FILE.exists():
        raise FileNotFoundError(
            "Missing input file: %s. Run preprocess_data.py first." % TRIALS_FILE)

    trials = pd.read_csv(TRIALS_FILE, dtype={"participant_id": str})
    needed = ["participant_id", "trial_order", "stimulus", "letter_position",
              "target_letter", "distractor_letter", "response", "accuracy",
              "rt", "exposure_duration_ms"]
    missing = [column for column in needed if column not in trials.columns]
    require(not missing, "%s is missing the columns %r" % (TRIALS_FILE, missing))
    return trials.sort_values(["participant_id", "trial_order"]).reset_index(drop=True)


def ordinal(letter_position):
    """Name a 1-indexed position in words (2 -> "second")."""
    require(1 <= letter_position <= len(ORDINALS),
            "no ordinal for position %r" % letter_position)
    return ORDINALS[letter_position - 1]


def participant_rng(participant_id):
    """A generator seeded from the participant identifier alone.

    Seeding from a hash of the identifier rather than from the loop counter keeps
    each participant's option order stable no matter what else the script does,
    and keeps it reproducible across runs and across machines.
    """
    digest = hashlib.sha256(participant_id.encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def build_prompt(participant_trials):
    """Render one participant's whole session as a single prompt."""
    rng = participant_rng(participant_trials["participant_id"].iloc[0])
    exposure = int(participant_trials["exposure_duration_ms"].iloc[0])

    lines = [INSTRUCTION, "", EXPOSURE_NOTE % exposure, ""]
    for number, trial in enumerate(participant_trials.itertuples(index=False), start=1):
        options = [trial.target_letter, trial.distractor_letter]
        rng.shuffle(options)
        lines.append(TRIAL_TEMPLATE % (
            number, trial.stimulus, options[0], options[1],
            ordinal(trial.letter_position), trial.response,
            round(float(trial.rt))))
    return "\n".join(lines)


def build_records(trials):
    """One JSON-ready record per participant."""
    records = []
    for participant_id, participant_trials in trials.groupby("participant_id", sort=True):
        require(len(participant_trials) == N_TRIALS_PER_PARTICIPANT,
                "participant %s has %d trials, expected %d"
                % (participant_id, len(participant_trials), N_TRIALS_PER_PARTICIPANT))
        require(participant_trials["exposure_duration_ms"].nunique() == 1,
                "participant %s has more than one exposure duration" % participant_id)
        records.append({
            "text": build_prompt(participant_trials),
            "experiment": EXPERIMENT,
            "participant_id": participant_id,
            "rt": participant_trials["rt"].tolist(),
            # Calibrated per participant and constant within a session. It is
            # metadata rather than instruction text: the participants were never
            # told their exposure duration.
            "exposure_duration_ms": int(participant_trials["exposure_duration_ms"].iloc[0]),
        })
    return records


def estimate_tokens(text):
    """A deliberately generous token estimate, using no tokeniser.

    Counting word and punctuation pieces underestimates subword splitting, and
    one token per four characters is the usual rule of thumb for English, so the
    larger of the two is reported and the word count is inflated by a fifth.
    """
    pieces = len(re.findall(r"\w+|[^\w\s]", text))
    return int(max(pieces * 1.2, len(text) / 4)) + 1


def check_records(records, trials):
    """Everything that has to hold of the finished prompts."""
    require(len(records) == N_PARTICIPANTS,
            "expected %d records, found %d" % (N_PARTICIPANTS, len(records)))

    by_participant = dict(tuple(trials.groupby("participant_id", sort=True)))
    worst_tokens, worst_participant = 0, None

    for record in records:
        participant_id = record["participant_id"]
        text = record["text"]
        participant_trials = by_participant[participant_id]

        trial_lines = [line for line in text.split("\n") if line.startswith("Trial ")]
        require(len(trial_lines) == N_TRIALS_PER_PARTICIPANT,
                "participant %s has %d trial lines, expected %d"
                % (participant_id, len(trial_lines), N_TRIALS_PER_PARTICIPANT))
        expected_markers = N_TRIALS_PER_PARTICIPANT * MARKERS_PER_TRIAL
        require(text.count("<<") == expected_markers and text.count(">>") == expected_markers,
                "participant %s has %d/%d << >> markers, expected %d of each"
                % (participant_id, text.count("<<"), text.count(">>"), expected_markers))

        # The instruction screen must survive assembly unaltered, and the exposure
        # duration must be stated once, with this participant's own value.
        require(text.startswith(INSTRUCTION + "\n\n"),
                "participant %s: the prompt does not open with the instruction screen"
                % participant_id)
        exposure = int(participant_trials["exposure_duration_ms"].iloc[0])
        note = EXPOSURE_NOTE % exposure
        require(text.count(note) == 1,
                "participant %s: %r appears %d times, expected once"
                % (participant_id, note, text.count(note)))
        require(text.startswith(INSTRUCTION + "\n\n" + note + "\n\n"),
                "participant %s: the exposure note is not between the instruction "
                "and the first trial" % participant_id)
        require(sum(line.startswith("In this session") for line in text.split("\n")) == 1,
                "participant %s: more than one exposure note" % participant_id)

        # No feedback was given in the experiment, so none may leak into the prompt.
        for word in ("Correct", "Incorrect"):
            require(word not in text,
                    "participant %s: the prompt contains %r" % (participant_id, word))

        require(len(record["rt"]) == N_TRIALS_PER_PARTICIPANT,
                "participant %s has %d reaction times, expected %d"
                % (participant_id, len(record["rt"]), N_TRIALS_PER_PARTICIPANT))

        for line, trial in zip(trial_lines, participant_trials.itertuples(index=False)):
            # The prompt transcribes the display, so the string that was shown has
            # to be there in full, together with both letters that were offered.
            require("'%s'" % trial.stimulus in line,
                    "participant %s: %r does not carry the letter string %r"
                    % (participant_id, line, trial.stimulus))
            for letter in (trial.target_letter, trial.distractor_letter):
                require("'%s'" % letter in line,
                        "participant %s: %r does not offer the candidate letter %r"
                        % (participant_id, line, letter))
            # The position named in words has to be the position that was probed.
            require(" %s position" % ordinal(trial.letter_position) in line,
                    "participant %s: %r does not name position %d as %r"
                    % (participant_id, line, trial.letter_position,
                       ordinal(trial.letter_position)))
            # The second marked value is this trial's reaction time, rounded to a
            # whole millisecond.
            require("RT: <<%d>> ms." % round(float(trial.rt)) in line,
                    "participant %s: %r does not carry the reaction time %r"
                    % (participant_id, line, trial.rt))
            # The response is one of the two candidates, and it agrees with accuracy.
            require(trial.response in (trial.target_letter, trial.distractor_letter),
                    "participant %s, string %r: the response %r is neither candidate"
                    % (participant_id, trial.stimulus, trial.response))
            require((trial.response == trial.target_letter) == (trial.accuracy == 1),
                    "participant %s, string %r: the chosen letter disagrees with accuracy"
                    % (participant_id, trial.stimulus))

        tokens = estimate_tokens(text)
        if tokens > worst_tokens:
            worst_tokens, worst_participant = tokens, participant_id

    require(worst_tokens <= TOKEN_LIMIT,
            "participant %s needs about %d tokens, over the limit of %d"
            % (worst_participant, worst_tokens, TOKEN_LIMIT))
    return worst_tokens, worst_participant


def write_archive(records):
    """Write prompts.jsonl, compress it, drop the uncompressed copy.

    The zip entry carries a fixed timestamp instead of the file's modification
    time, which is what lets two runs produce byte-identical archives.
    """
    previous = ARCHIVE_FILE.read_bytes() if ARCHIVE_FILE.exists() else None

    with PROMPTS_FILE.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    entry = zipfile.ZipInfo(PROMPTS_FILE.name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o644 << 16
    with zipfile.ZipFile(ARCHIVE_FILE, "w") as archive:
        archive.writestr(entry, PROMPTS_FILE.read_bytes())
    PROMPTS_FILE.unlink()

    written = ARCHIVE_FILE.read_bytes()
    return hashlib.sha256(written).hexdigest(), previous, written


def main():
    trials = load_trials()
    require(len(trials) == N_TRIALS,
            "expected %d trials, found %d" % (N_TRIALS, len(trials)))

    records = build_records(trials)
    worst_tokens, worst_participant = check_records(records, trials)
    digest, previous, written = write_archive(records)

    print("Lally & Rastle (2022) letter identification")
    print("Wrote %s (%d bytes) with %d prompts, one per participant"
          % (ARCHIVE_FILE, len(written), len(records)))
    print("Trials per prompt: %d, reaction times per record: %d"
          % (N_TRIALS_PER_PARTICIPANT, N_TRIALS_PER_PARTICIPANT))
    print("Largest prompt: about %d tokens (participant %s), limit %d"
          % (worst_tokens, worst_participant, TOKEN_LIMIT))
    print("SHA-256: %s" % digest)
    if previous is None:
        print("Reproducibility: no earlier archive to compare against; "
              "run again to confirm the bytes repeat.")
    else:
        print("Reproducibility: %s the archive from the previous run."
              % ("byte-identical to" if previous == written else "DIFFERENT from"))
        require(previous == written, "a repeated run produced a different archive")
    print("All consistency checks passed.")


if __name__ == "__main__":
    main()
