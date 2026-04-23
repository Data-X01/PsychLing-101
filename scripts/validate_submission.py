#!/usr/bin/env python3
"""
PsychLing-101 – Automated PR Validation Suite
=============================================

Validates dataset folder contributions against the project standards defined
in README.md, CODEBOOK.csv, and CONTRIBUTING.md.

Usage:
    python scripts/validate_submission.py <folder> [<folder2> ...]
    python scripts/validate_submission.py --changed   # auto-detect from git diff
    python scripts/validate_submission.py --all       # validate every dataset folder

Exit codes:
    0  – all checks passed (warnings may still be present)
    1  – one or more ERROR-level checks failed
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional dependency: langdetect (for prompt-language checks)
# ---------------------------------------------------------------------------
try:
    from langdetect import detect as _langdetect_detect
    from langdetect import DetectorFactory

    DetectorFactory.seed = 42  # reproducible language detection

    def detect_language(text: str) -> str | None:
        """Return an ISO 639-1 language code, or None on failure."""
        try:
            return _langdetect_detect(text)
        except Exception:
            return None

    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

    def detect_language(text: str) -> str | None:  # noqa: ARG001
        return None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent

# Folders that are NOT dataset contributions
IGNORED_FOLDERS = {".git", ".github", "scripts", "__pycache__", ".idea", "node_modules"}

# Required files/dirs inside every dataset folder
REQUIRED_FILES = ["CODEBOOK.csv", "README.md", "prompts.jsonl.zip"]
REQUIRED_DIRS = ["original_data", "processed_data"]
PREPROCESS_SCRIPT_NAMES = ["preprocess_data.py", "preprocess_data.R"]
GENERATE_SCRIPT_NAMES = ["generate_prompts.py", "generate_prompts.R"]

# Main CODEBOOK canonical header
MAIN_CODEBOOK_HEADER = ("Recommended Column Name", "Description")

# Required JSONL fields (per README §3.3)
REQUIRED_JSONL_FIELDS = {"text", "experiment", "participant"}

# Optional JSONL metadata fields that should mirror CSV columns
OPTIONAL_METADATA_FIELDS = {
    "rt",
    "age",
    "diagnosis",
    "clinical_diagnoses",
    "nationality",
    "gender",
    "education",
    "first_language",
}

# Rough character limit for ~32K tokens
TOKEN_CHAR_LIMIT = 128_000


# ---------------------------------------------------------------------------
# Result collection
# ---------------------------------------------------------------------------
class Result:
    """A single validation finding."""

    def __init__(self, level: str, module: str, message: str):
        assert level in ("ERROR", "WARNING"), f"Invalid level: {level}"
        self.level = level
        self.module = module
        self.message = message

    def __str__(self):
        return f"{self.level} ({self.module}) {self.message}"

    def github_annotation(self) -> str:
        """Return a GitHub Actions annotation string."""
        tag = "error" if self.level == "ERROR" else "warning"
        return f"::{tag}::{self.module}: {self.message}"


class ResultCollector:
    """Accumulates validation results for a dataset."""

    def __init__(self, folder_name: str):
        self.folder_name = folder_name
        self.results: list[Result] = []

    def error(self, module: str, msg: str):
        self.results.append(Result("ERROR", module, msg))

    def warning(self, module: str, msg: str):
        self.results.append(Result("WARNING", module, msg))

    @property
    def has_errors(self) -> bool:
        return any(r.level == "ERROR" for r in self.results)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.level == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.results if r.level == "WARNING")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_csv_auto(path: Path) -> tuple[list[str], list[list[str]], str]:
    """Read a CSV file, auto-detecting delimiter. Returns (header, rows, delimiter)."""
    with open(path, encoding="utf-8-sig") as f:
        sample = f.read(4096)

    # Sniff delimiter
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ","

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader, None)
        rows = list(reader)

    return header or [], rows, delimiter


def load_main_codebook() -> set[str]:
    """Load column names from the repository-level CODEBOOK.csv."""
    path = REPO_ROOT / "CODEBOOK.csv"
    if not path.exists():
        return set()
    header, rows, _ = read_csv_auto(path)
    # First column contains the recommended column names
    return {row[0].strip() for row in rows if row and row[0].strip()}


# ---------------------------------------------------------------------------
# Module 1: Codebook Validation
# ---------------------------------------------------------------------------
MODULE_CODEBOOK = "codebook"


def validate_codebook(folder: Path, rc: ResultCollector, main_columns: set[str]):
    """Validate the dataset's local CODEBOOK.csv."""
    path = folder / "CODEBOOK.csv"
    if not path.exists():
        rc.error(MODULE_CODEBOOK, "CODEBOOK.csv is missing.")
        return set()

    try:
        header, rows, delimiter = read_csv_auto(path)
    except Exception as e:
        rc.error(MODULE_CODEBOOK, f"Could not parse CODEBOOK.csv: {e}")
        return set()

    if not header:
        rc.error(MODULE_CODEBOOK, "CODEBOOK.csv is empty (no header row).")
        return set()

    # Check delimiter matches main (comma)
    if delimiter != ",":
        rc.warning(
            MODULE_CODEBOOK,
            f"CODEBOOK.csv uses '{delimiter}' delimiter — the main CODEBOOK uses ','.",
        )

    # Check header names match canonical format
    header_tuple = tuple(h.strip() for h in header[:2])
    if header_tuple != MAIN_CODEBOOK_HEADER:
        rc.warning(
            MODULE_CODEBOOK,
            f"CODEBOOK.csv header is {header_tuple!r} — expected {MAIN_CODEBOOK_HEADER!r}.",
        )

    # Collect local column names
    local_columns = {row[0].strip() for row in rows if row and row[0].strip()}

    # Check that local columns appear in the main CODEBOOK
    if main_columns:
        novel = local_columns - main_columns
        if novel:
            rc.warning(
                MODULE_CODEBOOK,
                f"Columns not in main CODEBOOK.csv (may need to be added): {sorted(novel)}",
            )

    return local_columns


