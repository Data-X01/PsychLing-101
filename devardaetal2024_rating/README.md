# de Varda et al. (2024) - Cloze Probability Rating Task

## Citation

de Varda, A. G., Marelli, M., & Amenta, S. (2024). Cloze probability, predictability ratings, and computational estimates for 205 English sentences, aligned with existing EEG and reading time data. *Behavior Research Methods*, 56(5), 5190-5213. https://doi.org/10.3758/s13428-024-02379-9

## Data Source

Data collected via Prolific in December 2020. Participants were native English speakers.

## Task Description

Participants completed a **predictability rating task** where they saw sentence fragments paired with a target word and rated (Likert, 1-5) how much they expected to see that word following the sentence fragment.

### Instructions (from paper)

Participants were presented with both the sentence fragment and the associated upcoming word and asked to rate, on a scale from 1 to 5, how much they would expect the presented word to follow the sentence fragment. Instructions emphasized that they were not asking to evaluate how plausible or sensible that word was, but rather how much they would expect to find it while reading the preceding sentence context.

## Dataset Details

- **Total items**: 1,726 sentence fragment + target word pairs
- **Lists**: 8 (items distributed across lists, ~216 items per list)
- **Total participants**: 470 (after exclusions based on comprehension checks) (about 60 per list)
- **Language**: English

## Exclusion Criteria

Participants were excluded if they answered fewer than 8 out of 10 comprehension check questions correctly.

## Known Issues

- List 5 had an encoding error where "2 - Very much" appeared instead of "5 - Very much". This has been corrected in preprocessing.

## Files

- `original_data/`: Raw data files from Prolific exports
- `processed_data/exp1.csv`: Cleaned trial-level data
- `preprocess_data.py`: Script to process raw data
- `generate_prompts.py`: Script to generate LLM prompts
- `prompts.jsonl.zip`: Zipped JSONL file with participant-level prompts
- `CODEBOOK.csv`: Variable descriptions

