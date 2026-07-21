from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ORIGINAL_DIR = BASE_DIR / "original_data"
OUTPUT_DIR = BASE_DIR / "processed_data"

RATINGS_INPUT = ORIGINAL_DIR / "Italian_Perceptual_Rating_raw.txt"
LEXICAL_DECISION_INPUT = ORIGINAL_DIR / "Italian_ANEW_Lexical_Decision_raw.txt"
NAMING_INPUT = ORIGINAL_DIR / "Italian_ANEW_Naming_raw.txt"

RATINGS_OUTPUT = OUTPUT_DIR / "exp1.csv"
LEXICAL_DECISION_OUTPUT = OUTPUT_DIR / "exp2.csv"
NAMING_OUTPUT = OUTPUT_DIR / "exp3.csv"

MISSING_VALUES = {"", "nan", "na", "n/a", "null", "none"}


def clean_text(value: str | None) -> str:
    """Remove unnecessary surrounding spaces while preserving missing values."""
    return "" if value is None else value.strip()


def is_missing(value: str | None) -> bool:
    """Identify common textual representations of missing values."""
    return clean_text(value).lower() in MISSING_VALUES


def normalise_number(
    value: str | None,
    column_name: str,
    row_number: int,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    require_integer: bool = False,
) -> str:
    """Validate a numeric value and preserve missing responses as empty cells."""
    if is_missing(value):
        return ""

    raw_value = clean_text(value)

    try:
        number = float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid value in column '{column_name}' at row {row_number}: "
            f"{raw_value}"
        ) from exc

    if math.isnan(number):
        return ""

    if minimum is not None and number < minimum:
        raise ValueError(
            f"Value below minimum in column '{column_name}' at row "
            f"{row_number}: {raw_value}"
        )

    if maximum is not None and number > maximum:
        raise ValueError(
            f"Value above maximum in column '{column_name}' at row "
            f"{row_number}: {raw_value}"
        )

    if require_integer and not number.is_integer():
        raise ValueError(
            f"Expected an integer in column '{column_name}' at row "
            f"{row_number}: {raw_value}"
        )

    return str(int(number)) if number.is_integer() else str(number)


def normalise_gender(value: str | None) -> str:
    """Convert the original gender labels into English lowercase labels."""
    value = clean_text(value).lower()

    mapping = {
        "f": "female",
        "female": "female",
        "m": "male",
        "male": "male",
    }

    return mapping.get(value, value)


def normalise_handedness(value: str | None) -> str:
    """Convert handedness labels to a consistent lowercase format."""
    value = clean_text(value).lower()

    mapping = {
        "r": "right",
        "right": "right",
        "l": "left",
        "left": "left",
        "a": "ambidextrous",
        "ambidextrous": "ambidextrous",
    }

    return mapping.get(value, value)


def normalise_stimulus_type(value: str | None) -> str:
    """Convert stimulus-type labels to a consistent format."""
    value = clean_text(value).lower()

    mapping = {
        "word": "word",
        "pseudoword": "pseudoword",
        "pseudo-word": "pseudoword",
        "nonword": "pseudoword",
        "non-word": "pseudoword",
    }

    if value not in mapping:
        raise ValueError(f"Unexpected stimulus type: {value}")

    return mapping[value]


def check_header(
    reader: csv.DictReader,
    expected_columns: list[str],
    input_file: Path,
) -> None:
    """Stop with an informative error if the raw-file structure has changed."""
    if reader.fieldnames != expected_columns:
        raise ValueError(
            f"Unexpected columns in: {input_file}\n"
            f"Expected: {expected_columns}\n"
            f"Found:    {reader.fieldnames}"
        )


