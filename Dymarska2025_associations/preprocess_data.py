"""
preprocess_data.py
------------------
Reads every CSV inside original_data/, renames columns to match the project
CODEBOOK, and writes two cleaned files to processed_data/:

  exp1.csv       — wide format: one row per (participant × cue),
                   response1 … response20 as separate columns.
  exp1_long.csv  — long format: one row per (participant × cue × response),
                   with first_key_RT, response_corrected, responseWordFreq,
                   and not_in_subtlex_uk.
"""

from pathlib import Path
import pandas as pd


# ---------------------------------------------------------------------------
# Column rename map  (raw name → CODEBOOK canonical name)
# ---------------------------------------------------------------------------

RENAME_MAP = {
    "Ps.number":         "participant_id",
    "Cue.number":        "cue_number",       # helper for ordering; dropped later
    "Response.number":   "response_number",
    "cues":              "stimulus",
    "Response":          "response",
    "RT":                "first_key_RT",
    "Response_spelling": "response_corrected",
    "ZipfUK":            "responseWordFreq",
}

# Columns to keep in the long output (CODEBOOK-aligned)
LONG_COLS = [
    "participant_id",
    "trial_id",
    "stimulus",
    "response_number",
    "response",
    "response_corrected",
    "first_key_RT",
    "responseWordFreq",
    "not_in_subtlex_uk",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


# ---------------------------------------------------------------------------
# Core preprocessing
# ---------------------------------------------------------------------------

def preprocess(base_dir: Path) -> None:
    original_dir = base_dir / "original_data"
    processed_dir = ensure_processed_dir(base_dir)

    # --- 1. Read all CSVs in original_data/ ---
    csv_files = sorted(original_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {original_dir}")

    frames = []
    for path in csv_files:
        print(f"  Reading: {path.name}")
        try:
            df = pd.read_csv(path, index_col=0)
            if df.index.name and df.index.name not in df.columns:
                df = df.reset_index()
        except Exception:
            df = pd.read_csv(path)
        frames.append(df)

    raw = pd.concat(frames, ignore_index=True)
    print(f"  Raw shape: {raw.shape}")

    # --- 2. Rename columns ---
    raw = raw.rename(columns=RENAME_MAP)

    # --- 3. Type coercions ---
    raw["participant_id"]  = pd.to_numeric(raw["participant_id"], errors="coerce")
    raw["response_number"] = pd.to_numeric(raw["response_number"], errors="coerce")
    raw["first_key_RT"]    = pd.to_numeric(raw["first_key_RT"], errors="coerce")
    raw["responseWordFreq"] = pd.to_numeric(raw["responseWordFreq"], errors="coerce")

    # --- 4. not_in_subtlex_uk: 1 if responseWordFreq is NaN, else 0 ---
    raw["not_in_subtlex_uk"] = raw["responseWordFreq"].isna().astype(int)

    # --- 5. Lowercase text fields ---
    for col in ("stimulus", "response", "response_corrected"):
        if col in raw.columns:
            raw[col] = raw[col].astype(str).str.lower().str.strip()
            raw[col] = raw[col].replace("nan", "")

    # --- 6. Compute trial_id (0-based index of cue per participant,
    #        ordered by cue_number) ---
    cue_order = (
        raw[["participant_id", "stimulus", "cue_number"]]
        .drop_duplicates()
        .sort_values(["participant_id", "cue_number"])
    )
    cue_order["trial_id"] = cue_order.groupby("participant_id").cumcount()
    raw = raw.merge(
        cue_order[["participant_id", "stimulus", "trial_id"]],
        on=["participant_id", "stimulus"],
        how="left",
    )
    raw = raw.drop(columns=["cue_number"], errors="ignore")

    # -----------------------------------------------------------------------
    # LONG FORMAT  (exp1_long.csv)
    # -----------------------------------------------------------------------
    long_cols_present = [c for c in LONG_COLS if c in raw.columns]
    df_long = (
        raw[long_cols_present]
        .sort_values(["participant_id", "trial_id", "response_number"])
        .reset_index(drop=True)
    )
    long_path = processed_dir / "exp1_long.csv"
    df_long.to_csv(long_path, index=False)
    print(f"  Written: {long_path.name}  ({df_long.shape[0]} rows × {df_long.shape[1]} cols)")

    # -----------------------------------------------------------------------
    # WIDE FORMAT  (exp1.csv) — one row per participant × cue,
    #              response1 … response20 as separate columns
    # -----------------------------------------------------------------------
    wide = (
        raw
        .pivot_table(
            index=["participant_id", "trial_id", "stimulus"],
            columns="response_number",
            values="response",
            aggfunc="first",
        )
        .rename(columns=lambda n: f"response{int(n)}")
        .reset_index()
    )
    wide.columns.name = None

    for i in range(1, 21):
        col = f"response{i}"
        if col not in wide.columns:
            wide[col] = ""
        wide[col] = wide[col].fillna("").astype(str)

    final_cols = (
        ["participant_id", "trial_id", "stimulus"]
        + [f"response{i}" for i in range(1, 21)]
    )
    df_wide = (
        wide[final_cols]
        .sort_values(["participant_id", "trial_id"])
        .reset_index(drop=True)
    )
    wide_path = processed_dir / "exp1.csv"
    df_wide.to_csv(wide_path, index=False)
    print(f"  Written: {wide_path.name}  ({df_wide.shape[0]} rows × {df_wide.shape[1]} cols)")

    # --- Summary ---
    print("\n  === Summary ===")
    print(f"  Participants      : {df_wide['participant_id'].nunique()}")
    print(f"  Unique cues       : {df_wide['stimulus'].nunique()}")
    print(f"  Total responses   : {len(df_long)}")
    print(f"  Not in SUBTLEX-UK : {raw['not_in_subtlex_uk'].sum()} responses")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    base = Path(__file__).parent.resolve()
    print(f"\nPreprocessing data in: {base}\n")
    preprocess(base)
    print("\nDone.\n")
