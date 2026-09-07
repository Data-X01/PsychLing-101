"""Build PsychLing-101 prompts for Zemla, Cao, Mueller & Austerweil (2020), BRM.

One JSON line per participant. The prompt replays that participant's whole
session: the on-screen instructions, then every round in order, then every item
they named inside each round, with the feedback screen the task showed between
rounds.

Input : processed_data/exp1.csv (written by preprocess_data.py)
Output: prompts.jsonl.zip, holding prompts.jsonl

All wording shown to the participant is taken verbatim from the published task,
original_data/from_github/fluency_task/web_version/main.html. Only two values
are substituted -- the time limit and the number of rounds -- because those
differ between the three pooled experiments while the HTML hard-codes the values
of Experiment1. A built-in check re-inserts the original values and compares the
result against the HTML, so the claim of verbatim wording is verified on
every run.

Run from the contribution folder:  python3 generate_prompts.py
"""

from pathlib import Path
import html as html_module
import json
import re
import zipfile

import pandas as pd

BASE = Path(__file__).resolve().parent
INPUT_FILE = BASE / "processed_data" / "exp1.csv"
TASK_HTML = BASE / "original_data" / "from_github" / "fluency_task" / "web_version" / "main.html"
JSONL_FILE = BASE / "prompts.jsonl"
ZIP_FILE = BASE / "prompts.jsonl.zip"

EXPERIMENT = "zemla2020_semantic_fluency/exp1"

EXPECTED_N_PARTICIPANTS = 82
EXPECTED_N_RESPONSES = 24572

# PsychLing-101 budget for one prompt.
TOKEN_LIMIT = 32_000
# Character-to-token heuristic used elsewhere in this repository; conservative
# for English. tiktoken is used instead when it is importable.
TOKENS_PER_CHAR = 0.30

# A fixed timestamp and fixed member metadata make the archive byte-identical
# across runs; zipfile would otherwise stamp the current mtime into it.
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_MEMBER_NAME = "prompts.jsonl"

NUMBER_WORDS = {
    2: "two", 3: "three", 4: "four", 8: "eight", 9: "nine",
    10: "ten", 12: "twelve", 18: "eighteen",
}

# --------------------------------------------------------------------------
# Wording, transcribed from main.html
# --------------------------------------------------------------------------
# The instructions screen. "three minutes" and "nine times" are the only
# substituted spans; everything else is the published text.
INSTRUCTIONS = (
    "Instructions\n"
    "For each round in this task, you will be given a category and asked to "
    "list as many items from that category as you can. For instance, if the "
    "category is instruments, you should list as many instruments as you can "
    "recall.\n"
    "- You will have {minutes} minutes to list as many items from the category "
    "as possible.\n"
    "- Please rely only on memory, and do not search the Internet for answers.\n"
    "- Do not enter the same item twice in a round, or list two items with the "
    'same suffix. For example if you list "guitar", do not list "guitars" in '
    "the same round.\n"
    "You will be asked to do this {rounds} times in total."
)

# Shown on both feedback screens. Experiment2 alternated two categories rather
# than sampling from three, so this notice is dropped for that group: whether
# participants were told a category could repeat is not established for them.
REPEAT_NOTICE = (
    "The next round may or may not be a category you have already done. If it "
    "is a category you've already done, it's OK to list items you've listed "
    "before, but you may also list new items."
)

# Shown after a round that met the response threshold and was not the last.
BETWEEN_ROUNDS = (
    "Times up!\n"
    "You named {count} {category}.\n"
    "\n"
    "You have completed {done} of {total} rounds.\n"
    "\n"
    "{repeat_notice}Please try to list as many items as possible, but only "
    "list an item once per round."
)

# Shown after a round with five or fewer responses, which the task replayed.
TOO_FEW = (
    "Uh-oh...\n"
    "You only entered {count} {category}!\n"
    "\n"
    "Let's try that round again! Please use the entire allotted time to try "
    "and generate as many items as possible, listing each item once per "
    "round.{repeat_notice}"
)

# The task replayed any round with this many responses or fewer (app.js:126).
REPLAY_THRESHOLD = 5

# How many rounds a participant was told to expect. This is a property of the
# design, not of the delivered data: app.js ran `categories.length * numx` = 3 x 3
# rounds and, when a round was replayed, decremented its counter so the extra
# round did not raise the total. A participant who replayed a round therefore
# contributes ten lists to the data but was told about nine throughout.
DESIGN_ROUNDS = {"Experiment1": 9, "Experiment3": 9}

