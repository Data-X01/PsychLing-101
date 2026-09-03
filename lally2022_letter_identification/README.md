# lally2022_letter_identification — Letter identification in words, pseudowords and consonant strings

## Dataset

This contribution adds the letter-identification experiment of Lally and Rastle (2022) to PsychLing-101.

The study asks how orthographic knowledge and low-level visual feature information combine during letter identification. Readers identify letters more accurately inside words than inside pseudowords or unpronounceable consonant strings, and they confuse letters that share visual features (such as `n` and `h`) more often than letters that do not (such as `n` and `t`). The experiment crosses these two factors to test whether orthographic knowledge reduces the cost of visual similarity. It does not: the two effects were additive, and the orthographic effect was substantially the larger of the two.

> Lally, C., & Rastle, K. (2022). Orthographic and feature-level contributions to letter identification. *Quarterly Journal of Experimental Psychology*, 76(5), 1111–1119. https://doi.org/10.1177/17470218221106155

**Source data:** https://osf.io/p4q9u/

## Task

Reicher–Wheeler two-alternative forced choice. Each trial:

1. Fixation cross, 500 ms.
2. Forward mask (`####`) covering the letter string, 33 ms.
3. The letter string, presented at a duration calibrated individually for each participant.
4. Backward mask (`####`), 100 ms, with vertical bars marking one letter position.
5. Two candidate letters appear above and below that position. The participant indicates which letter was present, using a button box. Response window 5000 ms.

Both candidates always yield an admissible string of the same type — `snow` versus `show`, `wade` versus `wage` — so the correct answer cannot be inferred from lexical plausibility alone. No accuracy feedback was given at any point.

Exposure duration was set by a separate adaptive thresholding task run before the main experiment. Raw data from that task are not part of the OSF deposit; only the resulting per-participant value is available, stored here as `exposure_duration_ms` (33, 50, 67 or 83 ms).

## Design

3 (orthographic context: word / pseudoword / consonant string) × 2 (visual feature overlap between the two candidates: high / low), fully crossed.

48 items, each realised in all three orthographic contexts, giving 144 trials per participant. Overlap condition was assigned to items by counterbalancing list (4 lists). 72 monolingual English speakers, 10,368 trials, 1,728 observations per design cell. Mean accuracy 0.739, against a chance level of 0.5.

## Folder contents

```
lally2022_letter_identification/
├── original_data/        # Unmodified files from osf.io/p4q9u
├── preprocess_data.py    # Reads original_data/, writes processed_data/
├── processed_data/       # exp1.csv, codebook-canonical column names
├── CODEBOOK.csv          # Descriptions of the columns used here
├── generate_prompts.py   # Reads processed_data/, writes prompts.jsonl.zip
├── prompts.jsonl.zip     # One natural-language prompt per participant
└── README.md             # This file
```

### `original_data/`

Downloaded from the OSF project without modification.

- `Data & Analyses/FeatureCuesResults.csv` — trial-level results, 10,368 rows
- `Data & Analyses/FeatureCuesAnalyses.Rmd` — the authors' analysis script
- `Stimuli & Experiments/FeatureCuesStimuli.xlsx` — item list, letter-similarity matrices
- `Stimuli & Experiments/FeatureCues_ExampleScript.rtf` — DMDX script for one list
- `Stimuli & Experiments/PreliminaryThresholdingTask.rtf` — DMDX script for the thresholding task
- `Stimuli & Experiments/ExperimentalProcedure.pdf` — illustration of the trial sequence
- `OSF Supplementary Material Power Analyses.pdf`

### `processed_data/exp1.csv`

One row per trial, 10,368 rows. Produced by `preprocess_data.py`.

The results file does not contain the presented strings, the candidate letters or the participant's response. These were reconstructed as follows.

