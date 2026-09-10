# Kyröläinen et al. (2022) - Valence rating of english words

## Citation

Kyröläinen, A. J., Luke, J., Libben, G., & Kuperman, V. (2022). Valence norms for 3,600 English words collected during the COVID-19 pandemic: Effects of age and the pandemic. Behavior Research Methods, 54(5), 2445-2456. https://doi.org/10.3758/s13428-021-01740-0

## Data Source

Data collected via Prolific from November 2020 - March 2021 during the COVID-19 pandemic. Participants were English speakers. https://osf.io/e6px8/overview?view_only=0bef4b18a10e4397b3dd04d7fb60559b

## Task Description

Participants were task with rating english words in terms of there **valence** on a scale of 1 (unhappy) to 9 (happy).

### Instructions (from paper)

The instructions informed the participant that the purpose of the study was to investigate emotion. The instructions asked participants to “respond to different types of words, by providing a rating on a scale of 1 (unhappy) to 9 (happy) of how you felt while reading each word. If you feel completely neutral you should rate a 5”.

In case the word was unknown to them, they were instructed to press the letter ‘n’.

### Prompt instruction (reconstructed from paper)
The purpose of this study is to investigate emotion. You will have to respond to different types of words, by providing a rating on a scale of 1 (unhappy) to 9 (happy) of how you felt while reading each word. If you feel completely neutral you should rate a 5. In case the word is unknown to you, press the letter 'n'.

### Prompt template
```
Trial {trial_num}: You see '{row["stimulus"]}'. {action}\n

if pd.isna(row["response"]):
    action = "You press <<n>>."
else:
    action = f"You answer <<{int(row["response"])}>>."
```

## Dataset Details

- **Total items**: 3,600 english words
- **Total participants**: 1,431
- **Total data points**: 157,230
- **Language**: English

## Files

- `original_data/`: Raw data files from Prolific exports
- `processed_data/exp1.csv`: Cleaned trial-level data
- `preprocess_data.py`: Script to process raw data
- `generate_prompts.py`: Script to generate LLM prompts
- `prompts.jsonl.zip`: Zipped JSONL file with participant-level prompts
- `CODEBOOK.csv`: Variable descriptions