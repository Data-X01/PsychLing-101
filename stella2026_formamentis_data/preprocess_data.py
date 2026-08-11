"""
Preprocess free-association + valence raw files for PsychLing-101.

Expected folder layout when this script is placed in your experiment folder:

    <authorYEAR_title>/
    ├── original_data/          # raw participant files, e.g. cfm_v6_*.csv
    ├── preprocess_data.py      # this script
    ├── processed_data/         # created by this script
    └── CODEBOOK.csv            # optional; script also checks the parent folder

The raw CFM-style files have two columns:
    word, resp
where trial rows contain a semicolon-separated response field:
    cue;response1;response2;response3;cue_valence;response1_valence;response2_valence;response3_valence
and participant metadata rows contain keys such as age, gender, nationality, firstlang, job, stem.

Output:
    processed_data/exp1.csv

The script also updates CODEBOOK.csv with the dataset-specific variables that are
needed here but absent from the canonical codebook.
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Iterable

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ORIGINAL_DATA_DIR = SCRIPT_DIR / "original_data"
PROCESSED_DATA_DIR = SCRIPT_DIR / "processed_data"
OUTPUT_FILE = PROCESSED_DATA_DIR / "exp1.csv"

CODEBOOK_COLUMNS = ["Recommended Column Name", "Description"]

# These fields are needed for this dataset but may not yet be present in the
# shared PsychLing-101 CODEBOOK.csv.
REQUIRED_CODEBOOK_ENTRIES = {
    "source_file": "Original raw data filename from which this observation was derived.",
    "occupation": "Participant's self-reported occupation, role, or student status.",
    "stem_background": "Raw participant STEM/background group code as recorded in the original data.",
    "response3": "Third association response (for association tasks).",
    "stimulus_valence": "Participant's normative valence rating for the cue/stimulus word.",
    "response1_valence": "Participant's normative valence rating for response1.",
    "response2_valence": "Participant's normative valence rating for response2.",
    "response3_valence": "Participant's normative valence rating for response3.",
}

METADATA_KEYS = {
    "age": "age",
    "gender": "gender",
    "nationality": "nationality",
    "firstlang": "first_language",
    "first_language": "first_language",
    "job": "occupation",
    "occupation": "occupation",
    "stem": "stem_background",
    "stem_background": "stem_background",
}

OUTPUT_COLUMNS = [
    "participant_id",
    "source_file",
    "age",
    "gender",
    "nationality",
    "first_language",
    "occupation",
    "stem_background",
    "trial_id",
    "trial_order",
    "stimulus",
    "response1",
    "response2",
    "response3",
    "stimulus_valence",
    "response1_valence",
    "response2_valence",
    "response3_valence",
]

QUOTE_CHARS = "\"'‘’“”`´"


# ---------------------------------------------------------------------------
# General cleaning helpers
# ---------------------------------------------------------------------------

def clean_text(value: object, *, lowercase: bool = False) -> str | pd.NA:
    """Strip quotes/extra whitespace while preserving internal spaces."""
    if pd.isna(value):
        return pd.NA

    text = str(value).replace("\ufeff", "").strip()
    if text.lower() in {"nan", "none", "null"}:
        return pd.NA

    # Remove quote characters anywhere in the short word/phrase field.
    text = text.translate(str.maketrans("", "", QUOTE_CHARS))
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return pd.NA
    return text.lower() if lowercase else text


def clean_word(value: object) -> str | pd.NA:
    """Clean lexical items consistently for cues and associations."""
    return clean_text(value, lowercase=True)


def clean_gender(value: object) -> str | pd.NA:
    """Normalize common gender labels without over-interpreting rare values."""
    text = clean_text(value, lowercase=True)
    if pd.isna(text):
        return pd.NA
    mapping = {
        "m": "male",
        "man": "male",
        "male": "male",
        "f": "female",
        "woman": "female",
        "female": "female",
    }
    return mapping.get(str(text), str(text))


def clean_metadata_value(column: str, value: object) -> object:
    """Clean participant-level metadata using light-touch normalisation."""
    if column == "gender":
        return clean_gender(value)
    if column in {"nationality", "first_language"}:
        return clean_text(value, lowercase=True)
    if column in {"age", "stem_background"}:
        return value
    return clean_text(value, lowercase=False)


def parse_int_like(value: object) -> object:
    """Return an integer-like value or pd.NA. Useful for age and coded metadata."""
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    number = pd.to_numeric(text, errors="coerce")
    if pd.isna(number):
        return pd.NA
    if float(number).is_integer():
        return int(number)
    return float(number)


def parse_valence(value: object) -> object:
    """Parse valence ratings as numbers, preserving missing values as pd.NA."""
    return parse_int_like(value)


def split_cfm_response(raw_response: object) -> tuple[list[object], list[object]]:
    """
    Split the CFM response field into four lexical fields and four valence fields.

    Expected format:
        cue;resp1;resp2;resp3;v_cue;v_resp1;v_resp2;v_resp3

    Missing trailing fields are padded with pd.NA. Extra fields are retained only
    through the first eight slots because semicolon is the raw delimiter.
    """
    if pd.isna(raw_response):
        parts: list[str] = []
    else:
        parts = str(raw_response).split(";")

    if len(parts) < 8:
        parts = parts + [""] * (8 - len(parts))
    elif len(parts) > 8:
        warnings.warn(
            f"Found {len(parts)} semicolon-separated fields; using the first 8: {raw_response!r}",
            RuntimeWarning,
            stacklevel=2,
        )
        parts = parts[:8]

    words = [clean_word(x) for x in parts[:4]]
    valences = [parse_valence(x) for x in parts[4:8]]
    return words, valences


def remove_repeated_responses(
    stimulus: object,
    responses: Iterable[object],
    response_valences: Iterable[object],
) -> tuple[list[object], list[object]]:
    """
    Remove repeated association words while preserving order and aligned valence.

    A response is dropped if, after cleaning, it repeats the cue/stimulus or any
    earlier retained response for the same trial. Later unique responses shift
    left; missing slots are padded with pd.NA.
    """
    seen: set[str] = set()
    if not pd.isna(stimulus):
        seen.add(str(stimulus).casefold())

    kept_responses: list[object] = []
    kept_valences: list[object] = []

    for response, valence in zip(responses, response_valences):
        if pd.isna(response):
            continue
        key = str(response).casefold()
        if key in seen:
            continue
        seen.add(key)
        kept_responses.append(response)
        kept_valences.append(valence)

    while len(kept_responses) < 3:
        kept_responses.append(pd.NA)
        kept_valences.append(pd.NA)

    return kept_responses[:3], kept_valences[:3]


# ---------------------------------------------------------------------------
# Input/output helpers
# ---------------------------------------------------------------------------

def find_codebook() -> Path:
    """
    Prefer a CODEBOOK.csv next to this script; otherwise use the parent folder.

    This supports both common layouts:
      1. CODEBOOK.csv copied into the experiment folder.
      2. CODEBOOK.csv kept at the repository root, one level above the experiment.
    """
    candidates = [
        SCRIPT_DIR / "CODEBOOK.csv",
        SCRIPT_DIR.parent / "CODEBOOK.csv",
        Path.cwd() / "CODEBOOK.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return SCRIPT_DIR / "CODEBOOK.csv"


def ensure_codebook_entries(codebook_path: Path) -> None:
    """Add required missing variables to CODEBOOK.csv using the existing format."""
    if codebook_path.exists():
        codebook = pd.read_csv(codebook_path, dtype=str)
        missing_columns = [c for c in CODEBOOK_COLUMNS if c not in codebook.columns]
        if missing_columns:
            raise ValueError(
                f"{codebook_path} must contain columns {CODEBOOK_COLUMNS}; "
                f"missing {missing_columns}"
            )
        codebook = codebook[CODEBOOK_COLUMNS].copy()
    else:
        codebook = pd.DataFrame(columns=CODEBOOK_COLUMNS)

    existing = set(codebook["Recommended Column Name"].dropna().astype(str))
    additions = [
        {
            "Recommended Column Name": name,
            "Description": description,
        }
        for name, description in REQUIRED_CODEBOOK_ENTRIES.items()
        if name not in existing
    ]

    if additions:
        codebook = pd.concat([codebook, pd.DataFrame(additions)], ignore_index=True)
        codebook.to_csv(codebook_path, index=False)
        print(f"Updated {codebook_path} with {len(additions)} new codebook entries.")
    else:
        print(f"No CODEBOOK.csv updates needed: {codebook_path}")


def read_raw_file(path: Path) -> pd.DataFrame:
    """Read a supported raw data file from original_data/."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, dtype=str, keep_default_na=False)
    raise ValueError(f"Unsupported raw file type: {path.name}")


