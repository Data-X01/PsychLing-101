from __future__ import annotations

import csv
import hashlib
import json
import random
import string
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "processed_data"

RATINGS_INPUT = PROCESSED_DIR / "exp1.csv"
LEXICAL_DECISION_INPUT = PROCESSED_DIR / "exp2.csv"
NAMING_INPUT = PROCESSED_DIR / "exp3.csv"

JSONL_OUTPUT = BASE_DIR / "prompts.jsonl"
ZIP_OUTPUT = BASE_DIR / "prompts.jsonl.zip"

# PsychLing-101 requires prompts to remain below 32K tokens.
# This conservative character limit avoids an additional tokenizer dependency.
MAX_PROMPT_CHARACTERS = 100_000

# The released raw files do not preserve the original randomized presentation
# order. The prompts therefore follow released-file row order. This must not be
# interpreted as the actual order seen by participants.
ORDER_NOTE = (
    "Nota per la rappresentazione dei dati: l'ordine randomizzato originale "
    "di presentazione non è disponibile. La sequenza seguente rispetta "
    "l'ordine delle righe del file rilasciato e non deve essere interpretata "
    "come l'ordine effettivo di presentazione.\n\n"
)

# These are the original participant-facing instructions supplied by the
# authors. In Experiment 1, the placeholder originally written as <<>> has been
# replaced with [PAROLA], because PsychLing-101 reserves << >> exclusively for
# human responses and continuous behavioural outcomes.
EXP1_INSTRUCTIONS = """Buongiorno e grazie per la tua partecipazione a questo studio.
Di seguito ti chiederemo di valutare in che misura puoi avere esperienza di una serie di parole attraverso ognuno dei 5 sensi (vista, tatto, gusto, olfatto, udito). Puoi valutare ogni parola utilizzando una scala che va da 0 (Per niente) a 5 (estremamente).
Sotto è riportato un esempio.
Una volta che avrai valutato tutte e cinque le modalità sensoriali per ogni parola, puoi passare alla successiva premendo la freccia in basso a destra.
Ti ricordiamo che non ci sono risposte giuste o sbagliate, valuta ogni parola seguendo il tuo giudizio. Se non conosci il significato di una parola, passa direttamente alla successiva.
Puoi mettere in pausa l’esperimento ogni volta che vuoi, potrai riprendere da dove l’hai interrotto semplicemente riaprendo il link che ti abbiamo inviato.
Nel corso dell’esperimento ci saranno degli item di controllo per valutare che il compito sia svolto correttamente. Nel caso di risposte casuali o troppe risposte mancanti verrà assegnato il numero minimo di crediti (0.1).
Ti ricordiamo che dovrai concludere l’esperimento entro due settimane dalla ricezione della mail contenente i due link. In caso il questionario non sia completato entro i termini stabiliti non verranno erogati cfu.
Nota bene: l'esperimento dovrà essere eseguito sempre sullo stesso dispositivo e utilizzando sempre lo stesso browser (ad esempio internet explorer, mozzilla firefox...).
Ti ricordiamo che il link è strettamente personale.
In che misura puoi avere esperienza di [PAROLA] attraverso: l'udito, il gusto, il tatto, l'olfatto, la vista
0 per niente 1 2 3 4 5 estremamente

"""

def lexical_decision_instructions(
    word_key: str,
    pseudoword_key: str,
) -> str:
    return (
        "Buongiorno e grazie per la tua partecipazione a questo studio.\n"
        "In questo compito ti verrà chiesto di scegliere il più velocemente "
        "possibile se la stringa di lettere che ti verrà presentata è una "
        "parola oppure no.\n"
        f"Premi il tasto {word_key} per le parole, il tasto "
        f"{pseudoword_key} per le non parole.\n"
        "Ti chiediamo di essere il più accurato e veloce possibile.\n\n"
    )


