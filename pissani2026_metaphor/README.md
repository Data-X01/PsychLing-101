
# Metaphor Dataset – README

## Reference
Pissani, L., & de Almeida, R. G. (2026). Metaphors in context and in isolation: Familiarity, aptness, concreteness, metaphoricity, and structure norms for 300 two-word expressions. Behavior Research Methods, 58(1), 31.

## Data Source
https://osf.io/xk3j9/overview

## Data Processing
Raw CSV files are stored in `original_data/`. Run `preprocess_data.R` from this folder to create the standardized CSV files in `processed_data/`:

- `exp1.csv`: aptness ratings from `df_apt.csv`
- `exp2.csv`: concreteness ratings from `df_con.csv`
- `exp3.csv`: constituency ratings from `df_cons.csv`
- `exp4.csv`: familiarity ratings from `df_fam.csv`
- `exp5.csv`: metaphoricity ratings from `df_met.csv`

Run `generate_prompts.R` after preprocessing to create `prompts.jsonl` and `prompts.jsonl.zip`. Each JSONL row represents one participant session and contains the full trial sequence with the participant's rating marked using `<< >>`.

## Images
This dataset does not include image stimuli.