ROUND_HEADER = "Round {number}. Category: {category}. You have {minutes} minutes."
RESPONSE_LINE = "You say <<{item}>> after <<{rt}>> ms."


class PromptGenerationError(RuntimeError):
    """A built-in consistency check failed; the prompts must not be published."""


def require(condition, message):
    """Abort generation with an explanatory message unless `condition` holds."""
    if not condition:
        raise PromptGenerationError(message)


def number_word(value):
    """Spell out a small integer, matching the register of the published text."""
    require(
        value in NUMBER_WORDS,
        f"No spelled-out form for {value}; extend NUMBER_WORDS before using it "
        f"in text that quotes the published instructions.",
    )
    return NUMBER_WORDS[value]


# --------------------------------------------------------------------------
# Verifying the transcription against the published task
# --------------------------------------------------------------------------
def screen_text(markup, div_id):
    """Return the visible text of one screen of the task, tags removed.

    Buttons are dropped: they are controls rather than wording. Rivets
    placeholders such as {game.category} are left in place, so that the
    templates above can be checked against them.
    """
    match = re.search(
        rf'<div id="{div_id}">(.*?)</div>', markup, flags=re.DOTALL
    )
    require(match, f"Screen '{div_id}' not found in {TASK_HTML.name}.")
    body = re.sub(r"<a\b.*?</a>", " ", match.group(1), flags=re.DOTALL)
    return html_module.unescape(re.sub(r"<[^>]+>", " ", body))


def normalise(text):
    """Collapse every run of whitespace, so line breaking cannot affect a match."""
    return " ".join(text.split())


def check_wording_is_verbatim():
    """Confirm the templates reproduce the published screens word for word."""
    markup = TASK_HTML.read_text(encoding="utf-8")

    # main.html hard-codes the parameters of Experiment1, so put those back.
    rebuilt_instructions = INSTRUCTIONS.format(minutes="three", rounds="nine")
    rebuilt_instructions = rebuilt_instructions.replace("- ", " ")

    # The screens carry the task's own placeholders; fill the templates with the
    # very same strings so the two sides can be compared directly.
    rebuilt_between = BETWEEN_ROUNDS.format(
        count="{ game.items | length }",
        category="{game.category}",
        done="{ game.gamenum }",
        total="9",
        repeat_notice=REPEAT_NOTICE + " ",
    )
    rebuilt_too_few = TOO_FEW.format(
        count="{ game.items | length }",
        category="{game.category}",
        repeat_notice=" " + REPEAT_NOTICE,
    )

    for div_id, rebuilt in [
        ("instructions", rebuilt_instructions),
        ("between_categories", rebuilt_between),
        ("too_few", rebuilt_too_few),
    ]:
        published = normalise(screen_text(markup, div_id))
        require(
            normalise(rebuilt) == published,
            f"The template for screen '{div_id}' is not verbatim.\n"
            f"  template : {normalise(rebuilt)}\n"
            f"  published: {published}",
        )
    return True


# --------------------------------------------------------------------------
# Building one prompt
# --------------------------------------------------------------------------
def participant_sort_key(participant_id):
    """Order A101 < A102 < ... < B1 < B2 < ... < B10, not lexicographically."""
    match = re.fullmatch(r"([A-Za-z]+)(\d+)", participant_id)
    require(
        match, f"Participant id '{participant_id}' is not a letter-plus-number id."
    )
    return match.group(1), int(match.group(2))


def design_round_count(participant_id, group_name, round_sizes):
    """How many rounds the participant was told the task would have.

    Experiment1 and Experiment3 ran the published task, whose total is fixed at
    nine and is unaffected by replays. No task code was published for
    Experiment2, so its total is read off the data; that is only sound because
    no Experiment2 round fell to the replay threshold, which is asserted here.
    """
    if group_name in DESIGN_ROUNDS:
        return DESIGN_ROUNDS[group_name]

    short = [n for n in round_sizes if n <= REPLAY_THRESHOLD]
    require(
        not short,
        f"Participant {participant_id} is in {group_name}, whose design total is "
        f"taken from the data, but has {len(short)} round(s) at or below the "
        f"replay threshold. Replays make the number of lists larger than the "
        f"number of rounds announced, so the total cannot be read off the data.",
    )
    return len(round_sizes)