# ---------------------------------------------------------------------------
# Module 2: Processed Data Folder
# ---------------------------------------------------------------------------
MODULE_PROCESSED = "processed_data"


def validate_processed_folder(folder: Path, rc: ResultCollector) -> list[Path]:
    """Check processed_data/ structure and file naming."""
    proc_dir = folder / "processed_data"
    if not proc_dir.exists():
        rc.error(MODULE_PROCESSED, "processed_data/ directory is missing.")
        return []

    csvs = sorted(proc_dir.glob("*.csv"))
    if not csvs:
        rc.error(MODULE_PROCESSED, "No CSV files found in processed_data/.")
        return []

    # Check naming convention: exp1.csv, exp2.csv, ...
    expected_pattern = re.compile(r"^exp(\d+)\.csv$")
    found_indices = []
    for csv_path in csvs:
        m = expected_pattern.match(csv_path.name)
        if not m:
            rc.error(
                MODULE_PROCESSED,
                f"File '{csv_path.name}' does not match naming convention 'expN.csv'.",
            )
        else:
            found_indices.append(int(m.group(1)))

    # Check sequential 1-indexed
    if found_indices:
        expected = list(range(1, len(found_indices) + 1))
        if sorted(found_indices) != expected:
            rc.warning(
                MODULE_PROCESSED,
                f"exp*.csv indices are not sequential 1..N. Found: {sorted(found_indices)}.",
            )

    # Check for non-CSV files
    all_files = [f for f in proc_dir.iterdir() if f.is_file()]
    non_csv = [f.name for f in all_files if f.suffix.lower() != ".csv"]
    if non_csv:
        rc.warning(
            MODULE_PROCESSED,
            f"Non-CSV files in processed_data/: {non_csv}",
        )

    return csvs


# ---------------------------------------------------------------------------
# Module 3: Data Integrity
# ---------------------------------------------------------------------------
MODULE_DATA = "data_integrity"

# Number of rows to sample for original-vs-processed checks
SANITY_CHECK_N = 5
SANITY_CHECK_SEED = 42
MISSING_THRESHOLD = 0.05  # 5%


