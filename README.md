# PsychLing-101

PsychLing-101 is a community-driven effort to compile a database of psycholinguistic data. 

Our goals are:

1. Organize and make available psycholinguistic data by converting existing data into a unified, standardized format.
2. Convert psycholinguistic data into a format that can be used to fine-tune and evaluate large language models (LLMs).
3. Collaboratively produce an article describing the database to be sent to a leading psycholinguistic outlet (e.g., ACL).  

The project is led by Taisiia Tikhomirova and Dirk U. Wulff at the Center for Adaptive Rationality at the Max Planck Institute for Human Development and supported by: Valentin Kriegmair (MPI for Human Development), Fritz Günther (Humboldt University), Marco Marelli (University of Milano-Bicocca), and Marcel Binz (Helmholtz Munich). 

PsychLing-101 will be open for contributions until December 1st, 2025. Future projects (PsychLing-201, PsychLing-301) may follow.

Currently, PsychLing-101 includes the data from XX studies, XX participants, and XX trials.  

## Participation rules

1. All data contributors will be co-authors on the final paper.
2. By contributing datasets to this repository, you agree to make them immediately available under our license (see below). We cannot delay availability to align with other projects' publication timelines.
3. You may not use any dataset in this repository for publication purposes before the official PsychLing-101 paper is released.
4. Anyone who wants to contribute data—either new or existing—must contact us first (see below).

   

## Data Scope and Inclusion Criteria

[WIP] 

We welcome a broad range of psycholinguistic data. Each submission is evaluated individually, and we’re happy to discuss edge cases or special formats. The following guidelines serve as a starting point:

### Scope

1. The study should primarily investigate language processing (e.g., lexical access, sentence comprehension, priming).

2. Multilingual datasets are allowed, but metadata such as column headers, participant IDs, task labels, and trial numbers should be provided in English.

3. Brain imaging data (EEG, fMRI) is welcome if formatted as CSV.

4. Images used as stimuli may be included. Audio or video files are currently not supported.

### Requirements

1. Data must include raw, trial-level information (no aggregated results).

2. Data must be convertible into a structured, text-based format.

