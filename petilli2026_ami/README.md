# Italian Affective Norms

## Overview

This folder contains trial-level data from the **Affective Measures for Italian (AMI)** project.

Participants rated approximately 250 Italian words. For each presented word, participants reported how they felt when reading it using three 1–9 scales displayed simultaneously on the same screen:

1. **Valence**: from negative to positive feelings.
2. **Arousal**: from calm or low activation to high activation.
3. **Dominance**: from powerlessness or a low sense of control to a high sense of control.

On the same screen, participants could also select a checkbox indicating that they did not know the meaning of the word.

The dataset includes nouns, adjectives, and verbs.

## Contributors

* Marco A. Petilli
* Alessandra Vergallito
* Marco Marelli
* Simona Amenta

## Citation

Petilli, M. A., Vergallito, A., Marelli, M., & Amenta, S. (2026). *Affective measures for Italian (AMI): Valence, arousal and dominance norms for 13,495 Italian nouns, adjective and verbs* [Preprint]. PsyArXiv. https://doi.org/10.31234/osf.io/frbk2_v1

## Data source

The original dataset is publicly available on OSF: https://osf.io/afe26/

## Experimental procedure

For each word, participants saw the following question:

> Cosa provi quando leggi la parola [PAROLA]?

The following three scales were displayed simultaneously:

* **Valence**: `sensazioni negative 1 2 3 4 5 6 7 8 9 sensazioni positive`
* **Arousal**: `calma, bassa attivazione 1 2 3 4 5 6 7 8 9 alta attivazione`
* **Dominance**: `impotenza, basso senso di controllo 1 2 3 4 5 6 7 8 9 alto senso di controllo`

At the bottom of the same screen, participants saw the following checkbox:

> Clicca qui se non conosci il significato di questa parola

## Original instructions

Ti invitiamo a prendere parte ad uno studio che indaga le emozioni ed il modo in cui le persone rispondono ai diversi tipi di parole. Ti saranno presentate circa 250 parole. Ti chiediamo di valutare per ogni singola parola il modo in cui ti senti quando la leggi, utilizzando tre diverse scale che hanno dei punteggi che vanno da 1 a 9 punti.

La prima scala, valenza, si riferisce a quanto una parola ti faccia provare sensazioni negative vs. positive. Ad un estremo di questa scala, ti senti infelice, infastidito, insoddisfatto, malinconico, disperato o annoiato. Quando provi esclusivamente sensazioni negative seleziona il punteggio 1. L’altro estremo di questa scala è quando ti senti felice, soddisfatto, contento, pieno di speranza. Puoi indicare provare esclusivamente sensazioni positive selezionando il punteggio 9. Se ti senti completamente neutrale, e non provi sensazioni negative né positive, seleziona il centro della scala (5). Come puoi vedere, i numeri consentono anche di descrivere sensazioni intermedie.

La seconda scala, che rappresenta lo stato di arousal o attivazione, si riferisce a quanto una parola ti faccia sentire calmo vs. attivato. Ad un estremo di questa scala, ti senti rilassato, calmo, tranquillo, pacifico, o non eccitato. Quando ti senti completamente calmo seleziona il punteggio 1. L’altro estremo di questa scala è quando ti senti stimolato, eccitato, frenetico, nervoso, completamente sveglio o attivato. Puoi indicare di sentirti completamente attivato selezionando 9. Se ti senti mediamente attivato, seleziona il centro della scala (5). Come puoi vedere, i numeri consentono anche di descrivere esperienze di attivazione intermedie.

La terza scala, che rappresenta il livello di dominanza, si riferisce a quanto una parola ti faccia sentire impotente vs. in controllo. Ad un estremo di questa scala, ti senti sottomesso, in balia degli eventi, non in controllo della situazione, influenzato. Quando ti senti completamente impotente seleziona il punteggio 1. L’altro estremo di questa scala è quando ti senti sicuro, influente, potente, dominante, autonomo, capace, totalmente capace di gestire la situazione. Puoi indicare di sentirti completamente in controllo selezionando 9. Se ti senti mediamente in controllo, seleziona il centro della scala (5). Come puoi vedere, i numeri consentono anche di descrivere esperienze di dominanza intermedie.

Per favore, procedi speditamente nella compilazione e non perdere troppo tempo a riflettere su ogni parola. Piuttosto, esprimi le tue valutazioni sulla base di una tua prima reazione istintiva quando leggi ogni parola.

Non ci sono risposte giuste o sbagliate, valuta ogni parola seguendo il tuo giudizio.

