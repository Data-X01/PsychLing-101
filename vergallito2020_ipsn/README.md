# Italian Perceptual Strength Norms (IPSN)

## Reference

Vergallito, A., Petilli, M. A., & Marelli, M. (2020). *Perceptual modality norms for 1,121 Italian words: A comparison with concreteness and imageability scores and an analysis of their impact in word processing tasks*. Behavior Research Methods. https://doi.org/10.3758/s13428-019-01337-8

## Data source

Trial-level supplementary data are available from the Open Science Framework project associated with the article:

https://osf.io/zdg59/

## Overview

This contribution contains trial-level data from three components of the study:

1. **Perceptual-strength ratings** for 1,121 Italian words. Participants rated the extent to which each word referent is experienced through five perceptual modalities: vision, taste, touch, smell, and hearing.
2. **Lexical decision task** used to evaluate the predictive validity of the perceptual-strength norms. Participants classified letter strings as words or pseudowords. Accuracy and reaction time were recorded for each trial.
3. **Word-naming task** used to evaluate the predictive validity of the perceptual-strength norms. Participants read words aloud as quickly as possible. Accuracy and reaction time were recorded for each trial.

## Folder structure

```text
vergallito2020_ipsn/
├── README.md
├── CODEBOOK.csv
├── preprocess_data.py
├── generate_prompts.py
├── prompts.jsonl.zip
├── original_data/
│   ├── Italian_Perceptual_Rating_raw.txt
│   ├── Italian_ANEW_Lexical_Decision_raw.txt
│   └── Italian_ANEW_Naming_raw.txt
└── processed_data/
    ├── exp1.csv
    ├── exp2.csv
    └── exp3.csv
```

## Raw files

### `Italian_Perceptual_Rating_raw.txt`

Raw trial-level perceptual-strength ratings. Each row corresponds to one participant rating one Italian word. The five sensory ratings are retained in separate columns because they were collected within the same experimental trial.

### `Italian_ANEW_Lexical_Decision_raw.txt`

Raw trial-level lexical-decision data. Each row corresponds to one presented word or pseudoword. Accuracy and reaction time are retained in separate columns within the same row because they are two outcomes from the same trial.

### `Italian_ANEW_Naming_raw.txt`

Raw trial-level word-naming data. Each row corresponds to one presented word. Accuracy and reaction time are retained in separate columns within the same row because they are two outcomes from the same trial.

## Processed files

The script `preprocess_data.py` converts the three raw files into standardized UTF-8 CSV files:

- `processed_data/exp1.csv`
- `processed_data/exp2.csv`
- `processed_data/exp3.csv`

The processed files use English variable names and retain the original trial-level observations.

## Trial identifiers and presentation order

The released raw files do not preserve the original randomized presentation order. Accordingly, the processed files do **not** include a `trial_order` column.

The `trial_id` field is a technical row identifier generated during preprocessing. Its numeric suffix ensures uniqueness but must **not** be interpreted as the order in which the participant saw the stimuli.

## Preprocessing

Run the preprocessing script from the repository root:

```bash
python vergallito2020_ipsn/preprocess_data.py
```

Expected output dimensions:

| Processed file | Participants | Sessions | Rows |
|---|---:|---:|---:|
| `exp1.csv` | 57 | — | 63,516 |
| `exp2.csv` | 30 in the released raw file | 60 | 67,260 |
| `exp3.csv` | 28 | 56 | 31,388 |

For the perceptual-strength ratings, 180 rows contain at least one missing sensory rating. Missing values are preserved as empty cells in the standardized CSV.

## Notes

The published article reports 33 recruited participants for the lexical-decision task. The released raw file contains data from 30 participants, consistent with the exclusion of three participants described in the article.