EXP3_INSTRUCTIONS = """Buongiorno e grazie per la tua partecipazione a questo studio.
In questo compito ti verrà chiesto di leggere il più velocemente possibile la parola presentata sullo schermo.
Ti chiediamo di essere il più accurato e veloce possibile.

"""


def clean_text(value: str | None) -> str:
    return "" if value is None else value.strip()


def marked(value: str | None) -> str:
    value = clean_text(value)
    return f"<<{value if value != '' else 'missing'}>>"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Processed file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def first_nonempty(rows: list[dict[str, str]], column: str) -> str:
    for row in rows:
        value = clean_text(row.get(column))
        if value != "":
            return value
    return ""


def add_optional_metadata(
    record: dict[str, Any],
    rows: list[dict[str, str]],
    columns: list[str],
) -> None:
    for column in columns:
        value = first_nonempty(rows, column)
        if value != "":
            record[column] = value


def validate_prompt(record: dict[str, Any]) -> None:
    prompt = record["text"]
    if len(prompt) > MAX_PROMPT_CHARACTERS:
        raise ValueError(
            "Prompt exceeds the conservative character limit: "
            f"experiment={record['experiment']}, "
            f"participant_id={record['participant_id']}, "
            f"characters={len(prompt)}, "
            f"limit={MAX_PROMPT_CHARACTERS}"
        )


def generate_perceptual_rating_prompts() -> list[dict[str, Any]]:
    rows = read_csv(RATINGS_INPUT)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        grouped[row["participant_id"]].append(row)

    records: list[dict[str, Any]] = []

    for participant_id, participant_rows in grouped.items():
        lines = [EXP1_INSTRUCTIONS, ORDER_NOTE]

        lines.append(
            "Formato dei dati trial-by-trial: PAROLA: "
            "<<udito>>, <<gusto>>, <<tatto>>, <<olfatto>>, <<vista>>.\n"
        )

        for row in participant_rows:
            lines.append(
                f"{row['stimulus']}: "
                f"{marked(row['auditory_rating'])},"
                f"{marked(row['gustatory_rating'])},"
                f"{marked(row['haptic_rating'])},"
                f"{marked(row['olfactory_rating'])},"
                f"{marked(row['visual_rating'])}.\n"
            )

        record: dict[str, Any] = {
            "text": "".join(lines),
            "experiment": "vergallito2020_ipsn/exp1_perceptual_ratings",
            "participant_id": participant_id,
        }
        add_optional_metadata(record, participant_rows, ["age", "gender"])
        validate_prompt(record)
        records.append(record)

    return records


def participant_choice_options(
    participant_id: str,
) -> tuple[str, str]:
    """Assign a reproducible randomized key pair to one participant.

    The first key corresponds to WORD and the second to PSEUDOWORD.
    Because the seed depends only on participant_id, the same participant
    receives the same pair in both sessions and across repeated script runs.
    """
    seed_text = f"vergallito2020_ipsn:{participant_id}"
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    seed = int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    )

    rng = random.Random(seed)
    word_key, pseudoword_key = rng.sample(
        list(string.ascii_uppercase),
        2,
    )

    return word_key, pseudoword_key


def infer_lexical_decision_key(
    stimulus_type: str,
    accuracy: str,
    word_key: str,
    pseudoword_key: str,
) -> str:
    stimulus_type = clean_text(stimulus_type).lower()
    accuracy = clean_text(accuracy)

    if stimulus_type == "word":
        correct_key = word_key
        incorrect_key = pseudoword_key
    elif stimulus_type == "pseudoword":
        correct_key = pseudoword_key
        incorrect_key = word_key
    else:
        raise ValueError(f"Unexpected stimulus type: {stimulus_type}")

    if accuracy == "1":
        return correct_key
    if accuracy == "0":
        return incorrect_key
    if accuracy == "":
        return "missing"

    raise ValueError(f"Unexpected accuracy value: {accuracy}")


