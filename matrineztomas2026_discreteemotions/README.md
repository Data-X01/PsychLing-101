# martineztomas2026_discrete_emotionality

## Citation

Martínez-Tomás, C., Günther, F., Hinojosa, J. A., & Gatti, D. (2026). Conveying (discrete) emotionality with novel words. *Journal of Experimental Psychology: General*. Advance online publication. https://doi.org/10.1037/xge0001960

## Data source

- Open Science Framework: https://osf.io/9zbx6/
- DOI: https://doi.org/10.1037/xge0001960
- Source data supplied for this contribution: `original_data/pseudo_discreteR1_def.RData`

## Study overview

The study investigated whether Spanish speakers can encode and decode discrete emotional meaning through novel words across three experiments.

- Experiment 1 (`exp1.csv`): participants saw an emotional Spanish word and generated a novel word intended to convey the same meaning.
- Experiment 2 (`exp2.csv`): participants saw a novel Spanish letter string generated in Experiment 1 and typed the original Spanish word they believed it represented.
- Experiment 3 (`exp3.csv`): participants saw a novel Spanish letter string and selected the emotion associated with its source word from anger, disgust, fear, happiness, and sadness.

## Original data

The supplied RData file contains the final cleaned analysis objects used for the article. The public trial-level tables are reconstructed from:

- `dat_TP3` for Experiment 1. This object contains one target-comparison row and one control-comparison row per behavioral trial; `preprocess_data.R` retains the target row so that every behavioral response appears exactly once.
- `dat_b3` for Experiment 2.
- `dat_a` for Experiment 3.

Identifiers containing source filenames and timestamps are not exported. Participants are assigned experiment-prefixed sequential identifiers.

## Processed data

- `processed_data/exp1.csv`: 1,105 trials from 54 participants.
- `processed_data/exp2.csv`: 1,445 trials from 61 participants.
- `processed_data/exp3.csv`: 1,567 trials from 66 participants.

The RData objects already reflect the participant- and trial-level exclusions reported in the article. Catch trials used for participant screening are not included in the final behavioral tables.

## Reaction times

- Experiments 1 and 2: `rt` is computed as `generation.stopped - generation.started` and converted from seconds to milliseconds.
- Experiment 3: `RTs` is converted from seconds to milliseconds.

All reaction times in the processed files and prompt metadata are therefore expressed in milliseconds.

## Prompt generation

`generate_prompts.py` creates `prompts.jsonl.zip` with exactly one JSONL line per participant and experiment. Every record contains one `text`, `experiment`, and `participant_id` field. Participant-level age and gender appear once, and reaction times appear once as an `rt` list aligned with trial order.

The participant-facing text is in Spanish and begins with the original Spanish instructions reported in the supplemental material. Human responses are marked with `<< >>`.

## Files

- `original_data/pseudo_discreteR1_def.RData`: supplied cleaned source/analysis data.
- `preprocess_data.R`: reconstructs standardized trial-level CSV files.
- `processed_data/exp1.csv`, `exp2.csv`, `exp3.csv`: standardized behavioral data.
- `CODEBOOK.csv`: variable definitions.
- `generate_prompts.py`: creates participant-level Spanish prompts.
- `prompts.jsonl.zip`: compressed JSONL prompt file.