def iter_raw_files(original_data_dir: Path) -> list[Path]:
    """Return supported files directly inside original_data/, sorted by name."""
    supported_suffixes = {".csv", ".tsv", ".xlsx", ".xls"}
    return sorted(
        path
        for path in original_data_dir.iterdir()
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in supported_suffixes
    )


# ---------------------------------------------------------------------------
# Dataset-specific transformation
# ---------------------------------------------------------------------------

def extract_metadata(raw: pd.DataFrame) -> dict[str, object]:
    """Extract participant-level metadata rows from a CFM-style raw file."""
    metadata: dict[str, object] = {}

    for _, row in raw.iterrows():
        raw_key = clean_text(row.get("word", ""), lowercase=True)
        if pd.isna(raw_key):
            continue
        canonical_key = METADATA_KEYS.get(str(raw_key))
        if canonical_key is None:
            continue
        metadata[canonical_key] = clean_metadata_value(canonical_key, row.get("resp", pd.NA))

    metadata["age"] = parse_int_like(metadata.get("age", pd.NA))
    metadata["stem_background"] = parse_int_like(metadata.get("stem_background", pd.NA))
    return metadata


def is_metadata_row(raw_word: object) -> bool:
    key = clean_text(raw_word, lowercase=True)
    return False if pd.isna(key) else str(key) in METADATA_KEYS