def validate_data_integrity(
    folder: Path,
    csvs: list[Path],
    local_columns: set[str],
    rc: ResultCollector,
) -> dict[str, list[str]]:
    """Validate the contents of each processed CSV.

    Returns a dict mapping csv filename to its list of column names.
    """
    csv_column_map: dict[str, list[str]] = {}

    for csv_path in csvs:
        try:
            header, rows, _ = read_csv_auto(csv_path)
        except Exception as e:
            rc.error(MODULE_DATA, f"Could not parse {csv_path.name}: {e}")
            continue

        if not header:
            rc.error(MODULE_DATA, f"{csv_path.name} has no header row.")
            continue

        columns = [h.strip() for h in header]
        csv_column_map[csv_path.name] = columns

        # --- participant_id required ---
        if "participant_id" not in columns:
            rc.error(MODULE_DATA, f"{csv_path.name}: missing required column 'participant_id'.")

        # --- Empty rows ---
        empty_rows = [
            i + 2  # 1-indexed, +1 for header
            for i, row in enumerate(rows)
            if all(cell.strip() == "" for cell in row)
        ]
        if empty_rows:
            display = empty_rows[:10]
            suffix = f" (and {len(empty_rows) - 10} more)" if len(empty_rows) > 10 else ""
            rc.error(
                MODULE_DATA,
                f"{csv_path.name}: {len(empty_rows)} fully empty row(s) at lines {display}{suffix}.",
            )

        # --- Column names vs local CODEBOOK ---
        if local_columns:
            undocumented = set(columns) - local_columns
            if undocumented:
                rc.error(
                    MODULE_DATA,
                    f"{csv_path.name}: columns not in local CODEBOOK.csv: {sorted(undocumented)}",
                )

        # --- Missing values ---
        if rows:
            n_rows = len(rows)
            for col_idx, col_name in enumerate(columns):
                n_missing = sum(
                    1 for row in rows if col_idx >= len(row) or row[col_idx].strip() == ""
                )
                frac = n_missing / n_rows
                if frac > MISSING_THRESHOLD:
                    rc.warning(
                        MODULE_DATA,
                        f"{csv_path.name}: column '{col_name}' has {n_missing}/{n_rows} "
                        f"({frac:.1%}) missing values.",
                    )

    # --- Sanity check: original vs processed ---
    _sanity_check_original_vs_processed(folder, csvs, rc)

    return csv_column_map


def _sanity_check_original_vs_processed(
    folder: Path,
    csvs: list[Path],
    rc: ResultCollector,
):
    """Spot-check a few rows from originals against processed data.

    Only runs when original_data contains CSV files.
    """
    import random

    orig_dir = folder / "original_data"
    if not orig_dir.exists():
        return

    orig_csvs = list(orig_dir.glob("*.csv"))
    if not orig_csvs:
        rc.warning(
            MODULE_DATA,
            "original_data/ contains no CSV files — skipping original-vs-processed sanity check.",
        )
        return

    # For each processed CSV, check row count plausibility against originals
    for csv_path in csvs:
        try:
            _, proc_rows, _ = read_csv_auto(csv_path)
        except Exception:
            continue

        # Sum original row counts
        total_orig_rows = 0
        for orig_csv in orig_csvs:
            try:
                _, orig_rows, _ = read_csv_auto(orig_csv)
                total_orig_rows += len(orig_rows)
            except Exception:
                continue

        if total_orig_rows > 0 and len(proc_rows) > 0:
            ratio = len(proc_rows) / total_orig_rows
            if ratio > 2.0:
                rc.warning(
                    MODULE_DATA,
                    f"{csv_path.name} has {len(proc_rows)} rows but original_data CSVs "
                    f"have {total_orig_rows} total rows (ratio {ratio:.1f}x) — "
                    "unexpected expansion, worth verifying.",
                )
            elif ratio < 0.1:
                rc.warning(
                    MODULE_DATA,
                    f"{csv_path.name} has {len(proc_rows)} rows but original_data CSVs "
                    f"have {total_orig_rows} total rows (ratio {ratio:.2f}x) — "
                    "large reduction, worth verifying.",
                )


# ---------------------------------------------------------------------------
# Module 4: Prompt Validation
# ---------------------------------------------------------------------------
MODULE_PROMPTS = "prompts"

