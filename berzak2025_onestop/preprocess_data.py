"""Preprocess OneStop Eye Movements (Berzak et al., 2025) for PsychLing-101.

Reads the interest area report in original_data/ and writes two tidy,
trial-level CSVs to processed_data/, split by the reading-goal manipulation.

    exp1.csv  ordinary reading for comprehension
    exp2.csv  information seeking (question shown before the paragraph)

One row = one word (interest area) read by one participant on one trial.

Notes on the source data handled here
-------------------------------------
* The source is a 5.6 GB CSV with 157 columns inside a zip. It is streamed
  rather than loaded, and only the measured eye-movement columns are kept.
  The precomputed linguistic annotations (frequency, GPT-2 surprisal, POS,
  dependency trees) are dropped, since they are derived rather than observed
  and are recomputable from the stimulus text.
* Practice trials are excluded. The dataset is described by its authors as
  19,438 regular and 3,888 repeated-reading trials, which are the trials kept
  here. Repeated readings are retained and flagged.
* The four answer options were displayed in a per-trial randomised order. They
  are joined into a single answer_options column in the order they appeared on
  screen, written once per trial on the row where word_position is 1. Repeating
  the option text on all 2.5 million word rows would add several hundred MB of
  duplicated text.
"""

import csv
import io
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
ORIGINAL_DIR = BASE_DIR / "original_data"
PROCESSED_DIR = BASE_DIR / "processed_data"

SOURCE_ZIP = ORIGINAL_DIR / "ia_Paragraph.csv.zip"
SOURCE_MEMBER = "ia_Paragraph.csv"
SESSION_FILE = ORIGINAL_DIR / "session_summary.csv"

# Source column -> output column, for values carried on every word row.
WORD_COLUMNS = {
    "IA_ID": "word_position",
    "IA_LABEL": "stimulus",
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

# Canonical answer label -> source column holding that option's text.
LABEL_TO_COLUMN = {"A": "answer_1", "B": "answer_2", "C": "answer_3", "D": "answer_4"}

# Separator between the four answer options in the answer_options column.
OPTION_SEPARATOR = " | "

OUTPUT_COLUMNS = [
    "participant_id",
    "trial_order",
    "article_id",
    "paragraph_id",
    "difficulty_level",
    "is_repeated_reading",
    "word_position",
    "stimulus",
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
    "question",
    "answer_options",
    "correct_answer_position",
    "response_position",
    "accuracy",
    "question_rt",
    "answer_rt",
    "comprehension_score",
    "lextale_score",
]

BOOL_MAP = {"True": 1, "False": 0, "TRUE": 1, "FALSE": 0}


def answer_options(row: list, idx: dict) -> str:
    """Return the four answer options in the order they appeared on screen."""
    raw_order = row[idx["answers_order"]]
    labels = [part.strip(" '\"[]") for part in raw_order.split(",")]
    texts = []
    for label in labels[:4]:
        column = LABEL_TO_COLUMN.get(label)
        texts.append(row[idx[column]] if column else "")
    return OPTION_SEPARATOR.join(texts)


def load_session_metadata() -> dict:
    """Return {participant_id: (comprehension_score, lextale_score)}."""
    meta = {}
    with open(SESSION_FILE, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            meta[row["participant_id"]] = (
                row.get("comprehension_score-regular_trials", ""),
                row.get("lextale_score", ""),
            )
    return meta


def main() -> None:
    PROCESSED_DIR.mkdir(exist_ok=True)
    session_meta = load_session_metadata()

    participants = {}
    counts = {"exp1": 0, "exp2": 0}
    trials = {"exp1": set(), "exp2": set()}
    skipped_practice = 0

    out_files = {}
    writers = {}
    for name in ("exp1", "exp2"):
        fh = open(PROCESSED_DIR / f"{name}.csv", "w", encoding="utf-8", newline="")
        out_files[name] = fh
        writers[name] = csv.writer(fh)
        writers[name].writerow(OUTPUT_COLUMNS)

    with zipfile.ZipFile(SOURCE_ZIP) as zf:
        with zf.open(SOURCE_MEMBER) as raw:
            stream = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
            reader = csv.reader(stream)
            header = next(reader)
            idx = {name: i for i, name in enumerate(header)}

            for row in reader:
                if row[idx["practice_trial"]] in ("True", "TRUE"):
                    skipped_practice += 1
                    continue

                is_seeking = row[idx["question_preview"]] in ("True", "TRUE")
                target = "exp2" if is_seeking else "exp1"

                raw_pid = row[idx["participant_id"]]
                if raw_pid not in participants:
                    participants[raw_pid] = len(participants) + 1
                participant_id = participants[raw_pid]

                word_position = row[idx["IA_ID"]]
                first_word = word_position == "1"

                dwell = row[idx["IA_DWELL_TIME"]]
                try:
                    is_fixated = 1 if float(dwell) > 0 else 0
                except ValueError:
                    is_fixated = ""

                comprehension, lextale = session_meta.get(raw_pid, ("", ""))

                record = {
                    "participant_id": participant_id,
                    "trial_order": row[idx["trial_index"]],
                    "article_id": row[idx["article_id"]],
                    "paragraph_id": row[idx["paragraph_id"]],
                    "difficulty_level": row[idx["difficulty_level"]],
                    "is_repeated_reading": BOOL_MAP.get(
                        row[idx["repeated_reading_trial"]], ""
                    ),
                    "is_fixated": is_fixated,
                    "correct_answer_position": row[idx["correct_answer_position"]],
                    "response_position": row[idx["selected_answer_position"]],
                    "accuracy": BOOL_MAP.get(row[idx["is_correct"]], ""),
                    "question": row[idx["question"]],
                    "question_rt": row[idx["QUESTION_RT"]],
                    "answer_rt": row[idx["ANSWER_RT"]],
                    "comprehension_score": comprehension,
                    "lextale_score": lextale,
                }
                for src, dst in WORD_COLUMNS.items():
                    record[dst] = row[idx[src]]
                record["answer_options"] = (
                    answer_options(row, idx) if first_word else ""
                )

                writers[target].writerow([record[c] for c in OUTPUT_COLUMNS])
                counts[target] += 1
                trials[target].add((participant_id, record["trial_order"]))

    for fh in out_files.values():
        fh.close()

    print("Wrote processed_data/exp1.csv (ordinary reading) "
          f"and processed_data/exp2.csv (information seeking)")
    print(f"  participants:        {len(participants)}")
    print(f"  exp1 rows / trials:  {counts['exp1']:,} / {len(trials['exp1']):,}")
    print(f"  exp2 rows / trials:  {counts['exp2']:,} / {len(trials['exp2']):,}")
    print(f"  practice rows dropped: {skipped_practice:,}")


if __name__ == "__main__":
    main()
