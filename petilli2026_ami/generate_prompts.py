import csv
import json
import zipfile
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "processed_data" / "exp1.csv"
README = ROOT / "README.md"
JSONL = ROOT / "prompts.jsonl"
ZIP = ROOT / "prompts.jsonl.zip"

EXPERIMENT = "petilli2026_ami/exp1"
MAX_CHARS = 100_000

REQUIRED = {
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
}

VALID_VAD = set("123456789")
VALID_UNKNOWN = {"0", "1"}
MISSING = {"", "nan", "na", "n/a"}


def clean(value):
    if value is None:
        return ""

    return value.strip()


def is_missing(value):
    return clean(value).lower() in MISSING


def read_instructions():
    text = README.read_text(
        encoding="utf-8"
    )

    start_heading = "## Original instructions"
    end_heading = "## Raw data"

    if (
        start_heading not in text
        or end_heading not in text
    ):
        raise ValueError(
            "README.md must contain the sections "
            "'## Original instructions' and '## Raw data'."
        )

    return (
        text
        .split(start_heading, 1)[1]
        .split(end_heading, 1)[0]
        .strip()
    )


def build_prompt(rows, instructions):
    interface_description = """
Per ciascuna parola era mostrata la domanda:
"Cosa provi quando leggi la parola [PAROLA]?"

Le risposte erano fornite simultaneamente sulle scale
di valenza, arousal e dominanza.

Era inoltre presente l'opzione:
"Clicca qui se non conosci il significato di questa parola".

I record seguenti sono riportati nell'ordine tecnico
disponibile nel file sorgente. Questo ordine non deve
essere interpretato come l'ordine temporale originale
di presentazione.
"""

    records = []

    for index, row in enumerate(
        rows,
        start=1,
    ):
        records.append(
            f'Record {index}: parola "{row["stimulus"]}". '
            f'Valenza <<{row["valence"]}>>; '
            f'arousal <<{row["arousal"]}>>; '
            f'dominanza <<{row["dominance"]}>>; '
            f'parola non conosciuta '
            f'<<{row["unknown_word"]}>>.'
        )

    return (
        instructions
        + "\n\n"
        + interface_description.strip()
        + "\n\n"
        + "\n".join(records)
    )


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Processed input file not found: {INPUT}"
        )

    if not README.exists():
        raise FileNotFoundError(
            f"README file not found: {README}"
        )

    instructions = read_instructions()

    sessions = OrderedDict()
    trial_ids = set()

    with INPUT.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as input_file:
        reader = csv.DictReader(
            input_file
        )

        missing_columns = (
            REQUIRED
            - set(reader.fieldnames or [])
        )

        if missing_columns:
            raise ValueError(
                "Missing columns: "
                f"{sorted(missing_columns)}"
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            row = {
                key: clean(value)
                for key, value in row.items()
            }

            trial_id = row["trial_id"]
            session_id = row["session_id"]

            if not trial_id:
                raise ValueError(
                    f"Missing trial_id at CSV line "
                    f"{line_number}"
                )

            if trial_id in trial_ids:
                raise ValueError(
                    f"Duplicate trial_id: {trial_id}"
                )

            trial_ids.add(
                trial_id
            )

            if not session_id:
                raise ValueError(
                    f"Missing session_id at CSV line "
                    f"{line_number}"
                )

            if not row["participant_id"]:
                raise ValueError(
                    f"Missing participant_id at CSV line "
                    f"{line_number}"
                )

            for field in (
                "valence",
                "arousal",
                "dominance",
            ):
                if row[field] not in VALID_VAD:
                    raise ValueError(
                        f"Invalid {field} value at CSV "
                        f"line {line_number}: "
                        f"{row[field]!r}"
                    )

            if (
                row["unknown_word"]
                not in VALID_UNKNOWN
            ):
                raise ValueError(
                    f"Invalid unknown_word value at CSV "
                    f"line {line_number}: "
                    f"{row['unknown_word']!r}"
                )

            sessions.setdefault(
                session_id,
                [],
            ).append(
                row
            )

    lengths = []
    participants = set()

    with JSONL.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as output_file:
        for session_id, rows in sessions.items():
            participant_ids = {
                row["participant_id"]
                for row in rows
            }

            if len(participant_ids) != 1:
                raise ValueError(
                    f"Inconsistent participant_id "
                    f"in session {session_id}"
                )

            participant_id = next(
                iter(participant_ids)
            )

            prompt = build_prompt(
                rows,
                instructions,
            )

            if len(prompt) > MAX_CHARS:
                raise ValueError(
                    f"Prompt too long in session "
                    f"{session_id}: "
                    f"{len(prompt)} characters"
                )

            record = {
                "text": prompt,
                "experiment": EXPERIMENT,
                "participant_id": participant_id,
                "session_id": session_id,
                "part_of_speech": [
                    row["part_of_speech"]
                    for row in rows
                ],
            }

            gender = rows[0]["gender"]
            age = rows[0]["age"]

            if not is_missing(gender):
                record["gender"] = gender

            if not is_missing(age):
                record["age"] = age

            output_file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

            lengths.append(
                len(prompt)
            )

            participants.add(
                participant_id
            )

    with zipfile.ZipFile(
        ZIP,
        "w",
        zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        archive.write(
            JSONL,
            arcname="prompts.jsonl",
        )

    JSONL.unlink()

    print("=== PROMPT GENERATION COMPLETED ===")
    print(
        f"Session-level prompts: "
        f"{len(sessions)}"
    )
    print(
        f"Distinct participants: "
        f"{len(participants)}"
    )
    print(
        f"Trial records included: "
        f"{len(trial_ids)}"
    )
    print(
        f"Shortest prompt: "
        f"{min(lengths)} characters"
    )
    print(
        f"Longest prompt: "
        f"{max(lengths)} characters"
    )
    print(
        f"Output: {ZIP}"
    )
    print(
        "Validation passed."
    )


if __name__ == "__main__":
    main()