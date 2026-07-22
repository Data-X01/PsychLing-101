# martineztomas2026_discrete_emotionality

## Citation

Martínez-Tomás, C., Günther, F., Hinojosa, J. A., & Gatti, D. (2026). Conveying (discrete) emotionality with novel words. *Journal of Experimental Psychology: General*. Advance online publication. https://doi.org/10.1037/xge0001960

## Data source

- Open Science Framework: https://osf.io/9zbx6/
- DOI: https://doi.org/10.1037/xge0001960
- Supplied source archive: `original_data/pseudo_discreteR1_def.RData`

## Dataset contents

The study investigated whether Spanish speakers can encode and decode discrete emotional meaning through novel words across three experiments.

- Experiment 1: participants saw an emotional Spanish word and generated a novel word intended to convey the same meaning.
- Experiment 2: participants saw a novel Spanish letter string generated in Experiment 1 and typed the original Spanish word they believed it represented.
- Experiment 3: participants saw a novel Spanish letter string and selected its associated emotion from anger, disgust, fear, happiness, and sadness.

### Raw data

All trial-level files in `original_data` and `processed_data` are UTF-8 comma-delimited CSV files.

- `original_data/exp1.csv`: 2,210 rows exported from `dat_TP3`. It contains one target-comparison and one control-comparison row per behavioral trial.
- `original_data/exp2.csv`: 1,445 rows exported from `dat_b3`.
- `original_data/exp3.csv`: 1,567 rows exported from `dat_a`.
- `original_data/pseudo_discreteR1_def.RData`: the supplied archival source containing the three exported objects and additional analysis objects.

The raw CSV exports preserve the source rows, column names, and values. The archival `.RData` file is retained for provenance, but `preprocess_data.py` reads the CSV files directly.

### Processed data

- `processed_data/exp1.csv`: 1,105 trials from 54 participants.
- `processed_data/exp2.csv`: 1,445 trials from 61 participants.
- `processed_data/exp3.csv`: 1,567 trials from 66 participants.

The source tables already reflect the participant- and trial-level exclusions reported in the article. Catch trials used for participant screening are not included. Source identifiers containing filenames or timestamps are not exported to the processed data; participants receive experiment-prefixed sequential identifiers.

## Variable mapping

### Experiment 1

- `participant_id` <- `ID`, replaced with an experiment-prefixed sequential identifier
- `stimulus` <- `Palabra`
- `response` <- `response.text`
- `emotion` <- `emotion`
- `rt` <- (`generation.stopped` - `generation.started`) converted from seconds to milliseconds
- rows are restricted to `type == "target"` so each behavioral response appears once

### Experiment 2

- `participant_id` <- `ID`, replaced with an experiment-prefixed sequential identifier
- `stimulus` <- `Palabra`
- `target_word` <- `target_word`
- `response` <- `response.text`
- `emotion` <- `emotion`
- `rt` <- (`generation.stopped` - `generation.started`) converted from seconds to milliseconds

### Experiment 3

- `participant_id` <- `ID`, replaced with an experiment-prefixed sequential identifier
- `stimulus` <- `Palabra`
- `target_word` <- `target_word`
- `response` <- `emotion_selected`
- `response_correct` <- `emotion`
- `accuracy` <- `accuracy`
- `emotion` <- `emotion`
- `rt` <- `RTs` converted from seconds to milliseconds

### Common fields

- `trial_order` preserves source row order within participant and is 0-indexed
- `trial_id` combines the experiment number with `trial_order`
- `age` <- `edad`
- `gender` <- `género`, normalized to `female`, `male`, or `unspecified`
- `phase_id` identifies the task as `production`, `word_decoding`, or `emotion_decoding`
- `experiment` is a globally unique dataset/experiment identifier

## Reaction times

- Experiments 1 and 2: `rt` is computed as `generation.stopped - generation.started` and converted from seconds to milliseconds.
- Experiment 3: `RTs` is converted from seconds to milliseconds.

All reaction times in the processed files and prompt metadata are therefore expressed in milliseconds.

## Prompt generation

`generate_prompts.py` creates `prompts.jsonl.zip` with exactly one JSONL line per participant and experiment. Every record contains one `text`, `experiment`, and `participant_id` field. Participant-level age and gender appear once, and reaction times appear once as an `rt` list aligned with trial order.

The participant-facing text is in Spanish and begins with the original Spanish instructions reported in the supplemental material. Human responses are marked with `<< >>`.

Experiments 1 and 2 use typed free-text responses. Experiment 3 uses the five named emotion options selected with the mouse, so the two-key randomization used by binary-choice datasets does not apply here.

## Notes

- Raw files are never modified by preprocessing; standardized trial tables are written separately to `processed_data`.
- Every processed row has a unique `(participant_id, trial_id)` pair.
- Reaction times must be present and positive, and participant responses must be nonblank.
- Each JSONL line contains one participant from one experiment. Reaction times appear once in the top-level `rt` list and align with trial order.

## Files

- `original_data/exp1.csv`, `original_data/exp2.csv`, `original_data/exp3.csv`: raw trial-level CSV exports used by preprocessing.
- `original_data/pseudo_discreteR1_def.RData`: supplied archival source.
- `preprocess_data.py`: creates standardized trial-level CSV files from the raw CSV exports.
- `processed_data/exp1.csv`, `exp2.csv`, `exp3.csv`: standardized behavioral data.
- `CODEBOOK.csv`: variable definitions.
- `generate_prompts.py`: creates participant-level Spanish prompts.
- `prompts.jsonl.zip`: compressed JSONL prompt file.
