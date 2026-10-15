"""Generate participant-level LLM prompts for MECO L1 (Waves 1 and 2).

Reads processed_data/exp1.csv (Wave 1) and processed_data/exp2.csv (Wave 2)
and writes prompts.jsonl.zip, following the formatting of luke2018_provo and
berzak2025_onestop.

Each text the participant read becomes one trial, presented word by word with
the total reading time on that word marked in ``<< >>``. Words that never
received a fixation are marked ``<<not fixated>>``. Trials are headed by their
text number ("Text 5:") and listed in the order the participant read them:
by trial_order where the source records it (Wave 2), otherwise by text_id,
which Wave 1 documents as the position of the text in the session.

Interest areas with an empty label are not shown. They are the gaps between two
sentences where the source text had a double space (21 positions across all
texts), not words; their rows stay in the CSV files.

Comprehension questions are not included: the data record only whether each
answer was correct, the question wording is not distributed for Wave 2, and
answers exist for texts whose eye-tracking data were removed (see README.md).

Sessions are split into chunks of consecutive texts
---------------------------------------------------
A full session of up to 12 texts does not fit the 32K-token budget in every
language, and tokenisers differ most for non-Latin scripts. Each participant's
texts are therefore split into chunks of TEXTS_PER_CHUNK consecutive texts, in
reading order, with the text numbers recorded in the ``texts`` metadata field.
No trials are dropped. The chunk size was chosen by measuring the longest chunk
under three tokenisers (see README.md); the script re-checks every prompt
against the 100,000-character limit of scripts/validate_submission.py and, when
tiktoken is installed, against 32,000 tokens.
"""

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.resolve()
PROCESSED_DIR = BASE_DIR / "processed_data"
JSONL_PATH = BASE_DIR / "prompts.jsonl"
ZIP_PATH = BASE_DIR / "prompts.jsonl.zip"

EXPERIMENTS = [
    ("exp1.csv", "siegelman2022_meco/exp1"),
    ("exp2.csv", "siegelman2022_meco/exp2"),
]

TEXTS_PER_CHUNK = 6
CHAR_LIMIT = 100_000
TOKEN_LIMIT = 32_000

# Reconstructed from the procedure reported by Siegelman et al. (2022; 2025);
# the wording of the instruction screen is not published.
INSTRUCTION = (
    "You will read short encyclopedic texts in {language}, one at a time on a "
    "computer screen, while your eye movements are recorded. Each text appears "
    "on a single screen. Read each text silently for comprehension, at your own "
    "pace, and press the space bar when you have finished. After each text you "
    "will answer four yes/no questions about it. We will measure how long you "
    "look at each word.\n\n"
)
CHUNK_NOTE = ("Below are {texts} of the session, in the order they were read. "
              "The comprehension questions and answers are not included.\n\n")


def text_label(texts: list[int]) -> str:
    if len(texts) == 1:
        return f"text {texts[0]}"
    return "texts " + ", ".join(str(t) for t in texts)


def format_trial(text_id: int, words: pd.DataFrame) -> tuple[str, list[int]]:
    """Render one text as a trial block headed by its text number."""
    lines = [f"Text {text_id}:\n"]
    reading_times: list[int] = []
    for row in words.itertuples(index=False):
        if row.stimulus == "":
            continue
        if row.is_fixated == 1:
            reading_time = int(row.rt)
            lines.append(f"  Word {row.word_position}: '{row.stimulus}'  <<{reading_time}>> ms\n")
            reading_times.append(reading_time)
        else:
            lines.append(f"  Word {row.word_position}: '{row.stimulus}'  <<not fixated>>\n")
    lines.append("\n")
    return "".join(lines), reading_times


def load(filename: str) -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / filename, keep_default_na=False,
                     na_values={c: [""] for c in ("rt", "is_fixated")},
                     dtype={"stimulus": str, "participant_id": str})
    return df