def build_prompt(participant_id, rows):
    """Render one participant's whole session, and collect their latencies."""
    rows = rows.sort_values(["fluency_list_id", "trial_order"], kind="stable")

    limits = rows["round_time_limit"].unique()
    require(
        len(limits) == 1,
        f"Participant {participant_id} has more than one round time limit "
        f"({sorted(limits)}); the instructions can only state one.",
    )
    limit_ms = int(limits[0])
    require(
        limit_ms % 60_000 == 0,
        f"Participant {participant_id} has a round time limit of {limit_ms} ms, "
        f"which is not a whole number of minutes.",
    )
    minutes = limit_ms // 60_000

    groups = list(rows.groupby("fluency_list_id", sort=True))
    n_lists = len(groups)
    round_sizes = [len(round_rows) for _, round_rows in groups]

    group_name = rows["experiment_group"].iloc[0]
    design_total = design_round_count(participant_id, group_name, round_sizes)
    require(
        round_sizes[-1] > REPLAY_THRESHOLD,
        f"Participant {participant_id} ends on a round of {round_sizes[-1]} "
        f"responses, which the task would have replayed. The session is "
        f"truncated in a way this script cannot narrate.",
    )

    # Experiment2 alternated two categories; the notice about a category
    # possibly repeating is not established for that design, so it is dropped.
    repeat_notice = "" if group_name == "Experiment2" else REPEAT_NOTICE

    parts = [
        INSTRUCTIONS.format(
            minutes=number_word(minutes), rounds=number_word(design_total)
        )
    ]

    latencies = []
    # Mirrors app.js `gamenum`: incremented when a round starts and decremented
    # again when it has to be replayed, so it counts rounds that actually stood.
    completed = 0
    for position, (_, round_rows) in enumerate(groups, start=1):
        category = round_rows["stimulus"].iloc[0]
        block = [
            # Rounds are numbered over the lists in the data, so that a replayed
            # round and its retry never share a number.
            ROUND_HEADER.format(
                number=position, category=category, minutes=minutes
            )
        ]
        for _, row in round_rows.iterrows():
            rt = int(row["rt"])
            block.append(RESPONSE_LINE.format(item=row["response"], rt=rt))
            latencies.append(rt)
        parts.append("\n".join(block))

        replayed = len(round_rows) <= REPLAY_THRESHOLD
        if not replayed:
            completed += 1

        if position == n_lists:
            continue  # the last round is followed by the end of the session

        if replayed:
            parts.append(
                TOO_FEW.format(
                    count=len(round_rows),
                    category=category,
                    repeat_notice=f" {repeat_notice}" if repeat_notice else "",
                )
            )
        else:
            parts.append(
                BETWEEN_ROUNDS.format(
                    count=len(round_rows),
                    category=category,
                    done=completed,
                    total=design_total,
                    repeat_notice=f"{repeat_notice} " if repeat_notice else "",
                )
            )

    require(
        completed <= design_total,
        f"Participant {participant_id} completed {completed} rounds, more than "
        f"the {design_total} the instructions announce.",
    )
    return "\n\n".join(parts), latencies, n_lists, design_total, minutes


# --------------------------------------------------------------------------
# Checks on the finished prompts
# --------------------------------------------------------------------------
def count_tokens(text, encoder):
    """Token count: exact where a tokeniser is available, estimated otherwise."""
    if encoder is not None:
        return len(encoder.encode(text))
    return int(len(text) * TOKENS_PER_CHAR) + 1


