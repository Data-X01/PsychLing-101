# PsychLing-101

PsychLing-101 is a community-driven effort to compile a database of psycholinguistic data. 

Our goals are:

1. Organize and make available psycholinguistic data by converting existing data into a unified, standardized format.
2. Convert psycholinguistic data into a format that can be used to fine-tune and evaluate large language models (LLMs).
3. Collaboratively produce an article describing the database to be sent to a leading psycholinguistic outlet (e.g., ACL).  

The project is led by Taisiia Tikhomirova and Dirk U. Wulff at the Center for Adaptive Rationality at the Max Planck Institute for Human Development and supported by: Valentin Kriegmair (MPI for Human Development), Fritz Günther (Humboldt University), Marco Marelli (University of Milano-Bicocca), and Marcel Binz (Helmholtz Munich). 

PsychLing-101 will be open for contributions until December 1st, 2025. Future projects may follow.

> **Current coverage** 
>
> *00* studies | *00* participants | *00* trials

---

## Participation rules

1. **Co‑authorship** – All data contributors will be co‑authors on the final paper.
2. **Immediate openness** – By contributing, you agree that the dataset becomes publicly available under the project license upon merge.
3. **Publication restrictions** – You may not publish analyses based on PsychLing‑101 data until the official paper is released.
4. **Contact first** – Open an issue or email us **before** you start working on a dataset (see below).

## Data scope and inclusion criteria

