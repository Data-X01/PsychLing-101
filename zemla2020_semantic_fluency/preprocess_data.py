"""Preprocessing for Zemla, Cao, Mueller & Austerweil (2020), Behavior Research Methods.

Semantic fluency: participants named as many members of a cued category as they
could within a fixed time limit, repeatedly, across several rounds. The published
sample pools three separate experiments that differ in their category sets, in the
number of rounds and in the time allowed per round.

Input : original_data/from_github/fluency_data/snafu_sample.csv
Output: processed_data/exp1.csv (one row per named item; nothing is dropped)

Nothing is filtered out. Responses that cannot be trusted are marked with flags
so that downstream analyses can exclude them explicitly.

Run from the contribution folder:  python3 preprocess_data.py
"""

from pathlib import Path
import csv

import pandas as pd

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent

# Two byte-comparable copies of the sample ship with the paper. They are
# row-for-row identical, but the OSF copy (original_data/from_osf/snafu_sample.csv)
# has no `itemnum` column and spells the latency column `RT` instead of `rt`.
# `itemnum` is the position of a response within its list, i.e. the presentation
# order this project's `trial_order` requires, so the GitHub copy is used.
INPUT_FILE = BASE / "original_data" / "from_github" / "fluency_data" / "snafu_sample.csv"

# Category scheme and spelling variants shipped with the paper. Used only to
# decide whether the contents of a list match the category label it carries.
ANIMAL_SCHEME_FILE = BASE / "original_data" / "from_osf" / "animals_snafu_scheme.csv"
ANIMAL_SPELLING_FILE = BASE / "original_data" / "from_osf" / "animals_snafu_spellfile.csv"

PROCESSED_DIR = BASE / "processed_data"
OUTPUT_FILE = PROCESSED_DIR / "exp1.csv"

# --------------------------------------------------------------------------
# Expected structure, taken from the paper and from the published task code
# --------------------------------------------------------------------------
EXPECTED_N_ROWS = 24572
EXPECTED_N_PARTICIPANTS = 82
EXPECTED_N_LISTS = 807
EXPECTED_N_CATEGORIES = 6

# Participant identifiers are prefixed by experiment: A -> Experiment1, and so on.
EXPECTED_PREFIX_TO_GROUP = {
    "A": ("Experiment1", 20),
    "B": ("Experiment2", 12),
    "C": ("Experiment3", 50),
}

# Round time limit, in milliseconds.
#
# For Experiment1 and Experiment3 this is documented: both published versions of
# the task (original_data/from_github/fluency_task/{web,lab}_version/app.js) set
# `timeperlist = 180`, i.e. 180 s, and the on-screen instructions say "three
# minutes". Those two experiments also match the task code in every other
# respect (three categories, three rounds each, replay of any round with five or
# fewer responses), so the documented value is used directly.
#
# No task code was published for Experiment2, which used two categories and
# either 12 or 18 rounds. Its limit is therefore RECONSTRUCTED from the data --
# see derive_round_time_limits().
DOCUMENTED_TIME_LIMIT_MS = 180_000
DOCUMENTED_LIMIT_GROUPS = ("Experiment1", "Experiment3")
RECONSTRUCTED_LIMIT_GROUPS = ("Experiment2",)

# Candidate limits considered when reconstructing. Whole-minute values only:
# an experimenter-chosen limit is expected to be a round number.
CANDIDATE_TIME_LIMITS_MS = (60_000, 120_000, 180_000, 240_000, 300_000)

# A reconstructed limit is only believable if participants actually ran into it.
# Every reconstructed participant must reach at least this share of the limit.
CEILING_TIGHTNESS = 0.95

# The countdown ran on a browser setInterval, which drifts and is throttled in
# background tabs, so the last response of a round can be timestamped slightly
# after the limit. The largest observed overshoot is 12758 ms.
TIMER_DRIFT_TOLERANCE_MS = 15_000

# `RTstart` is an integer running total of `rt`, so exact agreement is expected.
RT_RECONCILIATION_TOLERANCE_MS = 0

# Share of a list's responses that must be recognised animal names before the
# list is judged to hold animals regardless of the label it carries. The
# observed gap is wide: the single mismatching list scores 0.96, the highest
# scoring non-animal list scores 0.67, and every list labelled `animals` scores
# at least 0.86.
ANIMAL_SHARE_HIGH = 0.80
ANIMAL_SHARE_LOW = 0.50

REPORT_WIDTH = 78


