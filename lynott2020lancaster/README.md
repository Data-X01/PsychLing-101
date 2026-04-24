# Lynott et al. (2020) – Lancaster Sensorimotor Norms

## Citation

Lynott, D., Connell, L., Brysbaert, M. et al. The Lancaster Sensorimotor Norms: multidimensional measures of perceptual and action strength for 40,000 English words. Behav Res 52, 1271–1291 (2020). https://doi.org/10.3758/s13428-019-01316-z

## Data Source

Data collected online via Amazon’s Mechanical Turk. Original trial-level data available at: https://osf.io/7emr6/overview 

## Task Description

Participants rated ~40,000 English words on two separate norming components administered as distinct online experiments:

1. **Perception norms** (`exp1`): Participants rated how strongly each word is experienced through six perceptual modalities.
2. **Action norms** (`exp2`): Participants rated how strongly each word is associated with actions performed by five body-part effectors.

Ratings were made on a scale from 0 (*not at all*) to 5 (*greatly*). On each trial, participants could also tick a "Don't know the meaning of this word" checkbox (`unknown_word`: 0 = knows the word, 1 = does not know the word).

### Perception norms – dimensions

| Column | On-screen label |
|---|---|
| `Auditory` | By hearing |
| `Gustatory` | By tasting |
| `Haptic` | By feeling through touch |
| `Interoceptive` | By sensations inside your body |
| `Olfactory` | By smelling |
| `Visual` | By seeing |

### Action norms – dimensions

| Column | On-screen label |
|---|---|
| `Foot_leg` | foot / leg |
| `Hand_arm` | hand / arm |
| `Head` | head excluding mouth |
| `Mouth` | mouth / throat |
| `Torso` | torso |

### Prompt template

Each participant's trials are chunked into blocks of up to 100 trials. Each block becomes one JSONL entry. Trial numbering restarts at 1 within each chunk. The `participant_id` field is suffixed with `_part1`, `_part2`, etc. to uniquely identify each chunk.

Each prompt begins with a general content warning, followed by experiment-specific instructions, then trial-by-trial data.

**General instruction (shared by both experiments):**
```
This study uses a wide range of words that are encountered in everyday life. Very
occasionally, this means that some words may be offensive or explicit. If you feel
that being exposed to such words will be distressing for you, we would like to remind
you that you are free to end your participation in the study now or at any time you
choose.

If you wish to continue, please press the "Next" button.
```

**Perception trial:**
```
Trial {n}: To what extent do you experience {WORD} (integer from 0 = not at all to 5 = greatly)
  By hearing: <<{Auditory}>>
  By tasting: <<{Gustatory}>>
  By feeling through touch: <<{Haptic}>>
  By sensations inside your body: <<{Interoceptive}>>
  By smelling: <<{Olfactory}>>
  By seeing: <<{Visual}>>
  Don't know the meaning of this word: <<{unknown_word}>>
```

**Action trial:**
```
Trial {n}: To what extent do you experience {WORD} by performing an action with the (integer from 0 = not at all to 5 = greatly)
  foot / leg: <<{Foot_leg}>>
  hand / arm: <<{Hand_arm}>>
  head excluding mouth: <<{Head}>>
  mouth / throat: <<{Mouth}>>
  torso: <<{Torso}>>
  Don't know the meaning of this word: <<{unknown_word}>>
```

## Dataset Details

| | Perception (`exp1`) | Action (`exp2`) |
|---|---|---|
| Words | 39,486 | 39,954 |
| Participants | 2,612 | 1,931 |
| Trial rows | 787,990 | 831,663 |
| Unknown word (% of trials) | 7.3% | 6.0% |
| Dimensions | 6 | 5 |
| Rating scale | 0–5 | 0–5 |
| Language | English | English |

## Files

```
lynott2020lancaster/
├── original_data/
│   └── sm_norms_trial_level.csv   # Raw trial-level data from OSF
├── processed_data/
│   ├── exp1.csv                   # Perception norms (wide format, one row per participant × word)
│   └── exp2.csv                   # Action norms    (wide format, one row per participant × word)
├── preprocess_data.py             # Converts raw data to processed_data/exp*.csv
├── generate_prompts.py            # Generates prompts.jsonl.zip from processed CSVs
├── prompts.jsonl.zip              # Zipped JSONL; one entry per participant chunk; 9240 prompt entries for Perception (2612 participants); 9296 prompt entries for Action (1931 participants)
├── CODEBOOK.csv                   # Variable descriptions and canonical column names
└── README.md
```

## JSONL Entry Fields

| Field | Type | Description |
|---|---|---|
| `text` | string | Full prompt: instructions + trial-by-trial data |
| `experiment` | string | `lynott2020lancaster/perception` or `lynott2020lancaster/action` |
| `participant_id` | string | Anonymised participant ID with chunk suffix (e.g. `P001_part1`) |
| `age` | int | Participant age (if available) |
| `gender` | string | Participant gender (if available) |