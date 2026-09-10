from collections import defaultdict
from pathlib import Path
import csv
import json
import zipfile


DATASET_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = DATASET_DIR / "processed_data"
JSONL_PATH = DATASET_DIR / "prompts.jsonl"
ZIP_PATH = DATASET_DIR / "prompts.jsonl.zip"

EXP1_INSTRUCTIONS = """Imagina una situación en la que quieres expresar un significado, pero no puedes hacerlo a través de la palabra original. En este experimento, tu tarea consiste en inventar una nueva palabra que exprese dicho significado. Después, en otro experimento, pediremos a algunas personas que adivinen las palabras originales basándose en las palabras que tú has inventado.

Consejos y sugerencias importantes:
Es importante que la nueva palabra no contenga la palabra original. La palabra inventada no puede ser una secuencia de letras al azar (e.j., chertsj), ni crearse mediante la transposición de letras de la palabra original (e.j., diadema - diameda).

Aquí tienes algunos ejemplos de cómo puedes crear nuevas palabras para sustituir la palabra original, pero puedes ser todo lo creativo que quieras:
Vaso - Arno / Mesa - Leca

Ten en cuenta que es muy importante que los demás puedan adivinar el significado de la palabra original. Por favor, intenta inventar una palabra que aluda al significado de cada palabra real que te mostremos de la forma más clara posible.

No hay respuestas correctas o incorrectas. Nos interesa lo que se te ocurra. Una vez hayas terminado de generar la nueva palabra, deberás pulsar el botón de continuar. Puedes tomarte el tiempo que necesites, teniendo en cuenta que no podrás modificar tu respuesta luego. Se te presentará un máximo de 25 palabras."""

EXP2_INSTRUCTIONS = """Gracias por tu participación. En este experimento, leerás cadenas de letras que son legibles en español, pero que no son palabras reales del idioma. Estas cadenas de letras fueron creadas en un experimento anterior, en el que se pidió a los participantes que, a partir de una palabra en español, generasen nuevas palabras con el fin de transmitir el mismo significado que la palabra original. Por ejemplo, un participante creó la palabra "crastion" basándose en la palabra original en español "choque".

Aquí, tu tarea es la opuesta: se te presentarán cadenas de letras generadas en español y tendrás que adivinar, una por una, las palabras originales en español de las que se derivaron. Siguiendo el ejemplo anterior, se te dará una nueva palabra como "crastion" y deberás adivinar la palabra "choque".

Para responder, deberás escribir tu respuesta utilizando el teclado. Una vez que hayas escrito la palabra original de la que crees que deriva la cadena de letras que se te presenta, deberás presionar el botón "continuar". Puedes tomarte el tiempo que necesites, teniendo en cuenta que no podrás modificar tu respuesta luego. Te vamos a presentar un máximo de 30 palabras nuevas. El estudio durará unos 15 minutos."""

EXP3_INSTRUCTIONS = """Gracias por tu participación. En este experimento, leerás cadenas de letras que son legibles en español, pero que no son palabras reales del idioma. Estas cadenas de letras fueron creadas en un experimento anterior, en el que se pidió a los participantes que generasen palabras nuevas a partir de palabras emocionales (por ejemplo, palabras relacionadas con el asco, la felicidad, la tristeza, el enfado y el miedo) con el fin de transmitir el mismo significado que la palabra original. Por ejemplo, un participante creó la palabra "crastion" basándose en la palabra emocional relacionada con el miedo "choque".

Aquí, tu tarea es la opuesta: se te presentarán secuencias de letras generadas en español y deberás adivinar, una por una, la emoción asociada a la palabra original de la que derivan. Siguiendo el ejemplo anterior, se te dará una nueva palabra como "crastion" y deberás adivinar que la emoción asociada a la palabra original es "miedo".

Para responder, deberás seleccionar con el ratón el nombre de la emoción que más se ajuste (entre: asco, enfado, felicidad, miedo y tristeza). Puedes tomarte el tiempo que necesites, teniendo en cuenta que no podrás modificar tu respuesta luego. Te vamos a presentar un máximo de 30 palabras nuevas. El estudio durará unos 15 minutos."""

SPANISH_EMOTIONS = {
    "anger": "enfado",
    "disgust": "asco",
    "fear": "miedo",
    "happiness": "felicidad",
    "sadness": "tristeza",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def json_number(value: str):
    if value == "":
        return None
    number = round(float(value), 3)
    return int(number) if number.is_integer() else number


def group_participants(rows: list[dict[str, str]]):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["participant_id"]].append(row)
    for participant_id in sorted(grouped):
        participant_rows = sorted(grouped[participant_id], key=lambda row: int(row["trial_order"]))
        yield participant_id, participant_rows


def build_exp1_text(rows: list[dict[str, str]]) -> str:
    lines = [EXP1_INSTRUCTIONS]
    for index, row in enumerate(rows, start=1):
        lines.append(
            f'Ensayo {index}: La palabra original es "{row["stimulus"]}". '
            f'Crea tu propia palabra nueva. Respondes <<{row["response"]}>>.'
        )
    return "\n".join(lines)


def build_exp2_text(rows: list[dict[str, str]]) -> str:
    lines = [EXP2_INSTRUCTIONS]
    for index, row in enumerate(rows, start=1):
        lines.append(
            f'Ensayo {index}: La cadena de letras es "{row["stimulus"]}". '
            f'Escribes <<{row["response"]}>>.'
        )
    return "\n".join(lines)


def build_exp3_text(rows: list[dict[str, str]]) -> str:
    lines = [EXP3_INSTRUCTIONS]
    for index, row in enumerate(rows, start=1):
        response = SPANISH_EMOTIONS[row["response"]]
        lines.append(
            f'Ensayo {index}: La cadena de letras es "{row["stimulus"]}". '
            f'Seleccionas <<{response}>>.'
        )
    return "\n".join(lines)


def build_records(filename: str, text_builder):
    rows = read_csv(PROCESSED_DIR / filename)
    for participant_id, participant_rows in group_participants(rows):
        first = participant_rows[0]
        yield {
            "text": text_builder(participant_rows),
            "experiment": first["experiment"],
            "participant_id": participant_id,
            "age": int(first["age"]),
            "gender": first["gender"],
            "rt": [json_number(row["rt"]) for row in participant_rows],
        }


def main():
    records = []
    records.extend(build_records("exp1.csv", build_exp1_text))
    records.extend(build_records("exp2.csv", build_exp2_text))
    records.extend(build_records("exp3.csv", build_exp3_text))

    with JSONL_PATH.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(JSONL_PATH, arcname="prompts.jsonl")

    print("Wrote:", JSONL_PATH)
    print("Wrote:", ZIP_PATH)
    print("Participant records:", len(records))


if __name__ == "__main__":
    main()