class PreprocessingError(RuntimeError):
    """A built-in consistency check failed; the output must not be trusted."""


def require(condition, message):
    """Abort preprocessing with an explanatory message unless `condition` holds."""
    if not condition:
        raise PreprocessingError(message)


def section(title):
    """Print a report heading."""
    print()
    print("=" * REPORT_WIDTH)
    print(title)
    print("=" * REPORT_WIDTH)


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def load_raw():
    """Read the published sample and check that it has the documented shape."""
    require(
        INPUT_FILE.exists(),
        f"Input file not found: {INPUT_FILE}. Run this script from the "
        f"contribution folder, with original_data/ in place.",
    )
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")

    expected_columns = ["id", "listnum", "category", "item", "rt", "RTstart", "group", "itemnum"]
    require(
        list(df.columns) == expected_columns,
        f"Unexpected columns in {INPUT_FILE.name}: got {list(df.columns)}, "
        f"expected {expected_columns}. The OSF copy of this file has a different "
        f"header and cannot be used, because it carries no itemnum column.",
    )
    require(
        len(df) == EXPECTED_N_ROWS,
        f"Input has {len(df)} rows, expected {EXPECTED_N_ROWS}.",
    )
    return df


def load_animal_lexicon():
    """Collect every animal name and misspelling shipped with the paper.

    Both files are headerless two-column CSVs whose comment lines start with '#'.
    The scheme file pairs a cluster label with an animal; the spelling file pairs
    a canonical animal name with one observed variant. Both columns of the
    spelling file are kept, so that raw misspelled responses are recognised too.
    """
    lexicon = set()

    def read_pairs(path, columns):
        require(path.exists(), f"Category resource not found: {path}.")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                if not row or row[0].lstrip().startswith("#"):
                    continue
                if len(row) < 2:
                    continue
                for column in columns:
                    lexicon.add(row[column].strip().lower())

    read_pairs(ANIMAL_SCHEME_FILE, columns=(1,))
    read_pairs(ANIMAL_SPELLING_FILE, columns=(0, 1))
    lexicon.discard("")
    return lexicon


# --------------------------------------------------------------------------
# Structural checks on the input
# --------------------------------------------------------------------------
def check_input_structure(df):
    """Verify participant, list and item-order structure before deriving anything."""
    n_participants = df["id"].nunique()
    require(
        n_participants == EXPECTED_N_PARTICIPANTS,
        f"Found {n_participants} participants, expected {EXPECTED_N_PARTICIPANTS}.",
    )

    n_lists = len(df.groupby(["id", "listnum"]))
    require(
        n_lists == EXPECTED_N_LISTS,
        f"Found {n_lists} fluency lists (id x listnum), expected "
        f"{EXPECTED_N_LISTS} as reported in the paper.",
    )

    n_categories = df["category"].nunique()
    require(
        n_categories == EXPECTED_N_CATEGORIES,
        f"Found {n_categories} category labels ({sorted(df['category'].unique())}), "
        f"expected {EXPECTED_N_CATEGORIES}.",
    )

    # itemnum must run 1..n inside every list, with no gaps and no duplicates.
    sizes = df.groupby(["id", "listnum"])["itemnum"].agg(["min", "max", "count", "nunique"])
    broken = sizes[
        (sizes["min"] != 1)
        | (sizes["max"] != sizes["count"])
        | (sizes["nunique"] != sizes["count"])
    ]
    require(
        broken.empty,
        f"itemnum does not run 1..n in {len(broken)} list(s): "
        f"{broken.index.tolist()[:10]}.",
    )

    # The flags below are computed in file order, so the file must already be
    # sorted by participant, then list, then presentation order.
    position = df.groupby(["id", "listnum"]).cumcount() + 1
    require(
        position.equals(df["itemnum"].astype(position.dtype)),
        "Rows are not stored in presentation order within each list; "
        "itemnum does not match row position.",
    )

    # Participant id prefix must agree with the experiment label.
    prefix = df["id"].str[0]
    observed = (
        df.assign(prefix=prefix)
        .groupby("prefix")
        .agg(groups=("group", lambda s: sorted(s.unique())), n=("id", "nunique"))
    )
    require(
        sorted(observed.index) == sorted(EXPECTED_PREFIX_TO_GROUP),
        f"Unexpected participant id prefixes: {sorted(observed.index)}, "
        f"expected {sorted(EXPECTED_PREFIX_TO_GROUP)}.",
    )
    for letter, (group, size) in EXPECTED_PREFIX_TO_GROUP.items():
        row = observed.loc[letter]
        require(
            row["groups"] == [group],
            f"Participant prefix {letter} maps to {row['groups']}, expected ['{group}'].",
        )
        require(
            row["n"] == size,
            f"Prefix {letter} ({group}) has {row['n']} participants, expected {size}.",
        )
    return observed