def check_prompts(prompts, df):
    """Verify every prompt against the table it was built from."""
    require(
        len(prompts) == EXPECTED_N_PARTICIPANTS,
        f"Built {len(prompts)} prompts, expected {EXPECTED_N_PARTICIPANTS} "
        f"(one per participant).",
    )

    total_responses = 0
    for record in prompts:
        participant_id = record["participant_id"]
        rows = df[df["participant_id"] == participant_id]
        n_responses = len(rows)
        total_responses += n_responses
        text = record["text"]

        # Every response contributes one marked item and one marked latency.
        require(
            text.count("<<") == 2 * n_responses
            and text.count(">>") == 2 * n_responses,
            f"Participant {participant_id}: found {text.count('<<')} '<<' and "
            f"{text.count('>>')} '>>', expected {2 * n_responses} of each for "
            f"{n_responses} responses.",
        )

        require(
            len(record["rt"]) == n_responses,
            f"Participant {participant_id}: rt holds {len(record['rt'])} values "
            f"for {n_responses} responses.",
        )
        expected_rt = (
            rows.sort_values(["fluency_list_id", "trial_order"], kind="stable")["rt"]
            .astype(int)
            .tolist()
        )
        require(
            record["rt"] == expected_rt,
            f"Participant {participant_id}: rt is not the presentation-order "
            f"sequence of the rt column.",
        )

        # Round headers are one per list in the data, numbered without gaps, so
        # that a replayed round and its retry get distinct numbers.
        n_lists = rows["fluency_list_id"].nunique()
        headers = re.findall(
            r"^Round (\d+)\. Category: (.+?)\. You have (\d+) minutes\.$",
            text,
            flags=re.MULTILINE,
        )
        require(
            len(headers) == n_lists,
            f"Participant {participant_id}: text has {len(headers)} round "
            f"headers, the data has {n_lists} lists.",
        )
        require(
            [int(number) for number, _, _ in headers] == list(range(1, n_lists + 1)),
            f"Participant {participant_id}: rounds are not numbered 1..{n_lists}.",
        )

        # The announced total comes from the design instead, so that a replay
        # does not inflate it -- exactly as the task's own counter behaved.
        round_sizes = [
            len(group)
            for _, group in rows.sort_values(
                ["fluency_list_id", "trial_order"], kind="stable"
            ).groupby("fluency_list_id", sort=True)
        ]
        design_total = design_round_count(
            participant_id, rows["experiment_group"].iloc[0], round_sizes
        )
        announced = re.search(
            r"You will be asked to do this (\w+) times in total\.", text
        )
        require(
            announced and announced.group(1) == number_word(design_total),
            f"Participant {participant_id}: the instructions announce "
            f"'{announced.group(1) if announced else None}' rounds, expected "
            f"'{number_word(design_total)}' for the design.",
        )

        progress = [
            (int(done), int(total))
            for done, total in re.findall(
                r"You have completed (\d+) of (\d+) rounds\.", text
            )
        ]
        require(
            all(total == design_total for _, total in progress),
            f"Participant {participant_id}: a progress line states a total other "
            f"than the design total of {design_total}: "
            f"{sorted({total for _, total in progress})}.",
        )
        counted = [done for done, _ in progress]
        require(
            counted == sorted(set(counted)) and all(d <= design_total for d in counted),
            f"Participant {participant_id}: the completed-round counter is not "
            f"strictly increasing within 1..{design_total}: {counted}.",
        )
        # A replayed round must not advance the counter.
        n_replays = sum(1 for size in round_sizes if size <= REPLAY_THRESHOLD)
        require(
            len(counted) == n_lists - 1 - n_replays,
            f"Participant {participant_id}: {len(counted)} progress lines for "
            f"{n_lists} lists with {n_replays} replay(s); expected "
            f"{n_lists - 1 - n_replays}.",
        )

        # The stated limit must be the one recorded for every row.
        limit_ms = int(rows["round_time_limit"].iloc[0])
        for _, _, stated in headers:
            require(
                int(stated) * 60_000 == limit_ms,
                f"Participant {participant_id}: a round states {stated} minutes, "
                f"but round_time_limit is {limit_ms} ms.",
            )

        # Each header's category must match the list it stands for.
        by_round = [
            group["stimulus"].iloc[0]
            for _, group in rows.sort_values(
                ["fluency_list_id", "trial_order"], kind="stable"
            ).groupby("fluency_list_id", sort=True)
        ]
        require(
            [category for _, category, _ in headers] == by_round,
            f"Participant {participant_id}: round categories in the text do not "
            f"match the stimulus column.",
        )

        # Angle brackets are reserved for the markup.
        stripped = re.sub(r"<<[^<>]*>>", "", text)
        require(
            "<" not in stripped and ">" not in stripped,
            f"Participant {participant_id}: '<' or '>' occurs outside the "
            f"<<...>> markup.",
        )

    require(
        total_responses == EXPECTED_N_RESPONSES,
        f"Prompts cover {total_responses} responses, expected "
        f"{EXPECTED_N_RESPONSES}.",
    )
    return total_responses


