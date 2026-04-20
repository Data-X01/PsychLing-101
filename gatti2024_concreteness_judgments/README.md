# gatti2024_concreteness_judgments

## Citation
Gatti, D., Rinaldi, L., Marelli, M., Mazzoni, G., & Vecchi, T. (2024). Predicting hand movements with distributional semantics. *Cognitive Science*. https://doi.org/10.1111/cogs.13399

## Data source
Original data files:
- `original_data/data_EXP1_fin.csv`
- `original_data/data_EXP2_full.csv`

Source link: https://onlinelibrary.wiley.com/doi/full/10.1111/cogs.13399

## Dataset contents
This folder contains two concreteness-judgment datasets derived from the source files.

### Raw data
- `original_data/data_EXP1_fin.csv`
- `original_data/data_EXP2_full.csv`

### Processed data
- `processed_data/exp1.csv`: Experiment 1 trial-level judgment data
- `processed_data/exp2.csv`: Experiment 2 trial-level judgment data

## Variable mapping used in `exp1.csv`
- `participant_id` <- `ID`
- `stimulus_left` <- `text`
- `stimulus_right` <- `text2`
- `response` <- `resp`
- `response_side` = whether `response` matches `stimulus_left` or `stimulus_right`
- `condition_raw` <- `condition`
- `rt` <- `RTs` normalized to numeric
- `age` <- `age`
- `gender` <- `gender` normalized to `F`/`M` where possible
- `hand` <- `hand` normalized to `right` where possible
- `phase_id` = `judgment`
- `experiment` = `EXP1`

## Variable mapping used in `exp2.csv`
- `participant_id` <- `ID`
- `stimulus_left` <- `text`
- `stimulus_right` <- `text2`
- `response` <- `resp`
- `response_side` = whether `response` matches `stimulus_left` or `stimulus_right`
- `condition_raw` <- `condition`
- `device` <- `type` normalized to `mouse`/`trackpad` where possible
- `age` <- `age`
- `gender` <- `gender` normalized to `F`/`M` where possible
- `phase_id` = `judgment`
- `experiment` = `EXP2`

## Notes
- The task is a two-alternative forced-choice lexical judgment task.
- The prompt text should reflect the participant experience by presenting the two words shown on each trial and the chosen response.
- Metadata can store side, RT, device, age, gender, handedness, and original condition labels.
