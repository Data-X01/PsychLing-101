# Balota et al. (2007) - The English Lexicon Project - Lexical Decision Task (LDT)

## Citation

Balota, D. A., Yap, M. J., Hutchison, K. A., Cortese, M. J., Kessler, B., Loftis, B., ... & Treiman, R. (2007). The English lexicon project. Behavior research methods, 39(3), 445-459. https://doi.org/10.3758/BF03193014

## Data Source

### Data
Data collected at 6 (private and public) universities across the Midwest, Northeast and Southeast regions of the United States between March 2001 and July 2003. Participants were native English speakers. https://osf.io/n63s2/files/osfstorage

### Authors' Code Base
Includes scripts for reading the files, preprocessing and some model estimations in Julia language. https://github.com/dmbates/EnglishLexicon.jl/tree/main

The authors' code served as a basis for `preprocess_data.py`, although some modifications had been made (see Preprocessing Notes). 

## Task Description

Participants had to indicate whether a presented stimulus was a word or a nonword, i.e., **Lexical Decision Task (LDT)**.

### Prompt instruction (freely written)
In this task, you will see either a word or a nonword. Please press '`{choice_options[0]}`' when a word appears and '`{choice_options[1]}`' when a nonwords appears. Respond within 4 seconds.

### Prompt template
Trial line:
```
Trial {trial_num}: You see '{row['stimulus']}'. You press <<{chosen_button}>>.

# Feedback was provided during the whole experiment
if row["accuracy"] == 0:
    trial_line += " Incorrect!"
```

Break line:
Participants were given a break after every 250 trials with every thrid break lasting 3 minutes and all others lasting 1 minute. They were provided with feedback regarding their accuracy and average response time for the previous 250 trials along with the instruction to "use this time to get a drink, stretch, or walk around" in the longer breaks.
```
if block_accuracy < .8:
    feedback_accuracy = "Please increase your level of accuracy"
else:
    feedback_accuracy = "Please maintain this level of accuracy"

if block_rt > 1000:
    feedback_rt = "Please decrease your response time"
else:
    feedback_rt = "Please maintain this reaction time"

if break_count % 3 == 0:
    prompt_text += (
        "3 minute break. Please use this time to get a drink, stretch, or walk around.\n"+
        f"Your accuracy in the last 250 trials was {int(block_accuracy*100)} %. {feedback_accuracy}.\n"+
        f"Your average reaction time in the last 250 trials was {int(block_rt)} ms. {feedback_rt}."
    )
else:
    prompt_text += (
        "1 minute break.\n"+
        f"Your accuracy in the last 250 trials was {int(block_accuracy*100)} %. {feedback_accuracy}.\n"+
        f"Your average reaction time in the last 250 trials was {int(block_rt)} ms. {feedback_rt}."
    )
```

## Dataset Details

- **Total items**: 40,481 english words and 40,481 nonwords
- **Total participants**: 814
- **Total data points**: 2,744,578
- **Language**: English

## Preprocessing Notes

- `years_of_education`: The variable was supposed to be years of education but some are recorded as years of university. A corrected variable `years_of_education_corrected` was added, to which 12 was added if the original value was smaller than 12 the approximate the correct value.
- `rt`: In the data cleaning process of the authors, trials with a reaction time of less than 250 ms or more than 4,000 ms were excluded from the data set. Here, however, only trials with a reaction time of less than 0 ms or more than 4,000 ms were excluded. This applies to 4 trials. The upper bound of 4,000 ms was set because reaction times above this bound were technically impossible due to the program code, i.e., the values must be faulty.
- `accuracy`: The variable contained values other than 0 or 1. Since the participants' responses had to be inferred from the `accuracy` and `lexicality` variables, the 1,370 trials in question were removed from the data set. This approach is consistent with the authors' preprocessing procedure.

## Files

- `original_data/ldt_raw.zip`: Raw data files
- `original_data/ldt_extract.jl`: The authors' code for data extraction as reference
- `processed_data/exp1.csv`: Cleaned trial-level data
- `preprocess_data.py`: Script to process raw data
- `generate_prompts.py`: Script to generate LLM prompts
- `prompts.jsonl.zip`: Zipped JSONL file with participant-level prompts
- `CODEBOOK.csv`: Variable descriptions