Nel corso dell’esperimento ci saranno degli item di controllo attentivo per valutare che le risposte non siano date in modo casuale. Nel caso riscontrassimo una percentuale troppo alta di risposte casuali non saranno erogati CFU.

## Raw data

The original wide-format file is stored in:

`original_data/DATA_AllRatings_raw.csv`

The relevant source metadata fields are:

* `RatingScale`: type of scale or unknown-word checkbox (`Val`, `Aro`, `Dom`, or `Unk`);
* `POS`: part of speech (`Adj`, `Nou`, or `Ver`);
* `List`: experimental list version presented to the participant;
* `ResponseIdQualtrics`: unique Qualtrics response ID identifying the participant's survey session;
* `IDsubj`: anonymous ID assigned to each participant;
* `gender`: participant's self-reported gender;
* `age`: participant's self-reported age.

The remaining columns correspond to individual words.

A `NaN` value indicates that no response was recorded for that item in the corresponding source row. Items without any valence, arousal, or dominance rating are not included in the processed trial-level dataset.

## Preprocessing

The script:

`preprocess_data.py`

converts the original wide-format file into:

`processed_data/exp1.csv`

The script combines the four source rows corresponding to `Val`, `Aro`, `Dom`, and `Unk`. Each retained row in `exp1.csv` represents a single word-presentation trial and contains the three affective ratings and the unknown-word checkbox value recorded on the same screen.

The preprocessing script:

* retains only trials with recorded valence, arousal, and dominance ratings;
* excludes rows containing only an unknown-word checkbox value and no affective rating;
* preserves affective ratings associated with words marked as unknown;
* retains only the participant-level metadata relevant to the shared dataset;
* does not reconstruct the temporal presentation order because it is not available from the raw file;
* creates a synthetic `trial_id` that uniquely identifies each retained trial and allows the corresponding raw-file location to be recovered.

## Processed data structure

| Column           | Description                                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| `participant_id` | Anonymous participant ID.                                                                                           |
| `session_id`     | Unique Qualtrics response ID identifying the participant's survey session.                                          |
| `gender`         | Participant's self-reported gender.                                                                                 |
| `age`            | Participant's self-reported age in years.                                                                           |
| `part_of_speech` | Part of speech: `Adj`, `Nou`, or `Ver`.                                                                             |
| `list_id`        | Experimental list version presented to the participant.                                                             |
| `trial_id`       | Synthetic unique identifier for a retained word-presentation trial. It does not encode temporal presentation order. |
| `stimulus`       | Italian word presented to the participant.                                                                          |
| `valence`        | Valence rating from 1 to 9.                                                                                         |
| `arousal`        | Arousal rating from 1 to 9.                                                                                         |
| `dominance`      | Dominance rating from 1 to 9.                                                                                       |
| `unknown_word`   | Checkbox indicator: `0` = not selected; `1` = selected.                                                             |

## Preprocessing summary

The processed dataset contains:

* 224,265 retained word-presentation trials;
* 94,310 adjective trials;
* 92,971 noun trials;
* 36,984 verb trials;
* 2,421 retained trials in which the unknown-word checkbox was selected.

All retained trials contain valid valence, arousal, and dominance ratings. All observed affective ratings are integers from 1 to 9. All observed unknown-word checkbox values are coded as `0` or `1`.

## Notes

The temporal presentation order of the stimuli cannot be reconstructed from the original file. For this reason, the processed dataset intentionally omits a `trial_order` column.

Ratings associated with words marked as unknown are preserved in the processed dataset. Researchers may determine whether to exclude these ratings depending on their analytical goals.
EOF

## LLM prompts

The script:

`generate_prompts.py`

reads the trial-level file:

`processed_data/exp1.csv`

and generates:

`prompts.jsonl.zip`

The ZIP archive contains a single JSONL file named `prompts.jsonl`.

Each JSONL line represents one Qualtrics session and includes:

- `text`: original task instructions followed by the session-level trial records;
- `experiment`: experiment identifier;
- `participant_id`: anonymous participant ID;
- `session_id`: unique Qualtrics response ID;
- `gender`: participant's self-reported gender, when available;
- `age`: participant's self-reported age, when available.

Each retained word-presentation record includes the stimulus and the four responses collected on the same screen:

- valence;
- arousal;
- dominance;
- unknown-word checkbox.

Human responses are enclosed in `<< >>`.

Some anonymous participants completed more than one Qualtrics session. For this reason, the JSONL file contains one prompt per session rather than one prompt per unique participant. The temporal presentation order cannot be reconstructed from the original data. Records are therefore presented in the technical order available in the source file, which must not be interpreted as the original temporal order.