# Regex for <<...>> markers
ANGLE_MARKER_RE = re.compile(r"<<([^>]*)>>")
# Regex for <image> or <filename.ext> style image references
IMAGE_REF_RE = re.compile(r"<[^<>]+\.[a-zA-Z]{2,4}>|<image>")


def validate_prompts(
    folder: Path,
    csv_column_map: dict[str, list[str]],
    rc: ResultCollector,
):
    """Validate prompts.jsonl.zip contents."""
    zip_path = folder / "prompts.jsonl.zip"
    if not zip_path.exists():
        rc.error(MODULE_PROMPTS, "prompts.jsonl.zip is missing.")
        return

    try:
        zf = zipfile.ZipFile(zip_path)
    except Exception as e:
        rc.error(MODULE_PROMPTS, f"Could not open prompts.jsonl.zip: {e}")
        return

    jsonl_files = [n for n in zf.namelist() if n.endswith(".jsonl") and not n.startswith("__MACOSX")]
    if not jsonl_files:
        rc.error(MODULE_PROMPTS, "No .jsonl file found inside prompts.jsonl.zip.")
        zf.close()
        return

    # Collect all CSV columns across all processed CSVs
    all_csv_columns: set[str] = set()
    for cols in csv_column_map.values():
        all_csv_columns.update(cols)

    for jsonl_name in jsonl_files:
        try:
            with zf.open(jsonl_name) as f:
                stream = io.TextIOWrapper(f, encoding="utf-8")
                lines = stream.readlines()
        except Exception as e:
            rc.error(MODULE_PROMPTS, f"Could not read {jsonl_name}: {e}")
            continue

        if not lines:
            rc.error(MODULE_PROMPTS, f"{jsonl_name} is empty.")
            continue

        all_keys_seen: set[str] = set()
        instruction_texts: list[str] = []
        stimulus_words: list[str] = []
        n_lines = len([l for l in lines if l.strip()])

        # Counters for aggregating repeating per-line issues
        missing_field_counts: dict[str, int] = {}  # field_name -> count
        participant_id_misname_count = 0
        no_marker_count = 0
        stray_angle_count = 0
        stray_angle_lines: list[int] = []
        token_limit_count = 0
        token_limit_lines: list[int] = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # --- Valid JSON ---
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                rc.error(MODULE_PROMPTS, f"{jsonl_name} line {i}: invalid JSON — {e}")
                continue

            if not isinstance(obj, dict):
                rc.error(MODULE_PROMPTS, f"{jsonl_name} line {i}: expected a JSON object, got {type(obj).__name__}.")
                continue

            keys = set(obj.keys())
            all_keys_seen.update(keys)

            # --- Required fields ---
            for field in REQUIRED_JSONL_FIELDS:
                if field not in keys:
                    if field == "participant" and "participant_id" in keys:
                        participant_id_misname_count += 1
                    else:
                        missing_field_counts[field] = missing_field_counts.get(field, 0) + 1

            text = obj.get("text", "")

            # --- <<...>> markers ---
            markers = ANGLE_MARKER_RE.findall(text)
            if not markers:
                no_marker_count += 1

            # --- Stray < > ---
            # Remove <<...>> markers and <image>/<filename.ext> refs, then count strays
            cleaned = ANGLE_MARKER_RE.sub("", text)
            cleaned = IMAGE_REF_RE.sub("", cleaned)
            stray_left = cleaned.count("<")
            stray_right = cleaned.count(">")
            if stray_left > 0 or stray_right > 0:
                stray_angle_count += 1
                if len(stray_angle_lines) < 5:
                    stray_angle_lines.append(i)

            # --- Token length ---
            if len(text) > TOKEN_CHAR_LIMIT:
                token_limit_count += 1
                if len(token_limit_lines) < 5:
                    token_limit_lines.append(i)

            # Collect instruction text (first 500 chars) for language check
            if i <= 3:  # sample first 3 participants
                instruction_texts.append(text[:500])

            # Collect stimulus/response words for language comparison
            if i <= 3 and markers:
                stimulus_words.extend(markers[:10])

        # --- Emit aggregated per-line errors/warnings ---
        if participant_id_misname_count > 0:
            rc.error(
                MODULE_PROMPTS,
                f"{jsonl_name}: field 'participant_id' used instead of 'participant' "
                f"in {participant_id_misname_count}/{n_lines} lines.",
            )

        for field, count in sorted(missing_field_counts.items()):
            rc.error(
                MODULE_PROMPTS,
                f"{jsonl_name}: required field '{field}' missing "
                f"in {count}/{n_lines} lines.",
            )

        if no_marker_count > 0:
            rc.warning(
                MODULE_PROMPTS,
                f"{jsonl_name}: {no_marker_count}/{n_lines} lines have no <<...>> markers.",
            )

        if stray_angle_count > 0:
            example = f" (e.g., lines {stray_angle_lines})" if stray_angle_lines else ""
            rc.warning(
                MODULE_PROMPTS,
                f"{jsonl_name}: {stray_angle_count}/{n_lines} lines have stray '<' or '>' "
                f"characters outside <<...>> markers{example}.",
            )

        if token_limit_count > 0:
            example = f" (e.g., lines {token_limit_lines})" if token_limit_lines else ""
            rc.warning(
                MODULE_PROMPTS,
                f"{jsonl_name}: {token_limit_count}/{n_lines} lines exceed ~32K token limit "
                f"({TOKEN_CHAR_LIMIT:,} chars){example}.",
            )

        # --- Metadata cross-check ---
        metadata_in_csv = all_csv_columns & OPTIONAL_METADATA_FIELDS
        metadata_in_jsonl = all_keys_seen & OPTIONAL_METADATA_FIELDS
        missing_meta = metadata_in_csv - metadata_in_jsonl
        if missing_meta:
            rc.warning(
                MODULE_PROMPTS,
                f"{jsonl_name}: CSV columns {sorted(missing_meta)} could be included "
                "as metadata fields in the JSONL but are missing.",
            )

        # --- Language consistency check ---
        if HAS_LANGDETECT and instruction_texts:
            _check_language_consistency(
                instruction_texts, stimulus_words, jsonl_name, rc
            )

    zf.close()


