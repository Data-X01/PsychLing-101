# ferrand2018_megalex — MEGALEX, French visual lexical decision

This folder contains the standardized preprocessing scripts and LLM prompts for the **visual lexical decision** part of MEGALEX, contributed to the PsychLing-101 database. The auditory part of the megastudy is not included.

## Citation
Ferrand, L., Méot, A., Spinelli, E., New, B., Pallier, C., Bonin, P., Dufau, S., Mathôt, S., & Grainger, J. (2018). MEGALEX: A megastudy of visual and auditory word recognition. *Behavior Research Methods*, 50(3), 1285–1307. https://doi.org/10.3758/s13428-017-0943-1

## Data Source
OSF project of the authors: [https://osf.io/7z6th/](https://osf.io/7z6th/), folder *MEGALEX Word data trial-by-trial Visual + Auditory*, archive `By trials Auditory & Visual-MEGALEX.zip`.

## Task
Visual lexical decision in French, run in OpenSesame. Participants decided, as quickly and as accurately as possible, whether a letter string (lowercase, centre of the screen) was a French word or a pseudoword, using a Logitech gamepad: "yes" (word) with the right index finger, "no" (pseudoword) with the left index finger.

Trial sequence (article, Method): a fixation point (".") for 250 ms, a blank screen for 100 ms, then the letter string, which stayed on screen until a response or for 2 s at most, followed by a 1,000-ms blank intertrial interval. There was no feedback after individual trials. At the end of each block participants saw their mean correct reaction time and percentage of errors for words.

Each block was preceded by ten practice trials. A session normally consisted of two blocks with a short break between them, and after each block participants could choose to continue or stop. After a one-hour startup session in the lab (40 practice trials and the first session), participants booked sessions at their own pace; completing the experiment took 15 to 58 days.

## Design
96 participants finished the visual experiment (right-handed native speakers of French; age 17–52 across both modalities of the study). The item set is 28,466 French words and as many pseudowords; each participant saw exactly half of it, in a random order split into 109 blocks of 260 positions (130 words and 130 pseudowords per block). Each word was seen by about 46 participants.

| | trials | unique strings | accuracy | median RT (ms) |
|---|---|---|---|---|
| word | 1,311,832 | 28,466 | 0.889 | 567 |
| pseudoword | 1,284,263 | 27,843 | 0.927 | 620 |

## Folder contents

```
ferrand2018_megalex/
├── original_data/        # Author files, unmodified
├── preprocess_data.py    # Reads original_data/, writes processed_data/exp1.csv
├── processed_data/       # exp1.csv, codebook-canonical column names
├── CODEBOOK.csv          # Descriptions of the columns used here
├── generate_prompts.py   # Reads processed_data/, writes prompts.jsonl.zip
├── prompts.jsonl.zip     # Natural-language prompts, several per participant
└── README.md             # This file
```

### `original_data/`
Extracted without modification from `By trials Auditory & Visual-MEGALEX.zip`:

- `Visual.WpuispW.essais_ElTec.txt` — trial-level visual lexical decision data, words and pseudowords, 2,596,095 rows. Semicolon-separated; the header names 9 columns but every row has 10 fields, the first one being an unnamed row index written by R.
- `infos_variables.txt` — the authors' short description of the columns (in French; renamed from "Infos sur libellés variables.txt", which contains spaces).

### `processed_data/exp1.csv`
One row per trial, 2,596,095 rows, sorted by participant and presentation order. Produced by `preprocess_data.py` (about 10 s).

| column | original column | notes |
|---|---|---|
| `participant_id` | `subject` | |
| `trial_id` | `numinit` | unique across the file, increases with presentation order within a participant, not contiguous |
| `trial_order` | — | 0-indexed presentation order, derived by sorting each participant's trials on `numinit` |
| `phase_id` | `block` | 1–109 |
| `trial_in_block` | `trial_num_block` | position within the block, 1-indexed; starts at 11 (see below) |
| `stimulus_type` | `category` | `w` → `word`, `p` → `pseudoword` |
| `stimulus` | `target` | |
| `response` | — | derived, see below |
| `accuracy` | `correct` | 1 = correct |
| `rt` | `rt` | ms, unchanged |
| `repetition` | `repetition` | unchanged, see below |

## Author-side preprocessing vs. this repository
The author file already has 3,939 trials with technical problems removed, which leaves 2,596,095 trials. The article removes more trials before analysis:

| step | trials removed | remaining |
|---|---|---|
| trials in the author file | | 2,596,095 |
| RT < 300 ms or > 2,000 ms | 8,658 | 2,587,437 |
| 3 participants (1004, 1005, 1006) with mean accuracy below 80% | 73,272 | 2,514,165 |
| 8 blocks with accuracy below 75% | 1,981 | **2,512,184** (as reported in the article) |

**None of these exclusions is applied here.** `exp1.csv` and the prompts contain all 2,596,095 trials, so users can apply the authors' criteria or their own. All three steps can be reproduced exactly from `exp1.csv`, applied in the order above:

1. `rt < 300` or `rt > 2000`: 8,655 + 3 = 8,658 trials.
2. Participants 1004, 1005, 1006: 80,423 trials, of which 7,151 were already removed in step 1, leaving 73,272. The article does not name these participants; they are the three absent from the authors' separate pseudoword file (`vp.essais_ElTec&Seuils.txt` on OSF) and give exactly the reported count.
3. Blocks whose accuracy, computed on the trials left after steps 1–2, is below 0.75: 8 blocks, 1,981 trials (participant 1008 blocks 8–9; 1019 blocks 103, 105–108; 1088 block 89). Computed before step 1, the same criterion gives 9 blocks instead.

## Notes
- **Instruction is reconstructed.** The original instruction text is not part of the OSF deposit. The instruction in the prompts is reconstructed from the Method section of the article, with the participant's randomised button labels in place of the gamepad buttons.
- **`response` is derived.** The data file records accuracy but not which button was pressed. In a two-choice task the response follows from the stimulus type and accuracy: word & correct → `word`, word & incorrect → `nonword`, pseudoword & correct → `nonword`, pseudoword & incorrect → `word`.
- **Responses at the 2 s deadline.** The letter string was removed after 2 s without a response. The RT distribution shows no pile-up at 2,000 ms, so timed-out trials are evidently not in the author file. Three trials have RT > 2,000 ms. Two of them are correct (participant 1005, 2,015.9 ms; participant 1055, 2,007.4 ms), which a timeout cannot be, so they are late presses and keep their derived response. The third is incorrect with RT 2,000.01 ms, the deadline itself (participant 1006, `trial_id` 151696): it is probably a timeout, so its `response` is left empty and the prompt shows `<<nothing>>`. `accuracy` and `rt` are kept as recorded.
- **Positions 1–10 of each block are practice trials.** In almost every block the recorded `trial_in_block` values start at 11 and run to 260 (to 100 in the last block of most participants). This matches the ten practice trials that preceded each block; they are not in the author file. `trial_in_block` is kept as recorded, and the prompts number trials by it.
- **`repetition` is not documented by the authors.** Their column description leaves it blank. It is 1 on 1,029 trials (937 pseudoword, 92 word trials, 45 distinct strings) and 0 otherwise. In this file every second presentation of the same string to the same participant (990 trials) has `repetition = 1`; the remaining 39 flagged trials are the only presentation of their string to that participant left in the file, so their first presentation was probably among the trials removed for technical problems. The column is kept unchanged.
- **Not included:** the OSF project also contains the auditory lexical decision data (trial-level and item-level), separate pseudoword trial files for both modalities, item-level tables for visual and auditory words (`vw.ParItems.DVandIV.txt`, `aw.ParItems.DVandIV.txt`), and the audio files of the auditory pseudowords. None of them is part of this contribution.

## Prompts
`generate_prompts.py` writes `prompts.jsonl.zip` (about 25 s). A session of ~27,000 trials is far above the 32K-token limit, so each participant's session is split into chunks of 5 consecutive blocks (blocks 1–5, 6–10, …, 106–109), 2,112 prompts in total. Every chunk opens with the instruction and states which blocks it covers.

Fields: `text`, `experiment` (`ferrand2018_megalex/exp1`), `participant_id`, `blocks` (the block numbers in the chunk) and `rt` (one value per trial, in prompt order). `participant_id` is the participant's identifier and therefore repeats across that participant's chunks, as in `balota2007_LDT` and other chunked datasets in the repository; `blocks` tells the chunks apart.

The prompts follow the procedure of the experiment:

- **No feedback after a trial.** Each trial line gives the letter string and the button pressed, and nothing else.
- **Feedback at the end of each block.** After the last trial of a block the prompt shows the feedback screen: mean reaction time for correct responses to words and percentage of errors on words. These values are **recomputed from the recorded trials of the block**; the values actually displayed are not in the data. They can differ from what participants saw: trials removed by the authors for technical problems are missing from the computation, and the exact formula and display format of the original screen are not documented. The article's wording ("mean correct reaction times and percentage of errors for words") is read as applying to word trials for both values.
- **Trial numbers are positions in the block** (`trial_in_block`), so each block starts at trial 11 after the ten unrecorded practice trials, and a trial removed by the authors leaves a gap in the numbering.
- **Button labels** are two distinct capital letters drawn per participant, from a seed derived from the participant identifier, so they are the same in all chunks of one participant and the archive is reproduced byte for byte on re-running. Only the participant's button press is wrapped in `<< >>`.

```
In this experiment you will see letter strings presented one at a time in the centre of the screen. [...] Press F for a real word and E for a pseudoword. [...]

The trials below are from blocks 1-5 of the experiment. Each block begins with ten practice trials, which were not recorded; trials are numbered by their position in the block.

Block 1:
Trial 11: The letter string is 'haboua'. You press <<E>>.
Trial 12: The letter string is 'toquée'. You press <<E>>.
Trial 13: The letter string is 'empêche'. You press <<F>>.
[...]
Trial 260: The letter string is 'entrant'. You press <<E>>.
End of block 1. Mean reaction time for correct responses to words: 622 ms. Errors on words: 9.1%.

Block 2:
[...]
```

Largest prompt: 76,281 characters, 23,888 tokens with tiktoken `cl100k_base` and 25,895 with the Qwen2.5 tokenizer. Six blocks per chunk would reach 31,016 Qwen2.5 tokens, too close to the limit. The script checks every prompt against 32,000 tokens and against the 100,000-character limit of `scripts/validate_submission.py`, using tiktoken when it is installed and a conservative estimate otherwise.

## License
TODO: no license on OSF; requested from the authors.
