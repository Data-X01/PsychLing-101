# stella2026_formamentis_data

This folder contains trial-level data from a behavioural **forma mentis** word-association and valence-rating task, prepared for inclusion in PsychLing-101.

## Data source

The data are derived from the behavioural forma mentis network study reported in:

Haim, E., van den Bergh, L., Siew, C. S. Q., Kenett, Y. N., Marinazzo, D., & Stella, M. (2026). *Cognitive networks highlight differences and similarities in the STEM mindsets of human and LLM-simulated trainees, experts and academics*. **Journal of Complex Networks, 14**(2), cnag004. https://doi.org/10.1093/comnet/cnag004

Open-access article page: https://academic.oup.com/comnet/article/14/2/cnag004/8527975

PsychLing-101 project repository: https://github.com/MassimoStel/PsychLing-101

## Background

A **behavioural forma mentis network** is a cognitive network representation of how people associate and emotionally evaluate concepts. In this framework, words are represented as nodes and free associations are represented as links between concepts. Valence ratings provide an affective layer, making it possible to study not only which concepts are mentally connected, but also whether those concepts are perceived as positive, neutral, or negative.

The broader forma mentis framework was introduced and applied to STEM perception by Stella and colleagues:

Stella, M., de Nigris, S., Aloric, A., & Siew, C. S. Q. (2019). *Forma mentis networks quantify crucial differences in STEM perception between students and experts*. **PLOS ONE, 14**(10), e0222870. https://doi.org/10.1371/journal.pone.0222870

In that work, forma mentis networks were built from psycholinguistic data combining free associations to STEM concepts with valence ratings, allowing the authors to quantify differences in how students and experts conceptually and emotionally framed STEM topics.

## Task description

Participants completed a continued free-association task followed by valence ratings. Each participant saw 10 STEM-related or STEM-adjacent cue words:

- `art`
- `biology`
- `chemistry`
- `complex`
- `life`
- `mathematics`
- `physics`
- `school`
- `system`
- `university`

For each cue, participants provided three ordered single-word associations. They then rated the emotional valence of the cue and of each of the three associations on a 1-5 scale, where lower values indicate more negative affect, higher values indicate more positive affect, and 3 represents a neutral rating. Blank valence responses can occur when no strong sentiment was attached to a word.

The cleaned dataset contains the 177 valid human participants retained for analysis in the source study. The validity criterion followed the source paper: participants with more than 25% blank association responses, excluding valence scores, were removed.

## Data structure

The processed file is stored as:

```text
processed_data/exp1.csv
```

Each row is one participant-by-cue trial. The expected structure is:

```text
177 participants × 10 cue trials = 1770 rows
```

Core columns include:

- `participant_id`: anonymised participant/file identifier.
- `source_file`: original raw file name.
- `age`: participant age, where available.
- `gender`: participant gender, where available.
- `nationality`: participant nationality, where available.
- `first_language`: participant first language, where available.
- `occupation`: participant occupation or role, where available.
- `stem_background`: participant STEM-background indicator, where available.
- `trial_id`: unique trial identifier.
- `trial_order`: cue order within the participant session.
- `stimulus`: cue word.
- `response1`, `response2`, `response3`: ordered free associations.
- `stimulus_valence`: valence rating for the cue.
- `response1_valence`, `response2_valence`, `response3_valence`: valence ratings aligned with the three ordered responses.

## Network interpretation

A behavioural forma mentis network can be reconstructed from the cleaned trial-level data by treating cue words and response words as nodes and adding cue-response links for the three associations generated on each trial. The resulting network captures the participant's or group's associative structure around STEM-related concepts. Valence columns can be used as node attributes or affective annotations, allowing semantic frames to be coloured or summarised by emotional tone.

For example, a trial with cue `mathematics` and responses `numbers`, `logic`, and `equation` contributes three associative links:

```text
mathematics -- numbers
mathematics -- logic
mathematics -- equation
```

with valence scores attached to the cue and to each response.

## Files

```text
original_data/              Raw participant files.
processed_data/exp1.csv     Cleaned trial-level CSV for the 177 valid participants.
CODEBOOK.csv                Column definitions following PsychLing-101 conventions.
preprocess_data.py          Script used to convert raw files into processed_data/exp1.csv.
generate_prompts.py         Script used to convert exp1.csv into participant-level LLM prompts.
prompts.jsonl.zip           Zipped JSONL file with one natural-language prompt per participant.
README.md                   This file.
```

## Prompt-generation note

The accompanying `generate_prompts.py` script converts each participant session into one JSONL line. Each prompt includes the task instructions and all 10 trials for that participant. Human-generated associations and valence ratings are marked with `<< >>`, following the PsychLing-101 prompt-formatting requirement.

## Citation

If using this processed dataset, cite the source behavioural forma mentis network paper and the original forma mentis framework paper:

```bibtex
@article{haim2026cognitive,
  author = {Haim, Edith and van den Bergh, Lars and Siew, Cynthia S. Q. and Kenett, Yoed N. and Marinazzo, Daniele and Stella, Massimo},
  title = {Cognitive networks highlight differences and similarities in the STEM mindsets of human and LLM-simulated trainees, experts and academics},
  journal = {Journal of Complex Networks},
  volume = {14},
  number = {2},
  pages = {cnag004},
  year = {2026},
  doi = {10.1093/comnet/cnag004}
}

@article{stella2019formamentis,
  author = {Stella, Massimo and de Nigris, Sarah and Aloric, Aleksandra and Siew, Cynthia S. Q.},
  title = {Forma mentis networks quantify crucial differences in STEM perception between students and experts},
  journal = {PLOS ONE},
  volume = {14},
  number = {10},
  pages = {e0222870},
  year = {2019},
  doi = {10.1371/journal.pone.0222870}
}
```