- **Stimulus, candidate letters, critical-letter position.** Joined from `FeatureCuesStimuli.xlsx` (sheet `StimuliSummary`) on item number. The target string is the `_Target` column for the trial's orthographic context; the distractor letter is taken from the `_High` or `_Low` column at the manipulated position, according to the trial's overlap condition.
- **Participant response.** Derived from accuracy. The task is a two-alternative forced choice, so a correct response identifies the target letter and an incorrect response identifies the distractor. The column carries no information beyond `accuracy`; it is included to make each trial record self-contained.
- **Reaction time.** DMDX records reaction times with a negative sign on incorrect trials. The sign was removed. The number of negative values in the source file matches the number of incorrect trials exactly.
- **`trial_id`.** Four digits encoding orthographic context, visual overlap and item number. The five-digit code used in the original data was not reused directly because its leading digit encodes the counterbalancing list, which would give the same trial different identifiers across lists. The full code is retained as `dmdx_item_code`.

The reconstruction was validated against `FeatureCues_ExampleScript.rtf`, which contains the stimulus and both candidate letters for all 144 trials of one list. All 144 reconstructed trials matched.

The join assumes that row *n* of `StimuliSummary` corresponds to item *n*. This assumption is load-bearing and is not self-evident from the file, so `preprocess_data.py` verifies a fingerprint of the ordered target strings and fails loudly if the sheet is reordered.

### `prompts.jsonl.zip`

One JSON object per line, one line per participant. Fields: `text`, `experiment`, `participant_id`, `rt`, `exposure_duration_ms`.

Prompt template:

```
[the eleven instruction lines, verbatim]

In this session each letter string was shown for {exposure_duration_ms} ms.

Trial {n}: The letter string was '{stimulus}'. The letters '{option_a}' and '{option_b}'
appeared above and below the {ordinal} position. You press <<{response}>>. RT: <<{rt}>> ms.
```

Both quantities the experiment measured are marked with `<< >>`: the letter the participant chose and the time they took to choose it, following the lexical-decision contributions such as `hutchison2013_semantic`, which mark the response and the reaction time on the same trial line.

The individually calibrated exposure duration is stated on its own line between the instruction and the first trial, rather than written into the instruction, because the original instruction screen never mentions it and that screen is reproduced unaltered. This follows the convention set out in `schiekiera2026_pwi_en/generate_prompts.py`: parameters that are constant within a session belong to the instruction block instead of being repeated on every trial line.

The presented string is given in full, because the prompt transcribes the display rather than the participant's perception of it: the string really was shown, and that it went by too fast to read is a fact about the reader, not the screen. One consequence is worth stating plainly: reading the string off the page is easy, so a prompt reproduces the stimulus and the response but not the perceptual difficulty the participant faced at a threshold exposure under masking. The visual-similarity manipulation likewise has no textual counterpart.

Two decisions were needed to render this task in text.

**No feedback is included.** The experiment script sets `<nfb>`; participants were never told whether a response was correct.

**Option order is randomised per participant.** Which candidate appeared above and which below is not recorded in the results file. It is recoverable only for the single list whose DMDX script is included in the deposit, so the true order cannot be preserved for most participants. Randomising the order also satisfies the contribution guide's requirement to randomise option naming in discrete-choice tasks.

The instruction lines are reproduced verbatim from the experiment script, down to punctuation and capitalisation, and including the references to the button box and the spacebar, so that the prompt describes the situation the participant was actually in. The blank lines between them are the one thing not taken from the file. The script holds eleven quoted strings whose vertical placement on screen is set by DMDX `<ln>` markers; rows `-3` and `5` are left unoccupied, which puts a blank line after the second and after the ninth line. The paragraph breaks are therefore inferred from that screen geometry rather than read off the file, while the text of the lines is unaltered. Exposure duration is not part of the screen and is not added to it; it travels with each record as the `exposure_duration_ms` field instead.

## Reproducing the processing

From inside the `lally2022_letter_identification/` folder:

```bash
python preprocess_data.py     # original_data/ -> processed_data/exp1.csv
python generate_prompts.py    # processed_data/ -> prompts.jsonl.zip
```

Both scripts use relative paths and require only `pandas` and `openpyxl` beyond the standard library. `preprocess_data.py` runs in under two seconds and validates its output before writing.

## Licence

The OSF project is public but has no licence field set. The article is published under CC BY 4.0. The stimuli are English words, pronounceable pseudowords and consonant strings, and contain no copyrighted material. Please cite the paper above when using this contribution.