def _check_language_consistency(
    instruction_texts: list[str],
    stimulus_words: list[str],
    jsonl_name: str,
    rc: ResultCollector,
):
    """Flag if instruction language doesn't match stimulus language."""
    # Detect instruction language from the first few participants
    instr_langs = []
    for text in instruction_texts:
        lang = detect_language(text)
        if lang:
            instr_langs.append(lang)

    # Detect stimulus language from collected words
    if stimulus_words:
        stimulus_text = " ".join(stimulus_words)
        stim_lang = detect_language(stimulus_text)
    else:
        stim_lang = None

    if not instr_langs or not stim_lang:
        return

    # Most common instruction language
    from collections import Counter

    instr_lang = Counter(instr_langs).most_common(1)[0][0]

    if stim_lang != "en" and instr_lang == "en":
        rc.warning(
            MODULE_PROMPTS,
            f"{jsonl_name}: stimuli appear to be in '{stim_lang}' but instructions "
            f"appear to be in 'en'. If target words are non-English, instructions "
            "should also be in that language.",
        )
    elif stim_lang != instr_lang and stim_lang != "en":
        rc.warning(
            MODULE_PROMPTS,
            f"{jsonl_name}: language mismatch — instructions detected as '{instr_lang}', "
            f"stimuli detected as '{stim_lang}'.",
        )


# ---------------------------------------------------------------------------
# File presence checks (README §4 checklist)
# ---------------------------------------------------------------------------
MODULE_FILES = "file_presence"