def preprocess_perceptual_ratings() -> None:
    """Create the standardized CSV for Experiment 1."""
    expected_columns = [
        "Subject",
        "Age",
        "Gender",
        "Ita_Word",
        "Eng_Word",
        "Visual",
        "Gustatory",
        "Haptic",
        "Olfactory",
        "Auditory",
    ]

    output_columns = [
        "participant_id",
        "age",
        "gender",
        "trial_id",
        "condition",
        "stimulus",
        "stimulus_translation",
        "visual_rating",
        "gustatory_rating",
        "haptic_rating",
        "olfactory_rating",
        "auditory_rating",
    ]

    if not RATINGS_INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {RATINGS_INPUT}")

    participants: set[str] = set()
    row_counter: dict[str, int] = defaultdict(int)
    rows_written = 0
    incomplete_rating_rows = 0

    with RATINGS_INPUT.open("r", encoding="latin-1", newline="") as input_handle:
        reader = csv.DictReader(input_handle)
        check_header(reader, expected_columns, RATINGS_INPUT)

        with RATINGS_OUTPUT.open("w", encoding="utf-8", newline="") as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=output_columns)
            writer.writeheader()

            for row_number, row in enumerate(reader, start=2):
                participant_id = clean_text(row["Subject"])

                if participant_id == "":
                    raise ValueError(f"Missing participant ID at row {row_number}")

                row_index = row_counter[participant_id]
                row_counter[participant_id] += 1

                ratings = {
                    "visual_rating": normalise_number(
                        row["Visual"], "Visual", row_number, minimum=0, maximum=5
                    ),
                    "gustatory_rating": normalise_number(
                        row["Gustatory"], "Gustatory", row_number, minimum=0, maximum=5
                    ),
                    "haptic_rating": normalise_number(
                        row["Haptic"], "Haptic", row_number, minimum=0, maximum=5
                    ),
                    "olfactory_rating": normalise_number(
                        row["Olfactory"], "Olfactory", row_number, minimum=0, maximum=5
                    ),
                    "auditory_rating": normalise_number(
                        row["Auditory"], "Auditory", row_number, minimum=0, maximum=5
                    ),
                }

                if any(value == "" for value in ratings.values()):
                    incomplete_rating_rows += 1

                writer.writerow(
                    {
                        "participant_id": participant_id,
                        "age": normalise_number(
                            row["Age"], "Age", row_number, minimum=0
                        ),
                        "gender": normalise_gender(row["Gender"]),
                        "trial_id": f"rating_{participant_id}_{row_index:04d}",
                        "condition": "perceptual_strength_rating",
                        "stimulus": clean_text(row["Ita_Word"]),
                        "stimulus_translation": clean_text(row["Eng_Word"]),
                        **ratings,
                    }
                )

                participants.add(participant_id)
                rows_written += 1

    print("\nExperiment 1: perceptual-strength ratings")
    print(f"Input file:  {RATINGS_INPUT}")
    print(f"Output file: {RATINGS_OUTPUT}")
    print(f"Participants: {len(participants)}")
    print(f"Rows written: {rows_written}")
    print(f"Rows with at least one missing rating: {incomplete_rating_rows}")


def preprocess_lexical_decision() -> None:
    """Create the standardized CSV for Experiment 2."""
    expected_columns = [
        "Subject",
        "Age",
        "Gender",
        "Scolarity",
        "Handedness",
        "Session",
        "Stimulus_Type",
        "Ita_Word",
        "Eng_Word",
        "Accuracy",
        "RTs",
    ]

    output_columns = [
        "participant_id",
        "age",
        "gender",
        "education",
        "handedness",
        "session_id",
        "trial_id",
        "condition",
        "stimulus_type",
        "stimulus",
        "stimulus_translation",
        "accuracy",
        "rt",
    ]

    if not LEXICAL_DECISION_INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {LEXICAL_DECISION_INPUT}")

    participants: set[str] = set()
    sessions: set[tuple[str, str]] = set()
    row_counter: dict[tuple[str, str], int] = defaultdict(int)
    rows_written = 0
    missing_rt_rows = 0
    word_trials = 0
    pseudoword_trials = 0

    with LEXICAL_DECISION_INPUT.open(
        "r", encoding="latin-1", newline=""
    ) as input_handle:
        reader = csv.DictReader(input_handle)
        check_header(reader, expected_columns, LEXICAL_DECISION_INPUT)

        with LEXICAL_DECISION_OUTPUT.open(
            "w", encoding="utf-8", newline=""
        ) as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=output_columns)
            writer.writeheader()

            for row_number, row in enumerate(reader, start=2):
                participant_id = clean_text(row["Subject"])
                session_id = normalise_number(
                    row["Session"],
                    "Session",
                    row_number,
                    minimum=0,
                    require_integer=True,
                )

                if participant_id == "":
                    raise ValueError(f"Missing participant ID at row {row_number}")

                if session_id == "":
                    raise ValueError(f"Missing session ID at row {row_number}")

                session_key = (participant_id, session_id)
                row_index = row_counter[session_key]
                row_counter[session_key] += 1

                stimulus_type = normalise_stimulus_type(row["Stimulus_Type"])

                if stimulus_type == "word":
                    word_trials += 1
                else:
                    pseudoword_trials += 1

                rt = normalise_number(row["RTs"], "RTs", row_number, minimum=0)

                if rt == "":
                    missing_rt_rows += 1

                writer.writerow(
                    {
                        "participant_id": participant_id,
                        "age": normalise_number(
                            row["Age"], "Age", row_number, minimum=0
                        ),
                        "gender": normalise_gender(row["Gender"]),
                        "education": normalise_number(
                            row["Scolarity"], "Scolarity", row_number, minimum=0
                        ),
                        "handedness": normalise_handedness(row["Handedness"]),
                        "session_id": session_id,
                        "trial_id": f"ldt_{participant_id}_{session_id}_{row_index:04d}",
                        "condition": "lexical_decision",
                        "stimulus_type": stimulus_type,
                        "stimulus": clean_text(row["Ita_Word"]),
                        "stimulus_translation": clean_text(row["Eng_Word"]),
                        "accuracy": normalise_number(
                            row["Accuracy"],
                            "Accuracy",
                            row_number,
                            minimum=0,
                            maximum=1,
                            require_integer=True,
                        ),
                        "rt": rt,
                    }
                )

                participants.add(participant_id)
                sessions.add(session_key)
                rows_written += 1

    print("\nExperiment 2: lexical decision")
    print(f"Input file:  {LEXICAL_DECISION_INPUT}")
    print(f"Output file: {LEXICAL_DECISION_OUTPUT}")
    print(f"Participants in released raw file: {len(participants)}")
    print(f"Sessions: {len(sessions)}")
    print(f"Rows written: {rows_written}")
    print(f"Word trials: {word_trials}")
    print(f"Pseudoword trials: {pseudoword_trials}")
    print(f"Rows with missing RT: {missing_rt_rows}")