def preprocess_participant_file(path: Path) -> pd.DataFrame:
    """Convert one participant file into tidy trial-level rows."""
    raw = read_raw_file(path)
    required_input_columns = {"word", "resp"}
    missing = required_input_columns - set(raw.columns)
    if missing:
        raise ValueError(f"{path.name} is missing expected columns: {sorted(missing)}")

    participant_id = path.stem
    metadata = extract_metadata(raw)

    trial_rows = raw.loc[~raw["word"].map(is_metadata_row)].reset_index(drop=True)
    tidy_rows: list[dict[str, object]] = []

    for trial_order, row in trial_rows.iterrows():
        stimulus_from_word = clean_word(row["word"])
        word_fields, valence_fields = split_cfm_response(row["resp"])

        # The first word in resp is the cue repeated by the raw file. Prefer the
        # explicit `word` column, but warn when the duplicate cue disagrees.
        stimulus_from_resp = word_fields[0]
        if pd.isna(stimulus_from_word) and not pd.isna(stimulus_from_resp):
            stimulus = stimulus_from_resp
        else:
            stimulus = stimulus_from_word

        if (
            not pd.isna(stimulus_from_word)
            and not pd.isna(stimulus_from_resp)
            and str(stimulus_from_word).casefold() != str(stimulus_from_resp).casefold()
        ):
            warnings.warn(
                f"Cue mismatch in {path.name}, row {trial_order}: "
                f"word={stimulus_from_word!r}, resp cue={stimulus_from_resp!r}; using word column.",
                RuntimeWarning,
                stacklevel=2,
            )

        responses, response_valences = remove_repeated_responses(
            stimulus=stimulus,
            responses=word_fields[1:4],
            response_valences=valence_fields[1:4],
        )

        tidy_rows.append(
            {
                "participant_id": participant_id,
                "source_file": path.name,
                "age": metadata.get("age", pd.NA),
                "gender": metadata.get("gender", pd.NA),
                "nationality": metadata.get("nationality", pd.NA),
                "first_language": metadata.get("first_language", pd.NA),
                "occupation": metadata.get("occupation", pd.NA),
                "stem_background": metadata.get("stem_background", pd.NA),
                "trial_id": f"{participant_id}_trial_{trial_order:03d}",
                "trial_order": trial_order,  # 0-indexed, matching PsychLing-101 codebook wording
                "stimulus": stimulus,
                "response1": responses[0],
                "response2": responses[1],
                "response3": responses[2],
                "stimulus_valence": valence_fields[0],
                "response1_valence": response_valences[0],
                "response2_valence": response_valences[1],
                "response3_valence": response_valences[2],
            }
        )

    return pd.DataFrame(tidy_rows, columns=OUTPUT_COLUMNS)


def finalise_types(tidy: pd.DataFrame) -> pd.DataFrame:
    """Apply stable dtypes and final duplicate checks before writing CSV."""
    result = tidy.copy()

    for column in ["age", "stem_background", "trial_order"]:
        result[column] = pd.to_numeric(result[column], errors="coerce").astype("Int64")

    for column in [
        "stimulus_valence",
        "response1_valence",
        "response2_valence",
        "response3_valence",
    ]:
        result[column] = pd.to_numeric(result[column], errors="coerce").astype("Int64")

    # Defensive duplicate removal at the final-data level. The expected unit is
    # one participant × one cue/trial; repeated raw exports should not duplicate rows.
    before = len(result)
    result = result.drop_duplicates(subset=["participant_id", "trial_order", "stimulus"])
    after = len(result)
    if after < before:
        warnings.warn(f"Dropped {before - after} duplicated participant-trial rows.", RuntimeWarning)

    return result[OUTPUT_COLUMNS]


def main() -> None:
    if not ORIGINAL_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Cannot find {ORIGINAL_DATA_DIR}. Create original_data/ next to preprocess_data.py "
            "and place the raw files inside it."
        )

    codebook_path = find_codebook()
    ensure_codebook_entries(codebook_path)

    raw_files = iter_raw_files(ORIGINAL_DATA_DIR)
    if not raw_files:
        raise FileNotFoundError(f"No supported raw files found inside {ORIGINAL_DATA_DIR}")

    tidy_parts = []
    for path in raw_files:
        tidy_parts.append(preprocess_participant_file(path))

    tidy = finalise_types(pd.concat(tidy_parts, ignore_index=True))

    PROCESSED_DATA_DIR.mkdir(exist_ok=True)
    tidy.to_csv(OUTPUT_FILE, index=False)

    print(f"Read {len(raw_files)} raw file(s) from {ORIGINAL_DATA_DIR}")
    print(f"Wrote {len(tidy)} trial-level row(s) to {OUTPUT_FILE}")
    print(f"Columns: {', '.join(tidy.columns)}")


if __name__ == "__main__":
    main()
