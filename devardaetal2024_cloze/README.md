# de Varda et al. (2024) - Cloze Probability Task

## Citation

de Varda, A. G., Marelli, M., & Amenta, S. (2024). Cloze probability, predictability ratings, and computational estimates for 205 English sentences, aligned with existing EEG and reading time data. *Behavior Research Methods*, 56(5), 5190-5213. https://doi.org/10.3758/s13428-024-02379-9

## Data Source

Data collected via Prolific in December 2020. Participants were native English speakers.

## Task Description

Participants completed a **cloze probability task** where they saw sentence fragments extracted from narrative texts and were asked to type the next word they expected to follow.

### Instructions (from paper)

Participants were asked to continue the sentence by writing what they expect to be the next word. The instructions stressed that, even if participants came up with several options, their task was always to produce one single word – the one that, in their immediate intuition, should follow what was presented. Moreover, it was emphasized that the to-be-produced word could belong to any part-of-speech, including articles and prepositions.

## Dataset Details

- **Total items**: 1,726 sentence fragments
- **Lists**: 8 (items distributed across lists, ~216 items per list)
- **Total participants**: 630 (after exclusions based on comprehension checks) (about 80 per list)
- **Language**: English

## Exclusion Criteria

Participants were excluded if they answered fewer than 8 out of 10 comprehension check questions correctly.

## Files

- `original_data/`: Raw data files from Prolific exports
- `processed_data/exp1.csv`: Cleaned trial-level data
- `preprocess_data.py`: Script to process raw data
- `generate_prompts.py`: Script to generate LLM prompts
- `prompts.jsonl.zip`: Zipped JSONL file with participant-level prompts
- `CODEBOOK.csv`: Variable descriptions

