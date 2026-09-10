# Codebook: Semantic Networks of Younger and Older Adults

## Reference

Wulff, D. U., Hills, T. T., & Mata, R. (2022). Structural differences in the semantic networks of younger and older adults. *Scientific Reports*, *12*, 21459. https://doi.org/10.1038/s41598-022-11698-4

## Datasets

This codebook documents three datasets derived from two studies reported in Wulff, Hills, and Mata (2022). The studies investigate age-related differences in the structure of semantic networks in younger and older adults using both semantic fluency and similarity rating tasks. Data were collected at the Max Planck Institute for Human Development, Berlin.

- **Study1_Fluency.csv** — 10-minute semantic fluency data from Study 1 (referred to as "Study 1" in the paper). Participants (41 younger, 71 older adults) named as many exemplars as possible from two semantic categories (animals and countries) in 10-minute blocks. Responses were spoken into a microphone and transcribed.

- **Study2_Fluency.csv** — 10-minute semantic fluency data from Study 2 (referred to as "Study 2" in the paper). Participants (36 younger, 36 older adults) named as many animals as possible within 10 minutes. This study covers only the animal category.

- **Study2_SimRatings.csv** — Pairwise similarity ratings from Study 2. Each of the 72 participants rated 2,253 pairs of animals (1,953 unique pairs of 63 animals plus 300 repeated pairs) on a 1–20 scale ("extremely dissimilar" to "extremely similar") over the course of approximately one week using a take-home tablet. These ratings serve as the basis for the individual-level semantic networks analyzed in the paper.

## Variables

### Study1_Fluency.csv

- `id` — Participant identifier (unique within the study).
- `cat` — Semantic category cued for retrieval, either `animal` or `country`.
- `time` — Time in ms at which the response was produced since the start of the 10-minute fluency block.
- `word` — The response produced by the participant (raw).
- `correct` — The response produced by the participant (corrected).
- `round` — Block indicator specifying whether `animal` or `country` was first.
- `age` — Participant age in years at time of testing.
- `group` — Age group label, either `younger` (18–34) or `older` (66–81).
- `sex` — Participant sex (`male`/`female`).

### Study2_Fluency.csv

- `id` — Participant identifier (unique within the study).
- `time` — Time at which the response was produced, likely in seconds since the start of the 10-minute fluency block.
- `word` — The response produced by the participant.
- `correct` — Indicator of whether the response was retained as a valid animal exemplar after preprocessing.
- `age` — Participant age in years at time of testing.
- `group` — Age group label, either `younger` (18–32) or `older` (65–78).
- `sex` — Participant sex (`male`/`female`).

### Study2_SimRatings.csv

- `id` — Participant identifier (matches `id` in Study2_Fluency.csv where applicable).
- `group` — Age group label, either `younger` or `older`.
- `age` — Participant age in years at time of testing.
- `sex` — Participant sex (`male`/`female`).
- `part` — Study part indicator separating `test` and `retest` items.
- `pair_id` — Unique index of the animal pair being rated.
- `pair` — String representation of the pair (e.g., ordered concatenation of `left_word` and `right_word`).
- `time` — Response time for the individual rating (in seconds).
- `rating` — Raw similarity rating on the 1–20 scale (0/1 = extremely dissimilar, 20 = extremely similar).
- `left_word` — Animal presented on the left side of the rating screen.
- `right_word` — Animal presented on the right side of the rating screen.
- `revPair` — Identifier of the reversed pair (i.e., the same two animals presented in opposite left/right order); used to link repeat pairs for reliability analyses.
- `rev` — Indicator of whether the current trial is a reversed/repeated presentation of an earlier pair (FALSE = original, TRUE = reversed). NA for first presentations. 
- `norm_rating` — Normalized rating, mapping each participant's minimum and maximum rating to 0 and 1, respectively, as described in the paper. Used as edge weights in individual-level semantic networks.