# --------------------------------------------------------------------------
# Round time limit
# --------------------------------------------------------------------------
def derive_round_time_limits(df):
    """Map each participant to the time limit of one round, in milliseconds.

    Experiment1 and Experiment3 take the value hard-coded in the published task.

    Experiment2 has no published task code, so its limit is reconstructed: the
    task cut a round off at a fixed deadline, so no response can be timestamped
    past the limit, and a participant who kept naming items runs right up to it.
    The limit is therefore the smallest whole-minute candidate not exceeded by
    any of that participant's responses. Nothing here keys on participant id.
    """
    peak = df.groupby("id")["RTstart"].max()
    group_of = df.groupby("id")["group"].first()

    limits = {}
    for participant, highest in peak.items():
        group = group_of[participant]

        if group in DOCUMENTED_LIMIT_GROUPS:
            limits[participant] = DOCUMENTED_TIME_LIMIT_MS
            continue

        require(
            group in RECONSTRUCTED_LIMIT_GROUPS,
            f"Participant {participant} belongs to group '{group}', which has "
            f"neither a documented nor a reconstructable time limit.",
        )
        candidates = [c for c in CANDIDATE_TIME_LIMITS_MS if c >= highest]
        require(
            candidates,
            f"Participant {participant} has a response at {highest} ms, beyond "
            f"every candidate time limit {CANDIDATE_TIME_LIMITS_MS}.",
        )
        limit = min(candidates)
        require(
            highest >= CEILING_TIGHTNESS * limit,
            f"Participant {participant} peaks at {highest} ms, only "
            f"{highest / limit:.1%} of the reconstructed limit of {limit} ms. "
            f"The ceiling is not tight enough to reconstruct a limit from it.",
        )
        limits[participant] = limit

    # A reconstructed limit must partition the group cleanly: participants who
    # completed the same number of rounds must have been given the same limit.
    rounds_per_participant = df.groupby("id")["listnum"].nunique()
    reconstructed = [p for p in limits if group_of[p] in RECONSTRUCTED_LIMIT_GROUPS]
    by_round_count = {}
    for participant in reconstructed:
        by_round_count.setdefault(rounds_per_participant[participant], set()).add(
            limits[participant]
        )
    for round_count, found in by_round_count.items():
        require(
            len(found) == 1,
            f"Participants with {round_count} rounds were assigned more than one "
            f"reconstructed time limit ({sorted(found)}); the reconstruction is "
            f"not consistent with the design.",
        )

    return pd.Series(limits, name="round_time_limit")


def check_time_limits(df):
    """No response may sit past its round's limit by more than the timer drift."""
    overshoot = df["RTstart"] - df["round_time_limit"]
    worst = overshoot.max()
    require(
        worst <= TIMER_DRIFT_TOLERANCE_MS,
        f"A response is timestamped {worst} ms past its round time limit, more "
        f"than the {TIMER_DRIFT_TOLERANCE_MS} ms allowed for timer drift.",
    )
    return overshoot


# --------------------------------------------------------------------------
# Flags
# --------------------------------------------------------------------------
def flag_rt_outliers(df):
    """Mark responses whose latency cannot be taken at face value.

    Two independent symptoms, both computed from the data:

    1. The running total of `rt` inside a list disagrees with `RTstart`. Whenever
       that happens the whole timeline of the list is broken, so every response
       in the list is marked, not only the rows where the sums part company.
    2. `rt` is exactly 0, an impossible interval between two typed responses.
       parsedata.py records one such repair by the authors -- items that a
       participant entered on a single line were split apart afterwards and
       their latencies lost -- but the file holds further zeroed rows that the
       authors did not describe.
    """
    running_total = df.groupby(["id", "listnum"])["rt"].cumsum()
    row_mismatch = (running_total - df["RTstart"]).abs() > RT_RECONCILIATION_TOLERANCE_MS
    list_broken = row_mismatch.groupby([df["id"], df["listnum"]]).transform("any")
    zero_latency = df["rt"] == 0

    return (
        (list_broken | zero_latency).astype(int),
        row_mismatch,
        list_broken,
        zero_latency,
        running_total,
    )