def validate_file_presence(folder: Path, rc: ResultCollector):
    """Check that all required files and directories are present."""
    for fname in REQUIRED_FILES:
        # Case-insensitive check for README.md
        if fname.lower() == "readme.md":
            matches = [f for f in folder.iterdir() if f.name.lower() == "readme.md"]
            if not matches:
                rc.error(MODULE_FILES, f"Missing required file: {fname}")
        elif not (folder / fname).exists():
            rc.error(MODULE_FILES, f"Missing required file: {fname}")

    for dname in REQUIRED_DIRS:
        if not (folder / dname).exists():
            rc.error(MODULE_FILES, f"Missing required directory: {dname}/")

    # Preprocess script
    has_preprocess = any((folder / name).exists() for name in PREPROCESS_SCRIPT_NAMES)
    if not has_preprocess:
        # Check for common misnaming
        misspelled = folder / "preprocessed_data.py"
        if misspelled.exists():
            rc.error(
                MODULE_FILES,
                "Found 'preprocessed_data.py' — should be named 'preprocess_data.py'.",
            )
        else:
            rc.error(MODULE_FILES, "Missing preprocess script (preprocess_data.py or preprocess_data.R).")

    # Generate prompts script
    has_generate = any((folder / name).exists() for name in GENERATE_SCRIPT_NAMES)
    if not has_generate:
        rc.error(MODULE_FILES, "Missing generate_prompts script (generate_prompts.py or generate_prompts.R).")

    # Optional: images.zip if image_filename column is used (checked later in data integrity)


