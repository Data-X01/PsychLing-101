import csv
from collections import Counter
from pathlib import Path

# ============================================================
# Paths
# ============================================================

DATASET_DIR = Path(__file__).resolve().parent
INPUT_FILE = DATASET_DIR / "original_data" / "DATA_AllRatings_raw.csv"
OUTPUT_DIR = DATASET_DIR / "processed_data"
OUTPUT_FILE = OUTPUT_DIR / "exp1.csv"

# ============================================================
# Source-file structure
# ============================================================

# Metadata used to identify the four rows belonging to the same
# participant-session-list block.
GROUP_COLUMNS = [
    "ResponseIdQualtrics",
    "IDsubj",
    "gender",
    "age",
    "POS",
    "List",
]

# All non-stimulus columns present in the original wide-format file.
# Only the first seven substantive metadata fields are retained in the
# processed dataset. The remaining source columns are intentionally
# excluded and must not be treated as word stimuli.
SOURCE_METADATA_COLUMNS = {
    "RatingScale",
    "POS",
    "List",
    "ResponseIdQualtrics",
    "IDsubj",
    "gender",
    "age",
    "Duration",
    "arousal_correlation",
    "dominance_correlation",
    "valence_correlation",
    "MissingResponsePercentages",
    "IdenticalResponsePercentage",
    "Unknown",
}

EXPECTED_SCALES = {
    "Val",
    "Aro",
    "Dom",
    "Unk",
}

EXPECTED_PARTS_OF_SPEECH = {
    "Adj",
    "Nou",
    "Ver",
}

MISSING_VALUES = {
    "",
    "nan",
    "na",
    "n/a",
}

VALID_VAD_VALUES = {
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
}

VALID_UNKNOWN_VALUES = {
    "0",
    "1",
}

OUTPUT_COLUMNS = [
    "participant_id",
    "session_id",
    "gender",
    "age",
    "part_of_speech",
    "list_id",
    "trial_id",
    "stimulus",
    "valence",
    "arousal",
    "dominance",
    "unknown_word",
]


def clean(value):
    """Return a stripped string representation of a cell."""
    if value is None:
        return ""

    return value.strip()


def is_missing(value):
    """
    Return True when a cell contains a missing value.

    In the source file, NaN indicates that a rating was not recorded.
    """
    return clean(value).lower() in MISSING_VALUES


def output_value(value):
    """Represent missing values as empty cells in the processed CSV."""
    if is_missing(value):
        return ""

    return clean(value)


