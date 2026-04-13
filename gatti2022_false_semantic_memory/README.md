# gatti2022_false_semantic_memory

## Citation
Gatti, D., Rinaldi, L., Marelli, M., Mazzoni, G., & Vecchi, T. (2022). Decomposing the semantic processes underpinning veridical and false memories. *Journal of Experimental Psychology: General, 151*(2), 363.

## Data source
Original data file: `original_data/database_DRM.xlsx`

Source link: https://psycnet.apa.org/record/2022-15802-001

## Dataset contents
This folder contains the first processed dataset for the false semantic memory study.

### Raw data
- `original_data/database_DRM.xlsx`

### Processed data
- `processed_data/exp1.csv`: study + recognition trial-level data reconstructed from worksheets `EXP.1.1` and `EXP.1.2`

## Variable mapping used in `exp1.csv`
- `participant_id` <- `Subject`
- `stimulus` <- study-phase `Word` or recognition-phase `word`
- `response` <- `Response` (`1 = old`, `0 = new`); missing during study phase
- `condition` <- recognition `Type2`
  - `false_recog` = false recognition target
  - `veridical_recog` = true recognition target
- `accuracy` = whether `response` matches the condition-specific correct answer; missing during study phase
- `trial_order` = within-participant order, 0-indexed across the full session
- `trial_id` = phase-specific trial identifier
- `phase_id` = `study` or `recognition`
- `list_name` = critical-lure label identifying the DRM list
- `list` = dataset-specific numeric surrogate for `list_name`
- `experiment` = `EXP.1`

## Notes
- Metadata and variable names are documented in English, as required by the project.
- Prompts include the study phase followed by the recognition phase, so each participant record represents the full session.
- This version preserves the true-vs-false recognition distinction as the main recognition condition.
