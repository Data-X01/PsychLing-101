from pathlib import Path
from typing import Optional, Dict, List, Any
import pandas as pd
import argparse
import re
import sys

# --- Helper Functions ---

def find_case_insensitive(df: pd.DataFrame, name: str) -> Optional[str]:
    """
    Finds the exact column name in the DataFrame that matches the given name
    case-insensitively.

    Args:
        df: The pandas DataFrame.
        name: The target column name (case-insensitive search).

    Returns:
        The exact column name (string) from the DataFrame, or None if not found.
    """
    name_l = name.lower()
    for c in df.columns:
        if c.lower() == name_l:
            return c
    return None

def extract_suffix_int(s: Any) -> Optional[int]:
    """
    Extracts an integer suffix from a string (e.g., 'ppt_101' -> 101).

    Args:
        s: The input value, typically a participant ID string.

    Returns:
        The integer suffix, or None if no suffix is found.
    """
    # Convert to string safely before searching
    m = re.search(r'(\d+)$', str(s))
    return int(m.group(1)) if m else None

def build_numeric_mapping(orig_ids: List[Any]) -> Dict[Any, int]:
    """
    Creates a mapping from original participant IDs to sequential zero-based integers.

    It preserves the order of first appearance but prioritizes sorting by
    the numeric suffix (e.g., ppt_1, ppt_2, ppt_10) when available.

    Args:
        orig_ids: A list of original participant IDs.

    Returns:
        A dictionary mapping original IDs to new integer IDs.
    """
    # 1. Collect unique IDs in order of appearance
    seen = []
    for v in orig_ids:
        if v not in seen:
            seen.append(v)

    # 2. Separate IDs based on the presence of a numeric suffix
    with_suffix = []
    without_suffix = []
    for v in seen:
        s = extract_suffix_int(v)
        if s is not None:
            with_suffix.append((v, s))
        else:
            without_suffix.append(v)

    # 3. Sort IDs with suffixes numerically
    with_suffix_sorted = [v for v, _ in sorted(with_suffix, key=lambda x: x[1])]

    # 4. Combine sorted and unsorted lists
    final_order = with_suffix_sorted + without_suffix

    # 5. Create the final mapping
    return {orig: idx for idx, orig in enumerate(final_order)}

# --- Main Processing Function ---

def main(input_csv: Path) -> None:
    """
    Performs minimal preprocessing on a raw CSV file to standardize column names,
    generate numeric participant IDs, add a trial index, and save the result
    to the 'processed_data' directory.

    Args:
        input_csv: Path to the input CSV file (e.g., 'trial_level_data.csv').
    """
    if not input_csv.exists():
        print("ERROR: input file not found:", input_csv, file=sys.stderr)
        sys.exit(1)

    # Load data
    df = pd.read_csv(input_csv, low_memory=False)

    ## 1. Column Drops and Renaming

    # Drop Unnamed* columns
    unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols, errors='ignore')

    # Rename ppn, participant-like columns -> participant_id
    if find_case_insensitive(df, "ppn"):
        original_pid_col = find_case_insensitive(df, "ppn")
        df = df.rename(columns={original_pid_col: "participant_id"})
    else:
        # If 'ppn' isn't found, try other common participant column names
        PARTICIPANT_CANDIDATES = ("participant_id", "participant", "ppt", "subj", "subject")
        for cand in PARTICIPANT_CANDIDATES:
            c = find_case_insensitive(df, cand)
            if c:
                df = df.rename(columns={c: "participant_id"})
                break
        else:
            # Fallback: create synthetic participant_id from row index strings
            df["participant_id"] = df.index.astype(str)

    # Rename recognition_RT -> rt
    recog_col = find_case_insensitive(df, "recognition_RT")
    if recog_col:
        df = df.rename(columns={recog_col: "rt"})

    # Rename image -> image_filename
    image_col = find_case_insensitive(df, "image")
    if image_col:
        df = df.rename(columns={image_col: "image_filename"})

    ## 2. Participant ID Normalization and Trial Indexing

    # Map original IDs (e.g., 'ppt_1', 'ppt_2') to numeric IDs (0, 1, 2...)
    orig_ids = list(df["participant_id"].astype(str).unique())
    mapping = build_numeric_mapping(orig_ids)
    df["participant_id"] = df["participant_id"].astype(str).map(mapping).astype(int)

    # Add trial_id: zero-based index for each participant
    df["trial_id"] = df.groupby("participant_id").cumcount().astype(int)

    ## 3. Final Reordering and Output

    # Reorder columns to put key IDs and RT at the front
    cols = list(df.columns)
    front_cols = ["participant_id", "trial_id"]
    if "rt" in cols:
        front_cols.append("rt")

    # Exclude front columns from the rest
    rest_cols = [c for c in cols if c not in front_cols]
    df = df[front_cols + rest_cols]

    # Determine output path structure (e.g., /parent/processed_data/exp1.csv)
    out_parent = None
    # Find a parent directory named 'original_data' and use its parent
    for p in input_csv.parents:
        if p.name == "original_data":
            out_parent = p.parent
            break

    # If 'original_data' isn't in the path, use the input file's directory
    if out_parent is None:
        out_parent = input_csv.parent

    outdir = out_parent / "processed_data"
    outdir.mkdir(parents=True, exist_ok=True)

    # Write the processed file
    outpath = outdir / "exp1.csv"
    df.to_csv(outpath, index=False)
    print(f"Wrote processed CSV: {outpath} (rows: {len(df)}, participants: {len(mapping)})")

# --- Execution ---

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Create processed_data/exp1.csv with numeric participant IDs (no backup column).")
    ap.add_argument("input_csv", help="Path to trial_level_data.csv")
    args = ap.parse_args()
    main(Path(args.input_csv).expanduser().resolve())