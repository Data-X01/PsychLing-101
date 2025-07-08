# PsychLing-101

PsychLing-101 is a community-driven effort to compile a database of psycholinguistic data. 

Our goals are:

1. Organize and make available psycholinguistic data by converting existing data into a unified, standardized format.
2. Convert psycholinguistic data into a format that can be used to fine-tune and evaluate large language models (LLMs).
3. Collaboratively produce an article describing the database to be sent to a leading psycholinguistic outlet (e.g., ACL).  

The project is led by Taisiia Tikhomirova and Dirk U. Wulff at the Center for Adaptive Rationality at the Max Planck Institute for Human Development and supported by: Valentin Kriegmair (MPI for Human Development), Fritz Günther (Humboldt University), Marco Marelli (University of Milano-Bicocca), and Marcel Binz (Helmholtz Munich). 

PsychLing-101 will be open for contributions until December 1st, 2025. Future projects (PsychLing-201, PsychLing-301) may follow.

> **Current coverage** 
>
> *XX* studies | *XX* participants | *XX* trials

---

## Participation Rules

1. **Co‑authorship** – All data contributors will be co‑authors on the final paper.
2. **Immediate openness** – By contributing, you agree that the dataset becomes publicly available under the project license upon merge.
3. **Publication restrictions** – You may not publish analyses based on PsychLing‑101 data until the official paper is released.
4. **Contact first** – Open an issue or email us **before** you start working on a dataset (see below).

---

## Data Scope and Inclusion Criteria

We welcome a broad range of psycholinguistic paradigms. Each submission is evaluated individually, and we’re happy to discuss edge cases or special formats!
Key guidelines:

### Scope

1. The study must primarily investigate **language processing** (e.g., lexical access, sentence comprehension, priming).
2. **Multilingual** datasets are allowed, but metadata and variable names, participant IDs, etc. must be in English.
3. **EEG/fMRI** data are welcome if exported to a row‑wise CSV format.
4. **Images** may be included; **audio/video** are not (yet) supported.

### Minimum Requirements

1. Data must include raw, trial-level information (no aggregated results).
2. Data must be convertible into a structured, text‑based format (handled by your `preprocess_data.py`).

For the list of datasets currently being processed and datasets that are open for contribution, please consult [CONTRIBUTING.md](https://github.com/Data-X01/PsychLing-101/blob/main/CONTRIBUTING.md).

---

## How to Contribute

### 0. Check & Contact

1. Read **CONTRIBUTING.md** to make sure no one is already processing your dataset.
2. Open a [new issue](https://github.com/Data-X01/PsychLing-101/issues/new/choose) *or* email [psychling101@gmail.com](mailto:psychling101@gmail.com) describing the dataset.

### 1. Fork the Repository

1. In the upper‑right corner of the project page, click **Fork ▸ Create fork**.
2. Enable **Git LFS** on your fork if you plan to add large files (>100 MB).

### 2. Clone & Create a Feature Branch

Create a new folder named using the format: `authorYEAR_title` (e.g., `smith2000_priming`).

```bash
# Replace YOUR‑USERNAME with your GitHub handle and <authorYEAR_title> with your folder name
$ git clone https://github.com/YOUR-USERNAME/PsychLing-101.git
$ cd PsychLing-101
$ git checkout -b add_<authorYEAR_title>
```

### 3. Organize Raw Data

1. Inside the main folder, create a subfolder named `original_data/`.
2. Place **all raw files** from the source (e.g., OSF, repositories) into `original_data/`. Supported formats include `.csv`, `.tsv`, `.xlsx`, `.mat`, and `.json`.

```
<authorYEAR_title>/
└──  original_data/    ← **all** raw source files (.csv, .xlsx, .mat, …)
```
4. If raw data exceeds GitHub's file size limit, use [Git LFS](https://git-lfs.com/) to store and track these files.

```bash
$ git lfs track "*.csv"
```

### 4. Preprocess Raw Data 

Convert the raw files in original_data/ into clean, trial‑level CSVs stored in processed_data/.

1. Create a script named preprocess_data.py in the root of your experiment folder (i.e., next to original_data/).

2. Inside the script:

- Read every file inside original_data/ (e.g., using Path.glob("*")).

- Tidy the data: rename or recode columns so they match the canonical names in CODEBOOK.csv.If a required variable is missing, first add it to CODEBOOK.csv with a short description.

- Write one or more cleaned files (exp1.csv, exp2.csv, …) into a new folder called processed_data/.

```
<authorYEAR_title>/
├── original_data/        # unmodified raw files
├── preprocess_data.py    # conversion script (runs in < 60 s if possible)
├── processed_data/       # tidy CSVs (exp*.csv)
└── CODEBOOK.csv          # reference for standardized column names
```

### 5. Generate LLM Prompts

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
└── prompts.jsonl.zip ← a zipped JSONL file with promts. 
```


### 6. (Optional) Images

If your dataset includes images:

1. Prepare a lower-resolution version of the images to minimize file size.

2. Place all relevant images into a single folder and compress them into a images.zip archive.

3. Add the archive to your main experiment folder. If the zipped file exceeds GitHub’s size limit, use Git LFS to track and store it.

4. In your CSV file (e.g., exp1.csv), add a column named image_filename that matches each trial’s image (e.g., apple.jpg, scene1.png).

5. In your README.md, briefly describe:

- How images were used in the experiment (e.g., as stimuli, options, or cues)

- Any preprocessing applied to reduce image resolution or format

### 7. Final folder Checklist

Now your folder should cosist from: 

* [ ] `README.md` with citation and data source link
* [ ] `original_data/`
* [ ] `processed_data/` (`exp1.csv`, `exp2.csv`, …)
* [ ] `CODEBOOK.csv`
* [ ] `preprocess_data.py`
* [ ] `generate_prompts.py`
* [ ] `prompts.jsonl(.zip)`
* [ ] *(optional)* `images.zip`

### 8. Commit & Push

```bash
$ git add <authorYEAR_title>
$ git commit -m "Add <authorYEAR_title> dataset"
$ git push -u origin HEAD
```

### 9. Open a Pull Request

1. Navigate to **Your fork ▸ Pull requests ▸ *Compare & pull request***.
2. Fill in a short description; the PR template will remind you of the checklist above.

### 10. Review Process

A project maintainer will run the checks and leave comments directly in your PR.  Small fixes can be pushed to the same branch; the PR updates automatically.

---

## Pre‑Submission Validation Checklist

Before opening your pull request, double‑check that:

* [ ] All required files are present (see Section 7).
* [ ] `preprocess_data.py` runs without errors *from a clean repo clone*.
* [ ] Generated CSVs follow the column names in `CODEBOOK.csv`.
* [ ] `generate_prompts.py` produces `prompts.jsonl` without exceeding 32 K tokens per participant.
* [ ] No file larger than 100 MB is committed without Git LFS.
---

## License

This repository is shared under CC BY-NC-SA 4.0, with the following additional restrictions: You may not use the data in this repository for publication or presentation purposes until the official PsychLing-101 paper is released.

All contributors and users are expected to comply.
