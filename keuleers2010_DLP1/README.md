# keuleers2010_DLP1 — Dutch Lexicon Project 1

## Dataset

This contribution adds the **Dutch Lexicon Project 1 (DLP1)** to PsychLing-101.

In DLP1, 39 Dutch-speaking participants performed a visual lexical decision task on 14,089 mono- and disyllabic Dutch words and the same number of length- and structure-matched nonwords (28,178 stimuli total). Each participant responded to *every* stimulus across 58 blocks of 500 trials, distributed over multiple sessions, for a total of roughly 16–17 hours per participant. Block 1 was repeated as block 50 to assess long-term practice effects.

The original dataset and full procedural description can be found in:

> Keuleers, E., Diependaele, K., & Brysbaert, M. (2010). Practice effects in large-scale visual word recognition studies: A lexical decision study on 14,000 Dutch mono- and disyllabic words and nonwords. *Frontiers in Psychology*, 1, 174. https://doi.org/10.3389/fpsyg.2010.00174

**Source data:** https://osf.io/uw7t6/

## Task

Each trial:

1. Two short vertical fixation lines appear above and below the centre of the screen.
2. After 500 ms, a letter string is shown in lowercase between the lines.
3. The participant decides as quickly and accurately as possible whether the letter string is a real Dutch word or a nonword.
4. The stimulus disappears upon response or after a 2,000 ms timeout, followed by a 500 ms blank inter-trial interval.

Word responses were given with the dominant hand, nonword responses with the non-dominant hand, on an external response box. Participants were instructed to keep their accuracy above 85%.

## Folder contents

```
keuleers2010_DLP1/
├── original_data/        # Raw DLP1 files from osf.io/uw7t6
├── preprocess_data.R     # Reads original_data/, writes processed_data/
├── processed_data/       # Tidy CSVs with codebook-canonical column names
├── generate_prompts.R    # Reads processed_data/, writes prompts.jsonl
├── prompts.jsonl         # One natural-language prompt per participant
├── prompts.jsonl.zip     # Compressed copy of prompts.jsonl
└── README.md             # This file
```

### `original_data/`

Raw files downloaded from the OSF mirror of the project. The DLP1 authors distribute the data in three open formats; all are kept here for accessibility:

- `dlp-items.{Rdata,txt,xls}` — item-level aggregate (one row per stimulus)
- `dlp-trials.txt.zip`, `dlp-trials.Rdata` — full trial-level data (≈1.1M rows)
- `dlp-trials-block-50.{Rdata,txt}` — trial-level data from block 50 only (19,500 rows)
- `dlp-stimuli.{Rdata,txt,xls}` — stimulus characteristics

**Note on file sizes:** The unzipped full trial-level file (`dlp-trials.txt`) was 107 MB, exceeding GitHub's 100 MB per-file limit, so only the compressed version (`dlp-trials.txt.zip`, 38 MB) is included. The data are identical; users only need to unzip to access them.

### `processed_data/`

Produced by `preprocess_data.R`. Columns are renamed to match `CODEBOOK.csv`:

- **`exp1.csv`** — trial-level data from block 50 (19,500 rows)
  Columns: `participant_id`, `trial_id`, `trial_order`, `phase_id`, `stimulus`, `condition` (word/nonword), `response` (word/nonword), `accuracy` (0/1), `rt` (ms)
- **`exp1_items.csv`** — item-level aggregate (~28k rows)
  Columns: `stimulus`, `condition`, `rt` (mean), `accuracy` (mean)

We use **block 50** as the basis for the trial-level standardized output. The original authors note that practice effects are minimal, but block 50 represents responses *after* practice has stabilized and is an appropriate slice for evaluating language-model trial-by-trial behaviour. Including the full ~1M-row dataset would inflate prompt sizes well past the 32K token budget per participant.

### `prompts.jsonl(.zip)`

Produced by `generate_prompts.R`. One JSON object per line, one line per participant. Fields:

- `text` — Full natural-language prompt: original-style instructions followed by trial-by-trial replay. The participant's response key is wrapped in `<< >>`.
- `experiment` — `"keuleers2010_DLP1"`
- `participant_id` — Integer ID matching the original DLP1 numbering
- `rt` — List of reaction times (ms) corresponding to the trials included in `text`

Per the contribution guide, the response keys (`"a"` and `"l"`) are **randomly assigned per participant** to discourage models from relying on a memorized key mapping. Each prompt covers ~500 trials from block 50 and stays under ~10,400 tokens (well below the 32K cap).

## Reproducing the processing

From inside the `keuleers2010_DLP1/` folder:

```r
Rscript preprocess_data.R       # original_data/ -> processed_data/
Rscript generate_prompts.R      # processed_data/ -> prompts.jsonl(.zip)
```

Both scripts run in well under 60 seconds on a modern laptop and require only `readr`, `dplyr`, and `jsonlite`. Missing packages are installed automatically on first run.

## Licence

The original DLP1 data are released by Keuleers, Diependaele, and Brysbaert (2010) for unrestricted research use. Please cite the paper above when using this contribution.