def check_images_zip(folder: Path, csv_column_map: dict[str, list[str]], rc: ResultCollector):
    """If any CSV has an 'image_filename' column, images.zip should exist."""
    has_image_col = any("image_filename" in cols for cols in csv_column_map.values())
    if has_image_col and not (folder / "images.zip").exists() and not (folder / "Images.zip").exists():
        rc.warning(
            MODULE_FILES,
            "CSV contains 'image_filename' column but no images.zip was found.",
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def validate_folder(folder: Path, main_columns: set[str]) -> ResultCollector:
    """Run all validation modules on a single dataset folder."""
    rc = ResultCollector(folder.name)

    print(f"\n{'=' * 60}")
    print(f"  Validating: {folder.name}")
    print(f"{'=' * 60}")

    # 0. File presence
    validate_file_presence(folder, rc)

    # 1. Codebook
    local_columns = validate_codebook(folder, rc, main_columns)

    # 2. Processed data folder
    csvs = validate_processed_folder(folder, rc)

    # 3. Data integrity
    csv_column_map = validate_data_integrity(folder, csvs, local_columns, rc)

    # 4. Prompts
    validate_prompts(folder, csv_column_map, rc)

    # 4b. images.zip cross-check
    check_images_zip(folder, csv_column_map, rc)

    return rc


# ---------------------------------------------------------------------------
# CLI & Reporting
# ---------------------------------------------------------------------------
def detect_changed_folders() -> list[str]:
    """Use git diff to find dataset folders changed in the current PR."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(f"WARNING: git diff failed: {result.stderr.strip()}")
            return []

        changed_files = result.stdout.strip().split("\n")
        folders = set()
        for f in changed_files:
            parts = f.split("/")
            if parts and parts[0] not in IGNORED_FOLDERS and (REPO_ROOT / parts[0]).is_dir():
                folders.add(parts[0])
        return sorted(folders)
    except FileNotFoundError:
        print("WARNING: git not found — cannot detect changed folders.")
        return []


def detect_all_folders() -> list[str]:
    """Find all dataset folders in the repo root."""
    folders = []
    for item in sorted(REPO_ROOT.iterdir()):
        if item.is_dir() and item.name not in IGNORED_FOLDERS and not item.name.startswith("."):
            # Must contain at least one expected file to be considered a dataset folder
            if (item / "CODEBOOK.csv").exists() or (item / "processed_data").exists():
                folders.append(item.name)
    return folders


def print_report(collectors: list[ResultCollector]) -> bool:
    """Print a summary report. Returns True if any errors were found."""
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true"

    print(f"\n{'=' * 60}")
    print("  VALIDATION SUMMARY")
    print(f"{'=' * 60}")

    any_errors = False
    for rc in collectors:
        status = "FAIL" if rc.has_errors else "PASS"
        marker = "❌" if rc.has_errors else "✅"
        print(f"\n{marker} {rc.folder_name}: {status}  "
              f"({rc.error_count} errors, {rc.warning_count} warnings)")

        for r in rc.results:
            prefix = "  ❌" if r.level == "ERROR" else "  ⚠️ "
            print(f"{prefix} {r}")

        if rc.has_errors:
            any_errors = True

    print(f"\n{'=' * 60}")
    if any_errors:
        print("  RESULT: FAILED — errors must be fixed before merge.")
    else:
        print("  RESULT: PASSED" + (" (with warnings)" if any(rc.warning_count > 0 for rc in collectors) else ""))
    print(f"{'=' * 60}\n")

    # Write GitHub Actions Job Summary (rendered as markdown on the PR page)
    if is_ci:
        _write_job_summary(collectors, any_errors)

    return any_errors


def _build_summary_markdown(
    collectors: list[ResultCollector], any_errors: bool
) -> str:
    """Build a rich markdown summary string."""
    lines: list[str] = []

    # Header
    if any_errors:
        lines.append("# ❌ Validation Failed\n")
    else:
        has_warnings = any(rc.warning_count > 0 for rc in collectors)
        if has_warnings:
            lines.append("# ✅ Validation Passed (with warnings)\n")
        else:
            lines.append("# ✅ Validation Passed\n")

    # Overview table
    lines.append("| Dataset | Status | Errors | Warnings |")
    lines.append("|---------|--------|--------|----------|")
    for rc in collectors:
        marker = "❌ FAIL" if rc.has_errors else "✅ PASS"
        lines.append(f"| `{rc.folder_name}` | {marker} | {rc.error_count} | {rc.warning_count} |")
    lines.append("")

    # Details per dataset
    for rc in collectors:
        if not rc.results:
            continue

        lines.append(f"## `{rc.folder_name}`\n")

        # Errors first
        errors = [r for r in rc.results if r.level == "ERROR"]
        if errors:
            lines.append("<details open>")
            lines.append(f"<summary>❌ <strong>{len(errors)} Error(s)</strong> — must fix before merge</summary>\n")
            for r in errors:
                lines.append(f"- **[{r.module}]** {r.message}")
            lines.append("\n</details>\n")

        # Then warnings
        warnings = [r for r in rc.results if r.level == "WARNING"]
        if warnings:
            lines.append("<details>")
            lines.append(f"<summary>⚠️ {len(warnings)} Warning(s) — informational</summary>\n")
            for r in warnings:
                lines.append(f"- **[{r.module}]** {r.message}")
            lines.append("\n</details>\n")

    return "\n".join(lines)


def _write_job_summary(collectors: list[ResultCollector], any_errors: bool):
    """Write markdown summary to $GITHUB_STEP_SUMMARY and validation_summary.md."""
    md = _build_summary_markdown(collectors, any_errors)

    # Write to $GITHUB_STEP_SUMMARY (rendered on the Actions Summary tab)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a") as f:
                f.write(md + "\n")
        except Exception:
            pass

    # Write to file for PR comment posting
    try:
        with open(REPO_ROOT / "validation_summary.md", "w") as f:
            f.write(md + "\n")
    except Exception:
        pass


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Determine which folders to validate
    if sys.argv[1] == "--changed":
        folder_names = detect_changed_folders()
        if not folder_names:
            print("No dataset folders changed in this PR. Nothing to validate.")
            sys.exit(0)
    elif sys.argv[1] == "--all":
        folder_names = detect_all_folders()
        if not folder_names:
            print("No dataset folders found in the repository.")
            sys.exit(0)
    else:
        folder_names = sys.argv[1:]

    print(f"Folders to validate: {folder_names}")

    if not HAS_LANGDETECT:
        print("NOTE: 'langdetect' not installed — language consistency checks will be skipped.")
        print("      Install with: pip install langdetect")

    # Load the main CODEBOOK for cross-referencing
    main_columns = load_main_codebook()
    if not main_columns:
        print("WARNING: Could not load main CODEBOOK.csv — column cross-checks will be limited.")

    # Run validation
    collectors = []
    for name in folder_names:
        folder = REPO_ROOT / name
        if not folder.is_dir():
            print(f"\nWARNING: '{name}' is not a directory — skipping.")
            continue
        rc = validate_folder(folder, main_columns)
        collectors.append(rc)

    if not collectors:
        print("No valid dataset folders to validate.")
        sys.exit(0)

    # Report
    has_errors = print_report(collectors)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()