def generate_lexical_decision_prompts() -> list[dict[str, Any]]:
    rows = read_csv(LEXICAL_DECISION_INPUT)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        grouped[(row["participant_id"], row["session_id"])].append(row)

    records: list[dict[str, Any]] = []

    for (participant_id, session_id), session_rows in grouped.items():
        word_key, pseudoword_key = participant_choice_options(
            participant_id
        )

        lines = [
            lexical_decision_instructions(
                word_key,
                pseudoword_key,
            ),
            ORDER_NOTE,
        ]

        for row in session_rows:
            response_key = infer_lexical_decision_key(
                row["stimulus_type"],
                row["accuracy"],
                word_key,
                pseudoword_key,
            )
            lines.append(
                f"{row['stimulus']}. Premi {marked(response_key)}. "
                f"RT {marked(row['rt'])} ms.\n"
            )

        record: dict[str, Any] = {
            "text": "".join(lines),
            "experiment": "vergallito2020_ipsn/exp2_lexical_decision",
            "participant_id": participant_id,
            "session_id": session_id,
            "rt": [row["rt"] for row in session_rows],
            "accuracy": [row["accuracy"] for row in session_rows],
            "word_key": word_key,
            "pseudoword_key": pseudoword_key,
        }
        add_optional_metadata(
            record,
            session_rows,
            ["age", "gender", "education", "handedness"],
        )
        validate_prompt(record)
        records.append(record)

    return records


def generate_naming_prompts() -> list[dict[str, Any]]:
    rows = read_csv(NAMING_INPUT)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        grouped[(row["participant_id"], row["session_id"])].append(row)

    records: list[dict[str, Any]] = []

    for (participant_id, session_id), session_rows in grouped.items():
        lines = [EXP3_INSTRUCTIONS, ORDER_NOTE]

        for row in session_rows:
            lines.append(
                f"{row['stimulus']}. "
                f"Latenza di onset vocale {marked(row['rt'])} ms.\n"
            )

        record: dict[str, Any] = {
            "text": "".join(lines),
            "experiment": "vergallito2020_ipsn/exp3_naming",
            "participant_id": participant_id,
            "session_id": session_id,
            "rt": [row["rt"] for row in session_rows],
            "accuracy": [row["accuracy"] for row in session_rows],
        }
        add_optional_metadata(
            record,
            session_rows,
            ["age", "gender", "education", "handedness"],
        )
        validate_prompt(record)
        records.append(record)

    return records


def write_jsonl(records: list[dict[str, Any]]) -> None:
    with JSONL_OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_zip() -> None:
    with zipfile.ZipFile(
        ZIP_OUTPUT, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        archive.write(JSONL_OUTPUT, arcname="prompts.jsonl")


def main() -> None:
    records = (
        generate_perceptual_rating_prompts()
        + generate_lexical_decision_prompts()
        + generate_naming_prompts()
    )

    write_jsonl(records)
    write_zip()

    prompt_lengths = [len(record["text"]) for record in records]
    exp1_count = sum(
        record["experiment"].endswith("exp1_perceptual_ratings")
        for record in records
    )
    exp2_count = sum(
        record["experiment"].endswith("exp2_lexical_decision")
        for record in records
    )
    exp3_count = sum(
        record["experiment"].endswith("exp3_naming")
        for record in records
    )

    print("Prompt generation completed successfully.")
    print(f"JSONL file: {JSONL_OUTPUT}")
    print(f"ZIP file:   {ZIP_OUTPUT}")
    print(f"Total prompt records: {len(records)}")
    print(f"  Experiment 1 prompts: {exp1_count}")
    print(f"  Experiment 2 prompts: {exp2_count}")
    print(f"  Experiment 3 prompts: {exp3_count}")
    print(f"Longest prompt: {max(prompt_lengths)} characters")
    print(f"Conservative limit: {MAX_PROMPT_CHARACTERS} characters")
    print(
        "Note: prompts follow released-file row order, "
        "not the original randomized order."
    )


if __name__ == "__main__":
    main()