def preprocess_naming() -> None:
    """Create the standardized CSV for Experiment 3."""
    expected_columns = [
        "Subject",
        "Age",
        "Gender",
        "Scolarity",
        "Handedness",
        "Session",
        "Ita_Word",
        "Eng_Word",
        "Accuracy",
        "RTs",
    ]

    output_columns = [
        "participant_id",
        "age",
        "gender",
        "education",
        "handedness",
        "session_id",
        "trial_id",
        "condition",
        "stimulus",
        "stimulus_translation",
        "accuracy",
        "rt",
    ]

    if not NAMING_INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {NAMING_INPUT}")

    participants: set[str] = set()
    sessions: set[tuple[str, str]] = set()
    row_counter: dict[tuple[str, str], int] = defaultdict(int)
    rows_written = 0
    missing_rt_rows = 0

    with NAMING_INPUT.open("r", encoding="latin-1", newline="") as input_handle:
        reader = csv.DictReader(input_handle)
        check_header(reader, expected_columns, NAMING_INPUT)

        with NAMING_OUTPUT.open("w", encoding="utf-8", newline="") as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=output_columns)
            writer.writeheader()

            for row_number, row in enumerate(reader, start=2):
                participant_id = clean_text(row["Subject"])
                session_id = normalise_number(
                    row["Session"],
                    "Session",
                    row_number,
                    minimum=0,
                    require_integer=True,
                )

                if participant_id == "":
                    raise ValueError(f"Missing participant ID at row {row_number}")

                if session_id == "":
                    raise ValueError(f"Missing session ID at row {row_number}")

                session_key = (participant_id, session_id)
                row_index = row_counter[session_key]
                row_counter[session_key] += 1

                rt = normalise_number(row["RTs"], "RTs", row_number, minimum=0)

                if rt == "":
                    missing_rt_rows += 1

                writer.writerow(
                    {
                        "participant_id": participant_id,
                        "age": normalise_number(
                            row["Age"], "Age", row_number, minimum=0
                        ),
                        "gender": normalise_gender(row["Gender"]),
                        "education": normalise_number(
                            row["Scolarity"], "Scolarity", row_number, minimum=0
                        ),
                        "handedness": normalise_handedness(row["Handedness"]),
                        "session_id": session_id,
                        "trial_id": (
                            f"naming_{participant_id}_{session_id}_{row_index:04d}"
                        ),
                        "condition": "word_naming",
                        "stimulus": clean_text(row["Ita_Word"]),
                        "stimulus_translation": clean_text(row["Eng_Word"]),
                        "accuracy": normalise_number(
                            row["Accuracy"],
                            "Accuracy",
                            row_number,
                            minimum=0,
                            maximum=1,
                            require_integer=True,
                        ),
                        "rt": rt,
                    }
                )

                participants.add(participant_id)
                sessions.add(session_key)
                rows_written += 1

    print("\nExperiment 3: word naming")
    print(f"Input file:  {NAMING_INPUT}")
    print(f"Output file: {NAMING_OUTPUT}")
    print(f"Participants: {len(participants)}")
    print(f"Sessions: {len(sessions)}")
    print(f"Rows written: {rows_written}")
    print(f"Rows with missing RT: {missing_rt_rows}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    preprocess_perceptual_ratings()
    preprocess_lexical_decision()
    preprocess_naming()

    print("\nPreprocessing completed successfully.")
    print("Note: trial_id values are technical row identifiers generated during preprocessing.")
    print("They do not encode the real presentation order of the trials.")


if __name__ == "__main__":
    main()