For the list of datasets currently being processed and datasets that are open for contribution, please consult [CONTRIBUTING.md](https://github.com/Data-X01/PsychLing-101/blob/main/CONTRIBUTING.md).


## How to contribute

We welcome contributions of psycholinguistic datasets, whether newly collected or pre-existing. To maintain consistency and transparency, please follow the workflow below. All contributors must first contact the project team before submitting any datasets.

### Step 0: Before You Start

Before working on your submission, please do the following:

1. Consult [CONTRIBUTING.md](https://github.com/Data-X01/PsychLing-101/blob/main/CONTRIBUTING.md) to make sure others aren't already working on the dataset you'd like to contribute.
2. Contact us via a [Github issue](https://github.com/Data-X01/PsychLing-101/issues/new/choose) or [email](mailto:psychling101@gmail.com), describing the dataset you would like to contribute.   

### Step 1: Organize Raw Data

1. Create a new folder named using the format: `authorYEAR_title` (e.g., `smith2000_priming`).
2. Inside this folder, create a subfolder named `original_data/`.
3. Place **all raw files** from the source (e.g., OSF, author websites, repositories) into `original_data/`. Supported formats include `.csv`, `.tsv`, `.xlsx`, `.mat`, and `.json`.
4. If raw data exceeds GitHub's file size limit, use [Git LFS](https://git-lfs.com/) to store and track these files.


### Step 2: Preprocess Raw Data

1. In the main experiment folder, create a subfolder named `processed_data/`.
2. In the main experiment folder, create a script named `preprocess_data.py`.
3. This script should:
   - Read all files from `original_data/` subfolder.
   - Convert them into a **standardized CSV format** and write them into the `processed_data/' subfolder, following these rules:
     - Each experiment corresponds to a single CSV file: `exp1.csv`, `exp2.csv`, etc.
     - Each row must represent a single trial.
     - Follow the variable naming conventions and descriptions specified in [CODEBOOK.csv](CODEBOOK.csv) to ensure consistency across the repository.
     - Additional columns may be added if necessary.
     - Use zero-based indexing by default.
     - If no reward value is provided: assign `+1` for correct, `-1` for incorrect, and `0` for neutral responses.


### Step 3: Generate Prompts for LLM Fine-Tuning

1. In the experiment folder, create a script named `generate_prompts.py`.
2. This script should:
   - Read the standardized CSV file(s).
   - Generate a JSONL file (`prompts.jsonl`) with one line per participant.
   - Each prompt should:
     - Represent an entire session from one participant.
     - Include trial-by-trial data.
     - Begin with the instructions. Use original instructions, if available.
     - Mark human responses with `<< >>` (do not use these symbols elsewhere).
     - For discrete choice tasks, randomize the naming of options per participant (see [binz2022heuristics/generate_prompts.py](https://github.com/marcelbinz/Psych-201/tree/main/binz2022heuristics/generate_prompts.py)).
     - Stay within a 32K token limit per participant.

Example prompt:

~~~

In this task, you will see two words at the time. If both words are REAL ENGLISH words, you press the button \"a\". If ONE or BOTH words are non-sense words (for example \"FLUMMOL\"), you press the button \"l\". Respond within 2 seconds.

Trial 1: The word pair is 'table' and 'mirror'. You press <<a>>. Correct.
Trial 2: The word pair is 'flummol' and 'mirror'. You press <<l>>. Correct.
Trial 3: The word pair is 'glonch' and 'smarp'. You press <<l>>. Correct.
Trial 4: The word pair is 'planet' and 'flower'. You press <<a>>. Correct.
Trial 5: The word pair is 'snarp' and 'blonk'. You press <<l>>. Correct.
Trial 6: The word pair is 'dog' and 'fleeb'. You press <<l>>. Correct.
Trial 7: The word pair is 'sun' and 'cloud'. You press <<a>>. Correct.
Trial 8: The word pair is 'cheef' and 'grass'. You press <<l>>. Correct.

~~~

### Step 4: (Optional) Images

If your dataset includes images:

1. Prepare a lower-resolution version of the images to minimize file size.

2. Place all relevant images into a single folder and compress them into a images.zip archive.

3. Add the archive to your main experiment folder. If the zipped file exceeds GitHub’s size limit, use Git LFS to track and store it.

4. In your CSV file (e.g., exp1.csv), add a column named image_filename that matches each trial’s image (e.g., apple.jpg, scene1.png).

5. In your README.md, briefly describe:

   How images were used in the experiment (e.g., as stimuli, options, or cues)

   Any preprocessing applied to reduce image resolution or format
      

### Step 5: Structure Your Repository

Ensure your experiment folder includes the following:

- `README.md`: Includes a paper reference and link to original data.
- `original_data/`: Raw source files in their original format.
- `processed_data/`: Preprocessed exp*.csv files.
- `Codebook.csv`: A table defining all column names used in exp*.csv files.
- `preprocess_data.py`: Script for standardizing raw data.
- `generate_prompts.py`: Script for creating text-based prompts.
- `prompts.jsonl.zip`: A zipped JSONL file with one line per participant. Each line should have the following three fields:
  - `"text"`: Full natural language prompt with instructions, cover story and trial-by-trial data.
  - `"experiment"`: Identifier for the experiment.
  - `"participant"`: Participant ID.
  - Optional metadata fields (if available):
    - `"RTs"`: List of reaction times in ms.
    - `"age"`, `"diagnosis"`, `"nationality"`, or questionnaire-derived statistics.


### Step 5: Submission 

1. Fork the repository.
   
3. Clone the forked repository:
~~~
git clone https://github.com/YOUR-USERNAME/PsychLing-101
~~~

3. Add your experiments and push:

~~~
cd PsychLing-101/
(add your experiments)
git push
~~~

4. Click on "Pull requests", then "New pull request", finally "Create pull request".


### Step 6: Review process

There will be a lightweight review process ensuring that requirements are fulfilled. The communication for this will be done via the corresponding pull request.


## Licensing

This repository is shared under CC BY-NC-SA 4.0, with the following additional restrictions: You may not use the data in this repository for publication or presentation purposes until the official PsychLing-101 paper is released.

All contributors and users are expected to comply.
