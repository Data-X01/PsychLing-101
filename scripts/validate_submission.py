import csv
import io
import json
import sys
import zipfile
from pathlib import Path

REQUIRED_FILES = ["CODEBOOK.csv"]
REQUIRED_DIRS = ["original_data", "processed_data"]


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def validate_csv(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                fail(f"{path} is empty")
    except Exception as e:
        fail(f"Could not read CSV {path}: {e}")


def validate_prompts_zip(path):
    try:
        with zipfile.ZipFile(path) as z:
            jsonl_files = [x for x in z.namelist() if x.endswith(".jsonl")]
            if not jsonl_files:
                fail("No JSONL file inside prompts.zip")

            with z.open(jsonl_files[0]) as f:
                stream = io.TextIOWrapper(f, encoding="utf8")

                for i, line in enumerate(stream, 1):
                    obj = json.loads(line)

                    if "text" not in obj:
                        fail(f"Line {i} missing 'text'")
                    if "experiment" not in obj:
                        fail(f"Line {i} missing 'experiment'")
                    if "participant" not in obj:
                        fail(f"Line {i} missing 'participant'")

    except Exception as e:
        fail(f"Problem reading prompts.zip: {e}")


def validate_folder(folder):

    print(f"\nChecking folder: {folder}\n")

    folder = Path(folder)

    if not folder.exists():
        fail("Folder does not exist")

    for f in REQUIRED_FILES:
        if not (folder / f).exists():
            fail(f"Missing file: {f}")

    for d in REQUIRED_DIRS:
        if not (folder / d).exists():
            fail(f"Missing directory: {d}")

    validate_csv(folder / "CODEBOOK.csv")

    csvs = list((folder / "processed_data").glob("*.csv"))

    if not csvs:
        fail("No CSVs in processed_data")

    for c in csvs:
        validate_csv(c)

    validate_prompts_zip(folder / "prompts.jsonl.zip")

    print("All checks passed.")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/validate_submission.py dataset_folder")
        sys.exit(1)

    validate_folder(sys.argv[1])