def flag_repeated_responses(df):
    """Mark a response already given earlier in the same list.

    The instructions asked participants not to repeat themselves within a round
    ("Do not enter the same item twice in a round"), but the task never enforced
    it, so repeats are frequent and are counted as perseverations downstream.
    """
    return (df.groupby(["id", "listnum", "item"]).cumcount() > 0).astype(int)


def list_category(df):
    """The category a fluency list was actually run under: its majority label."""
    return df.groupby(["id", "listnum"])["category"].transform(
        lambda labels: labels.mode().iat[0]
    )


def flag_category_mismatch(df, animal_lexicon):
    """Mark responses whose category label contradicts the list they sit in.

    A round was cued with one category, so every response recorded under one
    (id, listnum) key should carry one label. Where a row disagrees with the
    majority label of its own list, that row was filed under the wrong round.
    The label itself is left untouched; only the flag is set.

    A second, independent test guards against a whole list being mislabelled,
    which the majority rule cannot see. Responses are scored against the animal
    lexicon shipped with the paper -- the only category resource published with
    this sample -- and a list is reported if its majority label says animals
    while its contents do not, or the other way round.
    """
    majority = list_category(df)
    mismatch = df["category"] != majority

    is_animal = df["item"].str.strip().str.lower().isin(animal_lexicon)
    animal_share = is_animal.groupby([df["id"], df["listnum"]]).transform("mean")
    labelled_animals = majority == "animals"
    contents_disagree = ((~labelled_animals) & (animal_share >= ANIMAL_SHARE_HIGH)) | (
        labelled_animals & (animal_share <= ANIMAL_SHARE_LOW)
    )
    offending = df.loc[contents_disagree, ["id", "listnum"]].drop_duplicates()
    require(
        offending.empty,
        f"The contents of {len(offending)} list(s) contradict their majority "
        f"category label, which the row-level flag cannot express: "
        f"{offending.to_records(index=False).tolist()}. Review these lists before "
        f"publishing the processed file.",
    )

    return mismatch.astype(int), animal_share, majority


def flag_invalid(df):
    """Mark responses that cannot be interpreted at all.

    A response is uninterpretable if it is missing or blank, or if its latency is
    missing or negative. This sample contains no such row; the column is kept so
    that the flag has the same meaning as elsewhere in the project.
    """
    blank_response = df["item"].isna() | (df["item"].astype(str).str.strip() == "")
    unusable_latency = df["rt"].isna() | (df["rt"] < 0)
    return (blank_response | unusable_latency).astype(int)


def describe_spillover(df):
    """Locate lists whose clock does not start at zero.

    The first response of a round must satisfy RTstart == rt, because RTstart is
    measured from the onset of that round. Where it does not, the timeline of the
    list has been damaged -- in one case demonstrably by a response belonging to
    the preceding list being carried over into the next one.
    """
    firsts = df[df["itemnum"] == 1]
    return firsts[firsts["RTstart"] != firsts["rt"]]