def write_reproducible_zip(jsonl_path, zip_path):
    """Compress the JSONL with fixed member metadata, then drop the plain file."""
    payload = jsonl_path.read_bytes()
    info = zipfile.ZipInfo(ZIP_MEMBER_NAME, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    info.create_system = 3  # Unix, so the host OS cannot leak into the archive
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(info, payload)
    jsonl_path.unlink()


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    require(
        INPUT_FILE.exists(),
        f"Input file not found: {INPUT_FILE}. Run preprocess_data.py first, "
        f"from the contribution folder.",
    )
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")
    require(
        len(df) == EXPECTED_N_RESPONSES,
        f"{INPUT_FILE.name} has {len(df)} rows, expected {EXPECTED_N_RESPONSES}.",
    )
    require(
        int(df["is_invalid"].sum()) == 0,
        f"{int(df['is_invalid'].sum())} response(s) are flagged is_invalid. "
        f"Decide how to render them before generating prompts; this script "
        f"assumes every response can be stated as given.",
    )

    check_wording_is_verbatim()
    print(f"Wording verified verbatim against {TASK_HTML.name} "
          f"(instructions, between_categories, too_few).")

    try:
        import tiktoken

        encoder = tiktoken.get_encoding("cl100k_base")
        token_method = "tiktoken cl100k_base, exact"
    except Exception:
        encoder = None
        token_method = f"estimate, {TOKENS_PER_CHAR} tokens per character"

    prompts = []
    for participant_id in sorted(df["participant_id"].unique(), key=participant_sort_key):
        rows = df[df["participant_id"] == participant_id]
        text, latencies, n_lists, design_total, minutes = build_prompt(
            participant_id, rows
        )
        prompts.append(
            {
                "text": text,
                "experiment": EXPERIMENT,
                "participant_id": participant_id,
                "rt": latencies,
            }
        )

    total_responses = check_prompts(prompts, df)

    with JSONL_FILE.open("w", encoding="utf-8", newline="\n") as handle:
        for record in prompts:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_reproducible_zip(JSONL_FILE, ZIP_FILE)

    # ---------------------------------------------------------------- report
    print()
    print(f"Wrote {len(prompts)} prompts to {ZIP_FILE.name} "
          f"(member: {ZIP_MEMBER_NAME}, fixed timestamp for reproducibility)")
    print(f"Responses covered: {total_responses:,} of {EXPECTED_N_RESPONSES:,}")

    by_group = df.groupby("experiment_group").agg(
        participants=("participant_id", "nunique"),
        responses=("response", "size"),
    )
    print()
    print("By experiment:")
    for group, row in by_group.iterrows():
        rounds = sorted(
            df[df["experiment_group"] == group]
            .groupby("participant_id")["fluency_list_id"]
            .nunique()
            .unique()
        )
        minutes = sorted(
            m // 60_000
            for m in df[df["experiment_group"] == group]["round_time_limit"].unique()
        )
        announced = sorted(
            {
                design_round_count(
                    pid,
                    group,
                    list(
                        df[df["participant_id"] == pid]
                        .groupby("fluency_list_id")
                        .size()
                    ),
                )
                for pid in df[df["experiment_group"] == group]["participant_id"].unique()
            }
        )
        print(
            f"  {group:<12} {row['participants']:>2} participants, "
            f"{row['responses']:>6,} responses, lists per participant {rounds}, "
            f"rounds announced {announced}, minutes per round {minutes}"
        )

    lengths = [len(record["text"]) for record in prompts]
    tokens = [count_tokens(record["text"], encoder) for record in prompts]
    longest = prompts[tokens.index(max(tokens))]["participant_id"]
    print()
    print(f"Token counting method: {token_method}")
    print(f"Tokens per participant: max {max(tokens):,} ({longest}), "
          f"median {sorted(tokens)[len(tokens) // 2]:,}, min {min(tokens):,}")
    print(f"Characters per participant: max {max(lengths):,}, min {min(lengths):,}")
    require(
        max(tokens) <= TOKEN_LIMIT,
        f"Participant {longest} needs {max(tokens):,} tokens, over the "
        f"{TOKEN_LIMIT:,}-token limit. Split that session before publishing.",
    )
    print(f"Within the {TOKEN_LIMIT:,}-token limit, with "
          f"{TOKEN_LIMIT - max(tokens):,} tokens to spare.")

    # Flags travel with processed_data/exp1.csv rather than with the prompts;
    # report how much flagged material the prompts contain.
    print()
    print("Flagged responses reproduced in the prompts "
          "(see processed_data/exp1.csv to filter them):")
    for flag in ["is_rt_outlier", "is_repeated_response", "is_category_mismatch"]:
        print(f"  {flag:<22} {int(df[flag].sum()):>6,} responses")
    replays = df.groupby(["participant_id", "fluency_list_id"]).size()
    replayed = replays[replays <= REPLAY_THRESHOLD]
    print(f"  rounds replayed        {len(replayed):>6,} "
          f"(five or fewer responses, so the task showed the replay screen)")
    for (participant_id, list_id), size in replayed.items():
        print(f"    {participant_id}/{list_id}: {size} responses. That participant "
              f"contributes "
              f"{df[df['participant_id'] == participant_id]['fluency_list_id'].nunique()} "
              f"lists but was told about "
              f"{DESIGN_ROUNDS[df[df['participant_id'] == participant_id]['experiment_group'].iloc[0]]} "
              f"rounds, and the counter did not advance across the replay.")

    return prompts


if __name__ == "__main__":
    main()
