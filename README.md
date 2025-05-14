# PsychLing-101

PsychLing-101 is a community-driven effort to collect, organize, and standardize datasets from psycholinguistic studies. PsychLing-101 focuses specifically on tasks central to psycholinguistics — such as lexical decision, priming, sentence processing, and related paradigms.

Our goals are:

1. Organize and preserve psycholinguistic data: Convert existing experiments into a unified, standardized format.

2. Convert psycholinguistic experiments into a format that can be used to fine-tune and evaluate large language models (LLMs).

This repository is a part of a collaborative publication effort. We intend to submit a comprehensive description of the dataset and associated methodology to the ACL Language Resources and Evaluation Conference (LREC).


Because this is a large collaborative project, it is necessary to define some **ground rules** to avoid chaos:

1. All contributors to data preprocessing will be co-authors on the final paper.

2. By contributing datasets to this repository, you agree to make them immediately available under our license (see below). We cannot delay availability to align with other projects' publication timelines.

3. **Importantly: you may not use any dataset in this repository for publication purposes before the official PsychLing-101 paper is released.**

4. Anyone who wants to contribute data—either new or existing—must contact us first to obtain approval. You can do this by:

   Creating an issue in this repository

   Sending an email to psychling101@gmail.com (TBD)

The project is currently coordinated by Dirk Wulff and Taisiia Tikhomirova, with support from Marco Marelli, Fritz Günther and Marcel Binz. 


## Scope of Psycholinguistic Data

[TO BE COMPLETED] 

For the list of datasets currently being processed and datasets that are open for contribution, please refer to the “List of Datasets in Progress” and “List of Open Datasets” sections in CONTRIBUTING.md.


## Timeline 

We aim to finalize the data collection by end of 2025 and submit our first paper shortly thereafter.
Future repositories (PsychLing-201, PsychLing-301) may follow.

**We are corrently in the process of collecting the data:** The deadline for the final submittions is ... 


## How to contribute

We welcome contributions of psycholinguistic experiments, whether newly collected or pre-existing. To maintain consistency and transparency, please follow the workflow below. All contributors must first contact the project team before submitting any experiment.

### Step 0: Get Approval Before You Start

Before working with any dataset, please request approval via one of the following:

1. Create a GitHub Issue briefly describing the dataset you'd like to contribute

2. Email us at psychling101@gmail.com (TBD)

Once approved, you may begin formatting and structuring your data.


### Step 1: Organize Raw Data

1. Create a new folder named using the format: `authorYEAR_title` (e.g., `smith2000_priming`).
2. Inside this folder, create a subfolder named `original_data/`.
3. Place **all raw files** from the source (e.g., OSF, author websites, repositories) into `original_data/`. Supported formats include `.csv`, `.tsv`, `.xlsx`, `.mat`, and `.json`.
4. If raw data exceeds GitHub's file size limit, use [Git LFS](https://git-lfs.com/) to store and track these files.


### Step 2: Preprocess Raw Data

1. In the main experiment folder, create a script named `preprocess_data.py`.
2. This script should:
   - Read all files from `original_data/`.
   - Convert them into a **standardized CSV format**, following these rules:
     - Each experiment corresponds to a single CSV file: `exp1.csv`, `exp2.csv`, etc.
     - Each row must represent a single trial.
     - Required columns: `['participant', 'task', 'trial', 'choice', 'reward']`
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

### Step 4: Structure Your Repository

Ensure your experiment folder includes the following:

- `README.md`: Includes a paper reference and link to original data.
- `original_data/`: Raw source files in their original format.
- `preprocess_data.py`: Script for standardizing raw data.
- `generate_prompts.py`: Script for creating text-based prompts.
- `prompts.jsonl.zip`: A zipped JSONL file with one line per participant. Each line should include:
  - `"text"`: Full natural language prompt with instructions, cover story and trial-by-trial data.
  - `"experiment"`: Identifier for the experiment.
  - `"participant"`: Participant ID.
  - Optional metadata fields (if available):
    - `"RTs"`: List of reaction times in ms.
    - `"age"`, `"diagnosis"`, `"nationality"`, or questionnaire-derived statistics like `"STICSA-T somatic"`.


### Submission 

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

4. On https://github.com/YOUR-USERNAME/PsychLing-101 click on "Pull requests", then "New pull request", finally "Create pull request".


### Review process

There will be a lightweight review process ensuring that requirements are fulfilled. The communication for this will be done via the corresponding pull request.


### Licensing

Data is shared under CC BY-NC-SA 4.0, with an additional restriction:

You may not use the datasets for publication or presentation purposes until the official PsychLing-101 paper is released.

All contributors and users are expected to comply.