def normalise_row_length(row, expected_length):
    """
    Make row length match the header length.

    This prevents silent column misalignment if malformed source rows
    are encountered.
    """
    if len(row) < expected_length:
        return row + [""] * (expected_length - len(row))

    if len(row) > expected_length:
        return row[:expected_length]

    return row


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ========================================================
    # Read the source file and group scale-specific rows
    # ========================================================

    groups = {}

    source_rows = 0
    malformed_source_rows = 0

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as input_handle:
        reader = csv.reader(input_handle)
        header = next(reader)

        required_columns = (
            set(GROUP_COLUMNS)
            | {"RatingScale"}
        )

        missing_required_columns = sorted(
            required_columns - set(header)
        )

        if missing_required_columns:
            raise ValueError(
                "Required source columns are missing: "
                + ", ".join(missing_required_columns)
            )

        column_positions = {
            column_name: header.index(column_name)
            for column_name in required_columns
        }

        stimulus_indices = [
            index
            for index, column_name in enumerate(header)
            if column_name not in SOURCE_METADATA_COLUMNS
        ]

        stimulus_names = [
            header[index]
            for index in stimulus_indices
        ]

        duplicate_stimulus_names = (
            len(stimulus_names)
            - len(set(stimulus_names))
        )

        for source_line_number, row in enumerate(
            reader,
            start=2,
        ):
            source_rows += 1

            if len(row) != len(header):
                malformed_source_rows += 1
                row = normalise_row_length(
                    row,
                    len(header),
                )

            rating_scale = clean(
                row[column_positions["RatingScale"]]
            )

            if rating_scale not in EXPECTED_SCALES:
                raise ValueError(
                    f"Unexpected RatingScale value "
                    f"{rating_scale!r} at source line "
                    f"{source_line_number}"
                )

            part_of_speech = clean(
                row[column_positions["POS"]]
            )

            if part_of_speech not in EXPECTED_PARTS_OF_SPEECH:
                raise ValueError(
                    f"Unexpected POS value "
                    f"{part_of_speech!r} at source line "
                    f"{source_line_number}"
                )

            group_key = tuple(
                clean(row[column_positions[column_name]])
                for column_name in GROUP_COLUMNS
            )

            if group_key not in groups:
                groups[group_key] = {
                    "first_source_line": source_line_number,
                    "rows_by_scale": {},
                }

            rows_by_scale = groups[group_key]["rows_by_scale"]

            if rating_scale in rows_by_scale:
                raise ValueError(
                    f"Duplicate source row for scale "
                    f"{rating_scale!r} at line "
                    f"{source_line_number}"
                )

            rows_by_scale[rating_scale] = row

    # ========================================================
    # Validate source blocks
    # ========================================================

    incomplete_groups = []

    for group_key, group_data in groups.items():
        observed_scales = set(
            group_data["rows_by_scale"]
        )

        if observed_scales != EXPECTED_SCALES:
            incomplete_groups.append(
                (
                    group_key,
                    sorted(observed_scales),
                )
            )

    if incomplete_groups:
        example_group, example_scales = incomplete_groups[0]

        raise ValueError(
            "Some participant-session-list blocks do not contain "
            "exactly one row for each expected scale. "
            f"Example group: {example_group!r}; "
            f"observed scales: {example_scales!r}"
        )

    # ========================================================
    # Combine the four source rows into trial-level records
    # ========================================================

    trial_rows_written = 0
    excluded_columns_without_vad = 0
    excluded_unknown_only_rows = 0

    rows_by_pos = Counter()
    unknown_word_values = Counter()

    missing_valence = 0
    missing_arousal = 0
    missing_dominance = 0
    missing_unknown_word = 0

    unexpected_vad_values = Counter()
    unexpected_unknown_values = Counter()

    unknown_word_selected = 0

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as output_handle:
        writer = csv.DictWriter(
            output_handle,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()

        for group_data in groups.values():
            rows_by_scale = group_data["rows_by_scale"]

            reference_row = rows_by_scale["Unk"]

            participant_id = clean(
                reference_row[
                    column_positions["IDsubj"]
                ]
            )

            session_id = clean(
                reference_row[
                    column_positions["ResponseIdQualtrics"]
                ]
            )

            gender = clean(
                reference_row[
                    column_positions["gender"]
                ]
            )

            age = clean(
                reference_row[
                    column_positions["age"]
                ]
            )

            part_of_speech = clean(
                reference_row[
                    column_positions["POS"]
                ]
            )

            list_id = clean(
                reference_row[
                    column_positions["List"]
                ]
            )

            first_source_line = group_data[
                "first_source_line"
            ]

            for source_column_index in stimulus_indices:
                valence = clean(
                    rows_by_scale["Val"][
                        source_column_index
                    ]
                )

                arousal = clean(
                    rows_by_scale["Aro"][
                        source_column_index
                    ]
                )

                dominance = clean(
                    rows_by_scale["Dom"][
                        source_column_index
                    ]
                )

                unknown_word = clean(
                    rows_by_scale["Unk"][
                        source_column_index
                    ]
                )

                # Retain a trial only when at least one affective
                # response was recorded. An unknown-word checkbox
                # value alone is not sufficient to define a valid
                # processed trial.
                if all(
                    is_missing(value)
                    for value in (
                        valence,
                        arousal,
                        dominance,
                    )
                ):
                    excluded_columns_without_vad += 1

                    if not is_missing(unknown_word):
                        excluded_unknown_only_rows += 1

                    continue

                stimulus = clean(
                    header[source_column_index]
                )

                # Synthetic unique identifier for the observed trial.
                # It allows the corresponding raw-file position to be
                # recovered but does not represent temporal order.
                trial_id = (
                    f"r{first_source_line:06d}_"
                    f"c{source_column_index:06d}"
                )

                writer.writerow(
                    {
                        "participant_id": participant_id,
                        "session_id": session_id,
                        "gender": gender,
                        "age": age,
                        "part_of_speech": part_of_speech,
                        "list_id": list_id,
                        "trial_id": trial_id,
                        "stimulus": stimulus,
                        "valence": output_value(valence),
                        "arousal": output_value(arousal),
                        "dominance": output_value(dominance),
                        "unknown_word": output_value(unknown_word),
                    }
                )

                trial_rows_written += 1
                rows_by_pos[part_of_speech] += 1

                if is_missing(valence):
                    missing_valence += 1
                elif valence not in VALID_VAD_VALUES:
                    unexpected_vad_values[
                        f"Val={valence}"
                    ] += 1

                if is_missing(arousal):
                    missing_arousal += 1
                elif arousal not in VALID_VAD_VALUES:
                    unexpected_vad_values[
                        f"Aro={arousal}"
                    ] += 1

                if is_missing(dominance):
                    missing_dominance += 1
                elif dominance not in VALID_VAD_VALUES:
                    unexpected_vad_values[
                        f"Dom={dominance}"
                    ] += 1

                if is_missing(unknown_word):
                    missing_unknown_word += 1
                else:
                    unknown_word_values[unknown_word] += 1

                    if unknown_word not in VALID_UNKNOWN_VALUES:
                        unexpected_unknown_values[
                            unknown_word
                        ] += 1

                    if unknown_word == "1":
                        unknown_word_selected += 1

    # ========================================================
    # Report
    # ========================================================

    print("=== PREPROCESSING COMPLETED ===")
    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Source rows read: {source_rows}")
    print(
        "Malformed source rows: "
        f"{malformed_source_rows}"
    )
    print(
        "Participant-session-list blocks: "
        f"{len(groups)}"
    )
    print(
        "Stimulus columns in source file: "
        f"{len(stimulus_indices)}"
    )
    print(
        "Duplicate stimulus-column names: "
        f"{duplicate_stimulus_names}"
    )
    print(
        "Trial-level rows written: "
        f"{trial_rows_written}"
    )
    print(
        "Source word-columns excluded because all VAD "
        "responses were missing: "
        f"{excluded_columns_without_vad}"
    )
    print(
        "Excluded rows containing only an unknown-word "
        "checkbox value and no VAD response: "
        f"{excluded_unknown_only_rows}"
    )

    print("\nTrials by part of speech:")
    for key, value in sorted(rows_by_pos.items()):
        print(f"  {key}: {value}")

    print("\nMissing responses in retained trials:")
    print(f"  Missing valence responses: {missing_valence}")
    print(f"  Missing arousal responses: {missing_arousal}")
    print(f"  Missing dominance responses: {missing_dominance}")
    print(
        "  Missing unknown-word responses: "
        f"{missing_unknown_word}"
    )

    print("\nUnknown-word checkbox values in retained trials:")
    for key, value in sorted(
        unknown_word_values.items()
    ):
        print(f"  {key}: {value}")

    print(
        "\nRetained trials with unknown-word checkbox "
        f"selected: {unknown_word_selected}"
    )

    if unexpected_vad_values:
        print("\nWARNING: unexpected VAD values:")

        for key, value in sorted(
            unexpected_vad_values.items()
        ):
            print(f"  {key}: {value}")
    else:
        print(
            "\nValidation passed: all observed VAD values "
            "are integers from 1 to 9."
        )

    if unexpected_unknown_values:
        print("\nWARNING: unexpected unknown-word values:")

        for key, value in sorted(
            unexpected_unknown_values.items()
        ):
            print(f"  {key}: {value}")
    else:
        print(
            "Validation passed: all observed unknown-word "
            "values are coded as 0 or 1."
        )

    expected_trial_rows = 224_265

    if trial_rows_written == expected_trial_rows:
        print(
            "\nValidation passed: the number of retained "
            f"trial-level rows matches the expected value "
            f"({expected_trial_rows})."
        )
    else:
        print(
            "\nWARNING: the number of retained trial-level "
            "rows differs from the expected value. "
            f"Expected {expected_trial_rows}, "
            f"obtained {trial_rows_written}."
        )


if __name__ == "__main__":
    main()