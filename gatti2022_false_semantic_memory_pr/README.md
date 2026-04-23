# gatti2022_false_semantic_memory_pr

## Citation
Gatti, D., Marelli, M., Mazzoni, G., Vecchi, T., & Rinaldi, L. (2023). Hands-on false memories: a combined study with distributional semantics and mouse-tracking. *Psychological Research, 87*, 1129–1142.

## Data source
Original data files:
- `original_data/data_DRM.xls`
- `original_data/liste.xls`

Source link: https://doi.org/10.1007/s00426-022-01710-x

## Dataset contents
This folder contains the cleaned recognition dataset for the false semantic memory study.

### Raw data
- `original_data/data_DRM.xls`: participant-level cleaned recognition data
- `original_data/liste.xls`: list materials

### Processed data
- `processed_data/exp1.csv`: recognition-trial data derived from `data_DRM.xls`

## Variable mapping used in `exp1.csv`
- `participant_id` <- `ID`
- `stimulus` <- `word`
- `response` <- `resp_resp`
- `trial_order` <- `ord - 1`
- `probe_type` <- `type`
- `condition` <- `type.2`
  - `studied` = old/studied target
  - `new` = new item
- `accuracy` = whether `response` matches the binary condition-specific correct answer
- `rt` <- `RT`
- `age` <- `age`
- `gender` <- `gender` normalized to uppercase
- `phase_id` = `recognition`
- `experiment` = `data_DRM`

## Notes
- This processed file preserves cleaned recognition data only.
- Trial-order gaps may remain because missing/unanswered trials were already absent from the cleaned source dataset.
- The binary recognition distinction (`studied` vs `new`) is preserved in `condition`.
- The finer-grained recognition subtype is preserved in `probe_type`.
- The prompt text includes a study phase built from all words in `liste.xls`; this study sequence is shared across participants.
