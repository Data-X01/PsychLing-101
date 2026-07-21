# gatti2024_geographical

## Overview
This dataset contains trial-level data from a geographical judgment task. On each trial, participants saw two city names, one on the left and one on the right, and selected which city was geographically closer to Milan.

## Citation
Gatti, D, Anceresi, G, Marelli, M, Vecchi T, & Rinaldi, L (2024). Decomposing geographical judgments into spatial, temporal and linguistic components. Psychological Research, 1-12. https://doi.org/10.1007/s00426-024-01980-7

## Source files
- `original_data/time_data.csv`

## Raw data structure
The raw file is semicolon-delimited and contains the following columns:
- `Cit2`
- `Cit1`
- `ID`
- `age`
- `gender`
- `hand`
- `resp`
- `RTs`
- `accuracy`

## Processing summary
`preprocess_data.py`:
- reads `original_data/time_data.csv` with `;` as delimiter
- preserves participant-level fields from the raw file
- preserves the raw presentation order within participant in `trial_order`
- renames `Cit1` and `Cit2` as `city_left` and `city_right`
- preserves the raw response key in `response_raw`
- derives `response_side` from the response key (`a` = left, `l` = right)
- parses reaction times from `rt_raw` into numeric milliseconds in `rt_ms` by converting decimal commas to decimal points
- normalizes the source gender codes into `gender` (`F` / `M`), while preserving `gender_raw`
- normalizes handedness into `hand` (`right` / `left`), while preserving `hand_raw`
- infers `correct_response` and `correct_side` at the ordered city-pair level
- derives `response_correct` from `response_raw` and `correct_response`
- verifies that `response_correct` matches the raw `accuracy` field
- writes the processed trial-level file to `processed_data/exp1.csv`

## Processed file
- `processed_data/exp1.csv`

Columns in the processed file:
- `experiment`
- `participant_id`
- `trial_id`
- `trial_order`
- `phase_id`
- `age`
- `gender`
- `gender_raw`
- `hand`
- `hand_raw`
- `city_left`
- `city_right`
- `response_raw`
- `response_side`
- `correct_response`
- `correct_side`
- `accuracy`
- `response_correct`
- `rt_raw`
- `rt_ms`

## Notes
- The raw `gender` field contains `FALSE`, `M`, and `f`; these are standardized to `F` / `M` in `gender`, and the source value is retained in `gender_raw`.
- The raw `hand` field contains formatting variation (`DX`, `DX `, `dx`, `SX`); these are standardized to `right` / `left` in `hand`, and the source value is retained in `hand_raw`.
- Response keys are kept in the original coding: `a` for left and `l` for right.
- Prompt-generation keys are two distinct random uppercase letters sampled once per participant and mapped consistently to the two answer options for that participant.
- Participant-facing prompt text should contain only task-relevant content. Task metadata such as response side, correctness, and participant attributes belong in metadata fields rather than prompt text.
- The participant-facing text in `prompts.jsonl.zip` is in Italian, matching the language of the experiment.
- Each JSONL line contains exactly one participant. Reaction times are stored once per participant in the top-level `rt` list in milliseconds and are aligned with trial order.
