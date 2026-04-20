# gatti2023_semantic_priming

## Citation
Gatti, D, Marelli, M, & Rinaldi, L (2022). Out-of-vocabulary but not meaningless: Evidence for semantic-priming effects in pseudoword processing. Journal of Experimental Psychology: General, 152(3), 851–863. https://doi.org/10.1037/xge0001304 .

## Data source
Original data file:
- `original_data/data_acc.csv`

Source link: https://psycnet.apa.org/record/2023-05426-001

## Dataset contents
This folder contains trial-level semantic priming data.

### Raw data
- `original_data/data_acc.csv`

### Processed data
- `processed_data/exp1.csv`: semantic priming trial-level data

## Variable mapping used in `exp1.csv`
- `participant_id` <- `ID`
- `prime` <- `Prime`
- `target` <- `Target`
- `response` <- `resp`
- `response_correct` <- `resp_corr`
- `accuracy` <- `accuracy`
- `rt` <- `RTs` converted from decimal-comma strings to numeric seconds
- `age` <- `age`
- `gender` <- `gender` normalized to uppercase
- `hand` <- `hand` normalized to `right` / `left`
- `phase_id` = `judgment`
- `experiment` = `semantic_priming`

## Notes
- This processed file preserves the source trial structure.
- Responses are binary and the source file already includes both the correct response and trial accuracy.