# --------------------------------------------------------------------------
# Output checks
# --------------------------------------------------------------------------
def check_output(out):
    """Verify the delivered table before writing it."""
    require(
        len(out) == EXPECTED_N_ROWS,
        f"Output has {len(out)} rows, expected {EXPECTED_N_ROWS}. Nothing may be "
        f"dropped by this script.",
    )
    require(
        out["participant_id"].nunique() == EXPECTED_N_PARTICIPANTS,
        f"Output has {out['participant_id'].nunique()} participants, expected "
        f"{EXPECTED_N_PARTICIPANTS}.",
    )
    require(
        len(out.groupby(["participant_id", "fluency_list_id"])) == EXPECTED_N_LISTS,
        f"Output has {len(out.groupby(['participant_id', 'fluency_list_id']))} "
        f"fluency lists, expected {EXPECTED_N_LISTS}.",
    )
    require(
        out["stimulus"].nunique() == EXPECTED_N_CATEGORIES,
        f"Output has {out['stimulus'].nunique()} category cues, expected "
        f"{EXPECTED_N_CATEGORIES}.",
    )

    missing = out.isna().sum()
    require(
        missing.sum() == 0,
        f"Output contains missing values: "
        f"{missing[missing > 0].to_dict()}.",
    )

    starts_at_zero = out.groupby(["participant_id", "fluency_list_id"])["trial_order"].min()
    require(
        (starts_at_zero == 0).all(),
        "trial_order is not 0-indexed in every list.",
    )

    for column in ["is_invalid", "is_rt_outlier", "is_repeated_response", "is_category_mismatch"]:
        require(
            out[column].isin([0, 1]).all(),
            f"Column {column} holds values other than 0 and 1.",
        )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    section("INPUT")
    df = load_raw()
    print(f"Read {len(df):,} rows from {INPUT_FILE.relative_to(BASE)}")

    prefixes = check_input_structure(df)
    print(f"Participants            : {df['id'].nunique()}")
    print(f"Fluency lists           : {len(df.groupby(['id', 'listnum'])):,}")
    print(f"Category cues           : {sorted(df['category'].unique())}")
    print("itemnum runs 1..n within every list, with rows in presentation order.")
    print()
    print("Participant id prefix by experiment:")
    for letter in sorted(prefixes.index):
        row = prefixes.loc[letter]
        print(f"  {letter} -> {row['groups'][0]:<12} {row['n']:>3} participants")

    section("ROUND TIME LIMIT")
    limits = derive_round_time_limits(df)
    df["round_time_limit"] = df["id"].map(limits)
    overshoot = check_time_limits(df)

    rounds = df.groupby("id")["listnum"].nunique()
    peak = df.groupby("id")["RTstart"].max()
    group_of = df.groupby("id")["group"].first()
    summary = (
        pd.DataFrame(
            {
                "group": group_of,
                "rounds": rounds,
                "limit": limits,
                "peak": peak,
            }
        )
        .groupby(["group", "rounds", "limit"])
        .agg(participants=("peak", "size"), highest_response=("peak", "max"))
        .reset_index()
    )
    for _, row in summary.iterrows():
        source = (
            "documented in app.js"
            if row["group"] in DOCUMENTED_LIMIT_GROUPS
            else "RECONSTRUCTED from data"
        )
        who = "participant " if row["participants"] == 1 else "participants"
        print(
            f"  {row['group']:<12} {row['participants']:>2} {who}, "
            f"{row['rounds']:>2} rounds, limit {row['limit']:>7,} ms  "
            f"(latest response {row['highest_response']:>7,} ms)  [{source}]"
        )
    print()
    print(
        f"No response passes its limit by more than {overshoot.max():,} ms "
        f"(tolerance {TIMER_DRIFT_TOLERANCE_MS:,} ms, browser timer drift)."
    )

    section("FLAGS")
    animal_lexicon = load_animal_lexicon()
    print(f"Animal lexicon loaded: {len(animal_lexicon):,} names and spelling variants.")

    (
        df["is_rt_outlier"],
        row_mismatch,
        list_broken,
        zero_latency,
        _running_total,
    ) = flag_rt_outliers(df)
    df["is_repeated_response"] = flag_repeated_responses(df)
    df["is_category_mismatch"], animal_share, majority = flag_category_mismatch(
        df, animal_lexicon
    )
    df["is_invalid"] = flag_invalid(df)

    broken_lists = (
        df[list_broken].groupby(["id", "listnum"]).size().index.tolist()
    )
    print()
    print(f"is_rt_outlier         : {int(df['is_rt_outlier'].sum()):>6,} rows")
    print(f"  running total of rt disagrees with RTstart in "
          f"{int(row_mismatch.sum()):,} rows, spread over {len(broken_lists)} lists;")
    print(f"  all {int(list_broken.sum()):,} rows of those lists are flagged, because a "
          f"broken timeline")
    print("  invalidates every latency in the list:")
    for participant, listnum in broken_lists:
        rows = df[(df["id"] == participant) & (df["listnum"] == listnum)]
        key = "{}/{}".format(participant, listnum)
        print(
            f"    {key:<8} {majority[rows.index].iloc[0]:<18} "
            f"{len(rows):>3} responses, {int(row_mismatch[rows.index].sum()):>3} disagree"
        )
    print(f"  rt is exactly 0 in {int(zero_latency.sum()):,} rows "
          f"({sorted({(a, b) for a, b in zip(df.loc[zero_latency, 'id'], df.loc[zero_latency, 'listnum'])})}); "
          f"{int((zero_latency & ~list_broken).sum()):,} of these are not already covered above.")

    repeated_lists = df[df["is_repeated_response"] == 1].groupby(["id", "listnum"]).ngroups
    print()
    print(f"is_repeated_response  : {int(df['is_repeated_response'].sum()):>6,} rows "
          f"in {repeated_lists} lists")

    mismatched = df[df["is_category_mismatch"] == 1]
    list_sizes = df.groupby(["id", "listnum"])["item"].transform("size")
    print()
    print(f"is_category_mismatch  : {int(df['is_category_mismatch'].sum()):>6,} rows")
    print("  Each is a single response filed under a round it does not belong to:")
    for index, row in mismatched.iterrows():
        print(
            f"    {row['id']}/{row['listnum']} item {row['itemnum']} '{row['item']}' "
            f"is labelled '{row['category']}', while the other "
            f"{list_sizes[index] - 1} responses of that list are labelled "
            f"'{majority[index]}'"
        )
        print(f"      rt={row['rt']:,} ms, RTstart={row['RTstart']:,} ms")
    print("  No whole list contradicts its majority label: every list was also")
    print("  scored against the animal lexicon and none disagreed.")
    print("  Labels are reported as recorded and are never rewritten by this script.")

    print()
    print(f"is_invalid            : {int(df['is_invalid'].sum()):>6,} rows")
    if df["is_invalid"].sum() == 0:
        print("    No response is uninterpretable: every row has a non-blank "
              "response and a non-negative latency.")

    spillover = describe_spillover(df)
    print()
    print("Lists whose clock does not start at zero (first response has "
          "RTstart != rt):")
    for index, row in spillover.iterrows():
        key = "{}/{}".format(row["id"], row["listnum"])
        print(
            f"    {key:<8} {majority[index]:<18} "
            f"first response '{row['item']}' rt={row['rt']:,} but "
            f"RTstart={row['RTstart']:,}"
        )
        # If the round really began earlier, some other response of the same
        # participant carries the timestamp this one continues from.
        predecessor_time = int(row["RTstart"]) - int(row["rt"])
        predecessor = df[
            (df["id"] == row["id"])
            & (df["RTstart"] == predecessor_time)
            & (df["listnum"] != row["listnum"])
        ]
        if predecessor.empty:
            print("      no earlier response carries the timestamp it continues from")
        else:
            found = predecessor.iloc[0]
            print(
                f"      continues '{found['item']}' in list "
                f"{found['id']}/{found['listnum']}: {predecessor_time:,} + "
                f"{row['rt']:,} = {row['RTstart']:,}"
            )
    print("  Cases with no such predecessor have no documented cause.")

    # A list whose rows are not stored back to back holds a response that was
    # filed under the wrong round. Reported, not treated as an error: the flags
    # above are computed per (id, listnum) group and are unaffected by it.
    list_key = df["id"].astype(str) + "|" + df["listnum"].astype(str)
    runs = int((list_key != list_key.shift()).sum())
    print()
    print(f"Fluency lists stored as more than one block of rows: "
          f"{runs - EXPECTED_N_LISTS}")
    if runs != EXPECTED_N_LISTS:
        split = list_key.value_counts()
        for key in list_key[list_key != list_key.shift()].value_counts().pipe(
            lambda counts: counts[counts > 1]
        ).index:
            print(f"    {key.replace('|', '/')} ({split[key]} responses) is "
                  f"interrupted by rows from another list")

    padded = df["item"] != df["item"].str.strip()
    print()
    print(f"Responses with surrounding whitespace, kept verbatim: "
          f"{int(padded.sum())} "
          f"({[f'{a}/{b}: {c!r}' for a, b, c in zip(df.loc[padded, 'id'], df.loc[padded, 'listnum'], df.loc[padded, 'item'])]})")

    section("OUTPUT")
    out = pd.DataFrame(
        {
            "participant_id": df["id"],
            "experiment_group": df["group"],
            "fluency_list_id": df["listnum"].astype(int),
            "trial_order": df["itemnum"].astype(int) - 1,  # itemnum is 1-indexed
            "stimulus": df["category"],
            "response": df["item"],
            "rt": df["rt"].astype(int),
            "cumulative_rt": df["RTstart"].astype(int),
            "round_time_limit": df["round_time_limit"].astype(int),
            "is_invalid": df["is_invalid"].astype(int),
            "is_rt_outlier": df["is_rt_outlier"].astype(int),
            "is_repeated_response": df["is_repeated_response"].astype(int),
            "is_category_mismatch": df["is_category_mismatch"].astype(int),
        }
    ).reset_index(drop=True)

    check_output(out)

    PROCESSED_DIR.mkdir(exist_ok=True)
    out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"Wrote {len(out):,} rows x {out.shape[1]} columns to "
          f"{OUTPUT_FILE.relative_to(BASE)}")
    print("No rows were dropped; unusable responses are flagged, not removed.")
    print()
    print("First 15 rows:")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(out.head(15).to_string(index=False))

    return out


if __name__ == "__main__":
    main()