We welcome a broad range of psycholinguistic paradigms. For the list of datasets currently being processed and datasets that are open for contribution, please consult [CONTRIBUTING.md](https://github.com/Data-X01/PsychLing-101/blob/main/CONTRIBUTING.md). 

Each submission is evaluated individually, and we’re happy to discuss edge cases or special formats!
Key guidelines: 

### Scope

1. The study must primarily investigate **language processing** (e.g., lexical access, sentence comprehension, priming).
2. **Multilingual** datasets are allowed, but metadata and variable names, participant IDs, etc. must be in English.
3. **EEG/fMRI** data are welcome if exported to a row‑wise CSV format.
4. **Images** may be included; **audio/video** are not (yet) supported.

### Minimum requirements

1. Data must include raw, trial-level information (no aggregated results).
2. Data must be convertible into a structured, text‑based format.

---

# How to contribute

## 0. Check & сontact 

1. Read **CONTRIBUTING.md** to make sure no one is already processing your dataset.
2. Open a [new issue](https://github.com/Data-X01/PsychLing-101/issues/new/choose) (*or* email [psychling101@gmail.com](mailto:psychling101@gmail.com)) describing the dataset.

## 1. Fork the repository

In the upper‑right corner of the project page, click **Fork ▸ Create fork**.

## 2. Clone & create a feature branch

On your local machine create a new folder named using the format: `authorYEAR_title` (e.g., `smith2000_priming`).

```bash
# Replace YOUR‑USERNAME with your GitHub handle and <authorYEAR_title> with your folder name
# Clone your fork to the local machine
$ git clone https://github.com/YOUR-USERNAME/PsychLing-101.git

# Move into the cloned repository
$ cd PsychLing-101

# Create & switch to a feature branch named after your dataset
$ git checkout -b add_<authorYEAR_title>
```

## 3. Prepare your dataset

In Steps 3.1 – 3.4 you transform the raw files of the original_data into standardized CSVs and then generate participant-level LLM prompts.

### 3.1. Organise raw data 

1. Inside the main folder, create a subfolder named `original_data/`.
2. Place **all raw files** into `original_data/`. If your data are in a proprietary format, export them to one of the open formats before committing.

```
<authorYEAR_title>/
└──  original_data/    ← **all** raw source files (.csv, .xlsx, .mat, …)
```

### 3.2. Preprocess raw data 

1. Create a script named preprocess_data.py in the root of your experiment folder (next to original_data/).

2. Inside the script:

- Read every file inside original_data/.

- Tidy the data: rename or recode columns so they match the canonical names in [CODEBOOK.csv](https://github.com/Data-X01/PsychLing-101/blob/main/CODEBOOK.csv). If a required variable is missing, first add it to CODEBOOK.csv with a short description.

- Write one or more cleaned files (exp1.csv, exp2.csv, …) into a new folder processed_data/ folder.

```
<authorYEAR_title>/
├── original_data/        # unmodified raw files
├── preprocess_data.py    # conversion script (runs in < 60 s if possible)
├── processed_data/       # tidy CSVs (exp*.csv)
└── CODEBOOK.csv          # reference for standardized column names
```

### 3.3. Generate LLM prompts

1. In the experiment folder, create a script named `generate_prompts.py` (for the example, see [guenther2024associations_sentences_texts/generate_prompts.py](https://github.com/marcelbinz/Psych-201/blob/main/guenther2024associations_sentences_texts/generate_prompts.py)).
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

In resulting `prompts.jsonl.zip` each line should have the following three fields:
- `"text"`: Full natural language prompt with instructions, cover story and trial-by-trial data.
- `"experiment"`: Identifier for the experiment.
- `"participant"`: Participant ID.
- Optional metadata fields (if available):
   - `"RTs"`: List of reaction times in ms.
   - `"age"`, `"diagnosis"`, `"nationality"`, or questionnaire-derived statistics.
   
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

```
<authorYEAR_title>/
├── original_data/    
├── preprocess_data.py 
├── processed_data/ 
├── CODEBOOK.csv 
├── generate_prompts.py ← script for creating text-based prompts.
└── prompts.jsonl.zip ← a zipped JSONL file with prompts. 
```


### 3.4. (Optional) Images

If your dataset includes images:

1. Prepare a lower-resolution version (PNG or JPEG only; ≤ 100 KB each) of the images to minimize file size. Contact us if this limit is problematic for your stimuli. 

2. Place all relevant images into a single folder and compress them into a images.zip file.

3. In your CSV file (e.g., exp1.csv), add a column named image_filename that matches each trial’s image (e.g., apple.jpg, scene1.png).

4. In your README.md, briefly describe:

- How images were used in the experiment (e.g., as stimuli, options, or cues)

- Any preprocessing applied to reduce image resolution or format

## 4. Final folder checklist 

Before opening a pull request, confirm all of the following:

### Files present
* [ ] `README.md` with citation and data source link
* [ ] `original_data/`
* [ ] `processed_data/` (`exp1.csv`, `exp2.csv`, …)
* [ ] `CODEBOOK.csv`
* [ ] `preprocess_data.py`
* [ ] `generate_prompts.py`
* [ ] `prompts.jsonl.zip`
* [ ] *(optional)* `images.zip`

### Validation 
* [ ] `preprocess_data.py` runs without errors *from a clean repo clone*.
* [ ] Generated CSVs follow the column names in `CODEBOOK.csv`.
* [ ] `generate_prompts.py` produces `prompts.jsonl` without exceeding 32 K tokens per participant.

## 5. Commit, push & open a pull request

⚠️ Large‑file warning!
GitHub rejects individual files ≥ 100 MB unless they are stored with [Git LFS](https://git-lfs.com/). If any file in your experiment folder is ≥ 100 MB (for example images.zip), you need to track it with [Git LFS](https://git-lfs.com/). For this follow the "Optional" steps in the code snippet below. 

```bash
# Stage the entire experiment folder
$ git add <authorYEAR_title>

# OPTIONAL - command Git LFS to manage all CSV files larger than 100 MB
$ git lfs track "*.csv"

# OPTIONAL - stage the .gitattributes file Git LFS just created
$ git add .gitattributes

# Create a commit
$ git commit -m "Add <authorYEAR_title> dataset"

# Push the branch to your fork on GitHub
$ git push -u origin HEAD
```

Next, navigate to **Your fork ▸ Pull requests ▸ *Compare & pull request***. Fill in a short description and click **Create pull request**. A project maintainer will run the checks and leave comments directly in your pull requests. Small fixes can be pushed to the same branch; the pull requests updates automatically.

---

## License

This repository is shared under CC BY-NC-SA 4.0, with the following additional restrictions: You may not use the data in this repository for publication or presentation purposes until the official PsychLing-101 paper is released.

All contributors and users are expected to comply.
