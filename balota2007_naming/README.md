# Balota et al. (2007) - The English Lexicon Project - Naming Task

## Citation

Balota, D. A., Yap, M. J., Hutchison, K. A., Cortese, M. J., Kessler, B., Loftis, B., ... & Treiman, R. (2007). The English lexicon project. Behavior research methods, 39(3), 445-459. https://doi.org/10.3758/BF03193014

## Data Source

### Data
Data collected at 6 (private and public) universities across the Midwest, Northeast and Southeast regions of the United States between November 2001 and August 2004. Participants were native English speakers. https://osf.io/n63s2/files/osfstorage

### Authors' Code Base
Includes scripts for reading the files, preprocessing and some model estimations in Julia language. https://github.com/dmbates/EnglishLexicon.jl/tree/main

The authors' code served as a basis for `preprocess_data.py`, although some modifications had been made (see Preprocessing Notes). 

## Task Description

Participants had to **speak aloud words** and label whether their pronunciation was correct, incorrect, or if they are uncertain of the pronunciation. Note: There is no variable in the data set that codes the accuracy of the participants' labels.

### Prompt instruction (freely written)
In this task, you will see words that you must speak aloud. Speak within 4 seconds. After you've said the word, you must indicate whether you pronounced it correctly, are uncertain of the pronunciation, pronounced it incorrectly, or if a microphone error occured. It is very important that you label your responses to the best of your knowledge, as this information will be used in the data analysis.

### Prompt template
Trial line:
```
mapping_coding = {
    1: "correct pronunciation",
    2: "uncertainty about pronunciation",
    3: "mispronunciation",
    4: "microphone error",
    5: "time-out"
}

if row["coding_category"] == 5:
    trial_line = f"Trial {trial_num}: You see '{row['stimulus']}'. Too slow!"
else:
    trial_line = f"Trial {trial_num}: You see '{row['stimulus']}'. You speak within <<{int(row['rt'])}>> ms and indicate <<{mapping_coding[row['coding_category']]}>>."
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

- **Total items**: 40,481 english words
- **Total participants**: 444
- **Total data points**: 1,123,342
- **Language**: English

## Preprocessing Notes

- `years_of_education`: The variable was supposed to be years of education but some are recorded as years of university. A corrected variable `years_of_education_corrected` was added, to which 12 was added if the original value was smaller than 12 to approximate the correct value.
- `self_coded_accuracy`: The variable was estimated from the participants' self-coded accuracy of their pronunciation with 1 = pronunciation labeled as correct and 0 = any other labeling option.

## Files

- `original_data/nmg_raw.zip`: Raw data files
- `original_data/nmg_extract.jl`: The authors' code for data extraction as reference
- `processed_data/exp1.csv`: Cleaned trial-level data
- `preprocess_data.py`: Script to process raw data
- `generate_prompts.py`: Script to generate LLM prompts
- `prompts.jsonl.zip`: Zipped JSONL file with participant-level prompts
- `CODEBOOK.csv`: Variable descriptions