def build_prompts(df: pd.DataFrame, experiment: str,
                  texts_per_chunk: int = TEXTS_PER_CHUNK) -> list[dict]:
    prompts = []
    # Keep the participant order of the CSV (sample, then participant number).
    for participant_id, rows in df.groupby("participant_id", sort=False):
        language = rows["first_language"].iloc[0]
        lab = rows["lab"].iloc[0]
        by_text = {t: g.sort_values("word_position") for t, g in rows.groupby("text_id")}
        # Reading order: the recorded trial counter where there is one.
        if "trial_order" in rows:
            position = rows.groupby("text_id")["trial_order"].first()
            texts = sorted(by_text, key=lambda t: position[t])
        else:
            texts = sorted(by_text)

        for start in range(0, len(texts), texts_per_chunk):
            chunk = [int(t) for t in texts[start:start + texts_per_chunk]]
            text = INSTRUCTION.format(language=language) + CHUNK_NOTE.format(texts=text_label(chunk))
            reading_times: list[int] = []
            for text_id in chunk:
                trial_text, trial_rts = format_trial(text_id, by_text[text_id])
                text += trial_text
                reading_times.extend(trial_rts)
            prompts.append({
                "text": text.rstrip("\n") + "\n",
                "experiment": experiment,
                "participant_id": participant_id,
                "first_language": language,
                "lab": lab,
                "texts": chunk,
                "rt": reading_times,
            })
    return prompts


def get_token_counter():
    try:
        import tiktoken
    except ImportError:
        return None, "not checked (tiktoken not installed)"
    encoder = tiktoken.get_encoding("cl100k_base")
    return (lambda s: len(encoder.encode(s))), "tiktoken cl100k_base"


def check(prompts: list[dict], n_rows: dict) -> None:
    count_tokens, method = get_token_counter()
    max_chars = max_tokens = 0
    for p in prompts:
        text = p["text"]
        n_markers = text.count("<<")
        assert n_markers == text.count(">>")
        assert "<" not in text.replace("<<", "") and ">" not in text.replace(">>", "")
        assert len(p["rt"]) == n_markers - text.count("<<not fixated>>")
        assert len(text) < CHAR_LIMIT, (p["participant_id"], p["texts"], len(text))
        max_chars = max(max_chars, len(text))
        if count_tokens:
            n = count_tokens(text)
            assert n < TOKEN_LIMIT, (p["participant_id"], p["texts"], n)
            max_tokens = max(max_tokens, n)
    for experiment, rows in n_rows.items():
        shown = sum(p["text"].count("  Word ") for p in prompts if p["experiment"] == experiment)
        print(f"  {experiment}: {rows['words']:,} word rows, {shown:,} shown "
              f"({rows['blank']} empty interest areas left out)")
        assert shown == rows["words"] - rows["blank"]
    print(f"  longest prompt: {max_chars:,} characters"
          + (f", {max_tokens:,} tokens ({method})" if count_tokens else f"; tokens {method}"))


def main() -> None:
    all_prompts, n_rows = [], {}
    for filename, experiment in EXPERIMENTS:
        df = load(filename)
        prompts = build_prompts(df, experiment)
        n_rows[experiment] = {"words": len(df), "blank": int((df["stimulus"] == "").sum())}
        print(f"  {experiment}: {len(prompts):,} lines from "
              f"{df['participant_id'].nunique()} participants")
        all_prompts.extend(prompts)

    check(all_prompts, n_rows)

    with open(JSONL_PATH, "w", encoding="utf-8", newline="\n") as f:
        for entry in all_prompts:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Fixed timestamp so that re-running the script gives a byte-identical archive.
    info = zipfile.ZipInfo("prompts.jsonl", date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    with zipfile.ZipFile(ZIP_PATH, "w") as zf:
        zf.writestr(info, JSONL_PATH.read_bytes())
    JSONL_PATH.unlink()

    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest()
    print(f"Wrote {ZIP_PATH.name}: {len(all_prompts):,} lines, sha256 {digest[:16]}")


if __name__ == "__main__":
    main()
