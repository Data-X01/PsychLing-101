"""Preprocessing for Zemla, Cao, Mueller & Austerweil (2020), Behavior Research Methods.

Semantic fluency: participants named as many members of a cued category as they
could within a fixed time, repeatedly, across nine rounds.

Input : original_data/from_github/fluency_data/snafu_sample.csv
Output: processed_data/exp1.csv  Experiment1 -- animals, fruits, vegetables
        processed_data/exp2.csv  Experiment3 -- animals, foods, tools

Mind the numbering: the output files are named for their position in this
contribution, not for the collection they hold. `exp2.csv` holds the collection
the source file calls Experiment3. There is no file for Experiment2 -- see
EXCLUDED_GROUP below.

Within the two retained collections nothing is filtered out. Responses whose
timing cannot be trusted are marked with flags so that downstream analyses can
exclude them explicitly.

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

# --------------------------------------------------------------------------
# Which collections are kept
# --------------------------------------------------------------------------
# The published sample pools three separate collections. Experiment2 is dropped
# here rather than flagged.
#
# Neither the task code nor a procedural description survives for that group.
# Its round time limit differs from the documented one -- two and four minutes
# against three -- and had to be reconstructed from the ceilings in the data.
# Once one parameter of the procedure is known to have changed, others may have
# changed too, the instruction wording among them. A prompt is a description of
# what a participant was asked to do, and for these twelve participants that
# description cannot be written. Their raw data stay untouched in original_data/.
EXCLUDED_GROUP = "Experiment2"
EXCLUDED_PREFIX = "B"
EXPECTED_N_EXCLUDED = 12

# One output file per retained collection, keyed by the group label in the
# source file. Note again that exp2.csv holds Experiment3.
OUTPUTS = {
    "Experiment1": {
        "file": "exp1.csv",
        "prefix": "A",
        "participants": 20,
        "rows": 4335,
        "lists": 182,
        "categories": ["animals", "fruits", "vegetables"],
    },
    "Experiment3": {
        "file": "exp2.csv",
        "prefix": "C",
        "participants": 50,
        "rows": 13264,
        "lists": 451,
        "categories": ["animals", "foods", "tools"],
    },
}

OUTPUT_COLUMNS = [
    "participant_id",
    "fluency_list_id",
    "trial_order",
    "stimulus",
    "response",
    "rt",
    "cumulative_rt",
    "round_time_limit",
    "is_invalid",
    "is_rt_outlier",
    "is_repeated_response",
    "is_category_mismatch",
]

# --------------------------------------------------------------------------
# Expected structure of the source file
# --------------------------------------------------------------------------
# These describe the file as published, before Experiment2 is dropped. The
# figures the paper reports -- 24,572 responses, 807 lists, 82 participants --
# cover all three collections together, so they are checked here, against the
# source, and never against an output file. Each output file is checked against
# its own counts in OUTPUTS instead.
SOURCE_N_ROWS = 24572
SOURCE_N_PARTICIPANTS = 82
SOURCE_N_LISTS = 807
SOURCE_N_CATEGORIES = 6

# Round time limit, in milliseconds. Documented for both retained collections:
# the published task (original_data/from_github/fluency_task/{web,lab}_version/
# app.js) sets `timeperlist = 180`, and the on-screen instructions say "three
# minutes". Nothing is reconstructed any more; the group whose limit had to be
# inferred is the one excluded above.
TIME_LIMIT_MS = 180_000

# The countdown ran on a browser setInterval, which drifts and is throttled in
# background tabs, so the last response of a round can be timestamped slightly
# after the limit. The largest overshoot in the retained data is 12,758 ms.
TIMER_DRIFT_TOLERANCE_MS = 15_000

# `RTstart` is an integer running total of `rt`, so exact agreement is expected.
RT_RECONCILIATION_TOLERANCE_MS = 0

# Share of a list's responses that must be recognised animal names before the
# list is judged to hold animals regardless of the label it carries.
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
        len(df) == SOURCE_N_ROWS,
        f"Input has {len(df)} rows, expected {SOURCE_N_ROWS}.",
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
# Structural checks on the source file
# --------------------------------------------------------------------------
def check_source_structure(df):
    """Verify the published file before anything is dropped or derived."""
    n_participants = df["id"].nunique()
    require(
        n_participants == SOURCE_N_PARTICIPANTS,
        f"Source has {n_participants} participants, expected {SOURCE_N_PARTICIPANTS}.",
    )

    n_lists = len(df.groupby(["id", "listnum"]))
    require(
        n_lists == SOURCE_N_LISTS,
        f"Source has {n_lists} fluency lists (id x listnum), expected "
        f"{SOURCE_N_LISTS}, the figure the paper reports across all three "
        f"collections.",
    )

    n_categories = df["category"].nunique()
    require(
        n_categories == SOURCE_N_CATEGORIES,
        f"Source has {n_categories} category labels "
        f"({sorted(df['category'].unique())}), expected {SOURCE_N_CATEGORIES}.",
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

    # Every group must occupy exactly one participant id prefix, and vice versa.
    expected_prefixes = {EXCLUDED_PREFIX: EXCLUDED_GROUP}
    expected_prefixes.update({spec["prefix"]: group for group, spec in OUTPUTS.items()})
    observed = (
        df.assign(prefix=df["id"].str[0])
        .groupby("prefix")
        .agg(groups=("group", lambda s: sorted(s.unique())), n=("id", "nunique"))
    )
    require(
        sorted(observed.index) == sorted(expected_prefixes),
        f"Unexpected participant id prefixes: {sorted(observed.index)}, "
        f"expected {sorted(expected_prefixes)}.",
    )
    for prefix, group in expected_prefixes.items():
        require(
            observed.loc[prefix, "groups"] == [group],
            f"Participant prefix {prefix} maps to "
            f"{observed.loc[prefix, 'groups']}, expected ['{group}'].",
        )
    return observed


def split_off_excluded(df):
    """Separate the collection that cannot be described, and check its size."""
    excluded = df[df["group"] == EXCLUDED_GROUP]
    retained = df[df["group"] != EXCLUDED_GROUP]

    require(
        excluded["id"].nunique() == EXPECTED_N_EXCLUDED,
        f"Excluding {EXCLUDED_GROUP} removed "
        f"{excluded['id'].nunique()} participants, expected {EXPECTED_N_EXCLUDED}.",
    )
    require(
        (excluded["id"].str[0] == EXCLUDED_PREFIX).all(),
        f"Not every excluded participant has the '{EXCLUDED_PREFIX}' prefix.",
    )
    require(
        sorted(retained["group"].unique()) == sorted(OUTPUTS),
        f"After exclusion the retained groups are "
        f"{sorted(retained['group'].unique())}, expected {sorted(OUTPUTS)}.",
    )
    return retained, excluded


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

    return (list_broken | zero_latency).astype(int), row_mismatch, list_broken, zero_latency


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

    return mismatch.astype(int), majority


def flag_invalid(df):
    """Mark responses that cannot be interpreted at all.

    A response is uninterpretable if it is missing or blank, or if its latency is
    missing or negative. The retained data contain no such row; the column is
    kept so that the flag has the same meaning as elsewhere in the project.
    """
    blank_response = df["item"].isna() | (df["item"].astype(str).str.strip() == "")
    unusable_latency = df["rt"].isna() | (df["rt"] < 0)
    return (blank_response | unusable_latency).astype(int)


def describe_spillover(df):
    """Locate lists whose clock does not start at zero.

    The first response of a round must satisfy RTstart == rt, because RTstart is
    measured from the onset of that round. Where it does not, the timeline of the
    list has been damaged.
    """
    firsts = df[df["itemnum"] == 1]
    return firsts[firsts["RTstart"] != firsts["rt"]]


# --------------------------------------------------------------------------
# Output checks
# --------------------------------------------------------------------------
def check_output(out, group, spec):
    """Verify one delivered table before writing it."""
    name = spec["file"]
    require(
        list(out.columns) == OUTPUT_COLUMNS,
        f"{name}: columns are {list(out.columns)}, expected {OUTPUT_COLUMNS}.",
    )
    require(
        len(out) == spec["rows"],
        f"{name} has {len(out)} rows, expected {spec['rows']} for {group}.",
    )
    require(
        out["participant_id"].nunique() == spec["participants"],
        f"{name} has {out['participant_id'].nunique()} participants, expected "
        f"{spec['participants']} for {group}.",
    )
    require(
        (out["participant_id"].str[0] == spec["prefix"]).all(),
        f"{name} holds participant ids outside the '{spec['prefix']}' prefix.",
    )

    # Per-file list count. The paper's 807 is a total across all three
    # collections, the excluded one included, so it cannot be checked here.
    n_lists = len(out.groupby(["participant_id", "fluency_list_id"]))
    require(
        n_lists == spec["lists"],
        f"{name} has {n_lists} fluency lists, expected {spec['lists']} for {group}.",
    )

    require(
        sorted(out["stimulus"].unique()) == sorted(spec["categories"]),
        f"{name} has categories {sorted(out['stimulus'].unique())}, expected "
        f"{sorted(spec['categories'])} for {group}.",
    )
    require(
        sorted(out["round_time_limit"].unique()) == [TIME_LIMIT_MS],
        f"{name} has round time limits {sorted(out['round_time_limit'].unique())}, "
        f"expected only {TIME_LIMIT_MS}.",
    )

    missing = out.isna().sum()
    require(
        missing.sum() == 0,
        f"{name} contains missing values: {missing[missing > 0].to_dict()}.",
    )

    starts_at_zero = out.groupby(["participant_id", "fluency_list_id"])["trial_order"].min()
    require(
        (starts_at_zero == 0).all(),
        f"{name}: trial_order is not 0-indexed in every list.",
    )

    for column in ["is_invalid", "is_rt_outlier", "is_repeated_response", "is_category_mismatch"]:
        require(
            out[column].isin([0, 1]).all(),
            f"{name}: column {column} holds values other than 0 and 1.",
        )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    section("SOURCE")
    df = load_raw()
    print(f"Read {len(df):,} rows from {INPUT_FILE.relative_to(BASE)}")
    prefixes = check_source_structure(df)
    print(f"Participants            : {df['id'].nunique()}")
    print(f"Fluency lists           : {len(df.groupby(['id', 'listnum'])):,}  "
          f"(the paper's figure, across all three collections)")
    print(f"Category cues           : {sorted(df['category'].unique())}")
    print("itemnum runs 1..n within every list, with rows in presentation order.")
    print()
    print("Participant id prefix by collection:")
    for prefix in sorted(prefixes.index):
        row = prefixes.loc[prefix]
        print(f"  {prefix} -> {row['groups'][0]:<12} {row['n']:>3} participants")

    section(f"EXCLUDING {EXCLUDED_GROUP}")
    retained, excluded = split_off_excluded(df)
    print(f"Dropped {excluded['id'].nunique()} participants, {len(excluded):,} responses, "
          f"{len(excluded.groupby(['id', 'listnum']))} lists.")
    print("Reason: no task code and no procedural description survive for this")
    print("collection, and its round time limit is not the documented one. The")
    print("ceilings its responses stop at, in whole minutes:")
    ceilings = excluded.groupby("id")["RTstart"].max()
    for minutes in sorted({round(v / 60_000) for v in ceilings}):
        who = sorted(
            (p for p, v in ceilings.items() if round(v / 60_000) == minutes),
            key=lambda x: int(x[1:]),
        )
        highest = max(ceilings[p] for p in who)
        print(f"  {minutes} min: {who} (latest response {highest:,} ms)")
    print("Against three minutes everywhere else. Since one parameter of the")
    print("procedure demonstrably changed, others may have changed too, so what")
    print("these participants were asked to do cannot be stated. Their rows stay")
    print("in original_data/ untouched.")

    section("FLAGS")
    animal_lexicon = load_animal_lexicon()
    print(f"Animal lexicon loaded: {len(animal_lexicon):,} names and spelling variants.")

    retained = retained.copy()
    retained["round_time_limit"] = TIME_LIMIT_MS
    overshoot = (retained["RTstart"] - retained["round_time_limit"]).max()
    require(
        overshoot <= TIMER_DRIFT_TOLERANCE_MS,
        f"A response is timestamped {overshoot} ms past the {TIME_LIMIT_MS} ms "
        f"round time limit, more than the {TIMER_DRIFT_TOLERANCE_MS} ms allowed "
        f"for timer drift.",
    )
    print(f"Round time limit {TIME_LIMIT_MS:,} ms for every retained participant "
          f"(app.js: timeperlist = 180).")
    print(f"No response passes it by more than {overshoot:,} ms "
          f"(tolerance {TIMER_DRIFT_TOLERANCE_MS:,} ms, browser timer drift).")

    (
        retained["is_rt_outlier"],
        row_mismatch,
        list_broken,
        zero_latency,
    ) = flag_rt_outliers(retained)
    retained["is_repeated_response"] = flag_repeated_responses(retained)
    retained["is_category_mismatch"], majority = flag_category_mismatch(
        retained, animal_lexicon
    )
    retained["is_invalid"] = flag_invalid(retained)

    broken_lists = retained[list_broken].groupby(["id", "listnum"]).size().index.tolist()
    print()
    print(f"is_rt_outlier         : {int(retained['is_rt_outlier'].sum()):>6,} rows")
    print(f"  running total of rt disagrees with RTstart in "
          f"{int(row_mismatch.sum()):,} rows, spread over {len(broken_lists)} lists;")
    print(f"  all {int(list_broken.sum()):,} rows of those lists are flagged, because a "
          f"broken timeline")
    print("  invalidates every latency in the list:")
    for participant, listnum in broken_lists:
        rows = retained[(retained["id"] == participant) & (retained["listnum"] == listnum)]
        key = "{}/{}".format(participant, listnum)
        print(
            f"    {key:<8} {majority[rows.index].iloc[0]:<18} "
            f"{len(rows):>3} responses, {int(row_mismatch[rows.index].sum()):>3} disagree"
        )
    zero_lists = sorted({(a, b) for a, b in
                         zip(retained.loc[zero_latency, "id"],
                             retained.loc[zero_latency, "listnum"])})
    print(f"  rt is exactly 0 in {int(zero_latency.sum()):,} rows ({zero_lists}); "
          f"{int((zero_latency & ~list_broken).sum()):,} of these are not already "
          f"covered above.")

    repeated_lists = retained[retained["is_repeated_response"] == 1].groupby(
        ["id", "listnum"]
    ).ngroups
    print()
    print(f"is_repeated_response  : {int(retained['is_repeated_response'].sum()):>6,} rows "
          f"in {repeated_lists} lists")

    mismatched = retained[retained["is_category_mismatch"] == 1]
    print()
    print(f"is_category_mismatch  : {len(mismatched):>6,} rows")
    if mismatched.empty:
        print("    No response is filed under a round it does not belong to. Both "
              "such rows in")
        print("    the published sample belong to the excluded collection. Every "
              "list was also")
        print("    scored against the animal lexicon and none contradicted its "
              "majority label.")
    else:
        list_sizes = retained.groupby(["id", "listnum"])["item"].transform("size")
        for index, row in mismatched.iterrows():
            print(
                f"    {row['id']}/{row['listnum']} item {row['itemnum']} "
                f"'{row['item']}' is labelled '{row['category']}', while the other "
                f"{list_sizes[index] - 1} responses of that list are labelled "
                f"'{majority[index]}'"
            )

    print()
    print(f"is_invalid            : {int(retained['is_invalid'].sum()):>6,} rows")
    if retained["is_invalid"].sum() == 0:
        print("    No response is uninterpretable: every row has a non-blank "
              "response and a non-negative latency.")

    spillover = describe_spillover(retained)
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
        predecessor_time = int(row["RTstart"]) - int(row["rt"])
        predecessor = retained[
            (retained["id"] == row["id"])
            & (retained["RTstart"] == predecessor_time)
            & (retained["listnum"] != row["listnum"])
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

    list_key = retained["id"].astype(str) + "|" + retained["listnum"].astype(str)
    runs = int((list_key != list_key.shift()).sum())
    n_lists = len(retained.groupby(["id", "listnum"]))
    print()
    print(f"Fluency lists stored as more than one block of rows: {runs - n_lists}")

    padded = retained["item"] != retained["item"].str.strip()
    print()
    print(f"Responses with surrounding whitespace, kept verbatim: {int(padded.sum())}"
          + (f" ({[f'{a}/{b}: {c!r}' for a, b, c in zip(retained.loc[padded, 'id'], retained.loc[padded, 'listnum'], retained.loc[padded, 'item'])]})"
             if padded.any() else ""))

    section("OUTPUT")
    # `experiment_group` is deliberately absent: one collection per file means
    # the column would hold a single repeated value and encode nothing. The
    # file-to-collection mapping lives in OUTPUTS and in the README.
    PROCESSED_DIR.mkdir(exist_ok=True)
    written = []
    for group, spec in OUTPUTS.items():
        rows = retained[retained["group"] == group]
        out = pd.DataFrame(
            {
                "participant_id": rows["id"],
                "fluency_list_id": rows["listnum"].astype(int),
                "trial_order": rows["itemnum"].astype(int) - 1,  # itemnum is 1-indexed
                "stimulus": rows["category"],
                "response": rows["item"],
                "rt": rows["rt"].astype(int),
                "cumulative_rt": rows["RTstart"].astype(int),
                "round_time_limit": rows["round_time_limit"].astype(int),
                "is_invalid": rows["is_invalid"].astype(int),
                "is_rt_outlier": rows["is_rt_outlier"].astype(int),
                "is_repeated_response": rows["is_repeated_response"].astype(int),
                "is_category_mismatch": rows["is_category_mismatch"].astype(int),
            }
        ).reset_index(drop=True)

        check_output(out, group, spec)
        path = PROCESSED_DIR / spec["file"]
        out.to_csv(path, index=False, encoding="utf-8")
        written.append((group, spec, out))
        print(
            f"{spec['file']:<9} {group:<12} {len(out):>6,} rows  "
            f"{out['participant_id'].nunique():>2} participants  "
            f"{len(out.groupby(['participant_id', 'fluency_list_id'])):>3} lists  "
            f"{sorted(out['stimulus'].unique())}"
        )

    total_rows = sum(len(out) for _, _, out in written)
    total_participants = sum(out["participant_id"].nunique() for _, _, out in written)
    total_lists = sum(
        len(out.groupby(["participant_id", "fluency_list_id"])) for _, _, out in written
    )
    print()
    print(f"Delivered {total_rows:,} rows, {total_participants} participants, "
          f"{total_lists} lists across {len(written)} files.")
    print(f"Excluded {len(excluded):,} rows, {excluded['id'].nunique()} participants, "
          f"{len(excluded.groupby(['id', 'listnum']))} lists ({EXCLUDED_GROUP}).")
    print(f"Source totals were {SOURCE_N_ROWS:,} rows, {SOURCE_N_PARTICIPANTS} "
          f"participants, {SOURCE_N_LISTS} lists.")
    require(
        total_rows + len(excluded) == SOURCE_N_ROWS,
        f"{total_rows} delivered plus {len(excluded)} excluded do not add up to "
        f"the {SOURCE_N_ROWS} rows read in.",
    )

    print()
    print("Flags per file:")
    for group, spec, out in written:
        flags = {c: int(out[c].sum()) for c in OUTPUT_COLUMNS if c.startswith("is_")}
        print(f"  {spec['file']:<9} {flags}")

    print()
    print(f"First 15 rows of {written[0][1]['file']}:")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(written[0][2].head(15).to_string(index=False))

    return written


if __name__ == "__main__":
    main()
