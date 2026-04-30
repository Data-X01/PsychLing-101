# de Varda, Lamarra, et al. (2025) - Iconicity Rating Task with Italian L1 and L2 Speakers

## Citation
de Varda, A. G., Lamarra, T., Ravelli, A. A., Saponaro, C., Giustolisi, B., Bolognesi, M. (2025). IconicITA: Iconicity ratings of the Italian affective lexicon. *PLoS One* 20(12): e0337947. https://doi.org/10.1371/journal.pone.0337947

## Data Source
Data collected via Prolific and snowball sampling between December 7, 2023 and April 10, 2024. L1 participants were native Italian speakers; L2 participants were native English speakers with at least B1 proficiency in Italian, pre-screened via the LexIta lexical decision task (threshold: score ≥ 26).

## Task Description
Participants rated Italian words on a 7-point Likert scale for iconicity — i.e., how much the sound of a word resembles its meaning. For each word, participants also had the option to select "I do not know this word" and skip the rating. Instructions were presented in both Italian and English.

## Instructions (summarized)
Participants were asked to rate a list of words in terms of how much they considered each word to be iconic. They were instructed to pronounce each word aloud and focus on the meaning of the whole word rather than decomposing it into parts. A rating of 1 indicated no perceived link between sound and meaning; a rating of 7 indicated a very strong perceived link. Onomatopoeic words such as *boom*, *crash*, and *bang* were given as examples of high-iconicity words; words such as *ragione* (reason), *manico* (handle), and *pensione* (pension/boarding house) as examples of low-iconicity words.


## Prompt Template

```
Trial {trial_idx}. La parola italiana è: '{stimulus}'. Quanto è iconica questa parola? 1 (Per niente iconica) 2 3 4 5 6 7 (Moltissimo iconica). Hai valutato: <<{response}>>
```

## Dataset Details

- **Total items:** 1,121 words from the ANEW database + 30 additional words (5 onomatopoeic control words present in all lists; 25 phonosymbolic words, 5 per list)
- **Lists:** 5 (224 words per list, one list with 225 words)
- **Total participants:** 111 after exclusions (54 L1, 57 L2); participants could rate 1 or more lists
- **Language:** Italian (stimuli); instructions in Italian and English

## Exclusion Criteria
A leave-one-out (LOO) reliability check was applied to filter out unreliable raters. For each participant, their ratings were correlated with the mean ratings of all other participants who rated the same words. Only participants with a positive and significant correlation (r > 0, p < .05) were retained. Out of 59 L1 participants, 54 passed (91.53%); out of 69 L2 participants, 57 passed (82.61%).

## Files

- `original_data/`: Raw data files from Prolific exports
- `processed_data/exp1.csv`: Cleaned trial-level data
- `preprocess_data.R`: Script to process raw data
- `generate_prompts.R`: Script to generate LLM prompts
- `prompts.jsonl.zip`: Zipped JSONL file with participant-level prompts
- `CODEBOOK.csv`: Variable descriptions
