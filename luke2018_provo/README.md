# Reference:
Luke, S. G., & Christianson, K. (2018). The Provo Corpus: A large eye-tracking corpus with predictability norms. *Behavior Research Methods*, 50(2), 826–833. https://doi.org/10.3758/s13428-017-0908-4

# Data source:
https://osf.io/sjefs/ (released under CC BY 4.0)

Two files from the OSF project are included in `original_data/`:
- `Provo_Corpus-Eyetracking_Data.csv` — the trial-level eye-tracking data used here.
- `Provo_Corpus-Predictability_Norms.csv` — the cloze-norming study the predictability values are derived from. Included for provenance and used by `preprocess_data.py` as a consistency check.

# Description
Eye movements recorded while 84 native English speakers each read all 55 short
passages of the Provo Corpus. Passages are 2–5 sentences long (up to 62 words)
and are drawn from news articles, popular science, magazines and fiction.
Passage order was randomised per participant.

- **exp1.csv**: 230,412 rows = 84 participants × 2,743 words. One row per word
  (DataViewer interest area) per participant. Reading-time measures are total
  dwell time, first fixation duration, gaze duration and go-past time, together
  with fixation counts, first-pass skipping and regression indicators. Each word
  also carries the cloze predictability values from the accompanying norming
  study.

Participants read silently for comprehension and pressed a button to advance to
the next passage. There was no lexical decision, naming or comprehension-question
component — reading time is the only behavioural measure.

# Prompts
In `prompts.jsonl`, each passage is one trial and each word is listed with its
**total reading time (dwell time) in milliseconds** marked with `<< >>`. Words
that never received a fixation are marked `<<not fixated>>`; these account for
33.4% of words, which is typical for L1 reading. The `rt` metadata field lists
the reading times of the fixated words only.

Each participant's session is split into **two consecutive batches** of
passages, in the order the participant actually read them, with the batch number
recorded in the `batch` metadata field. A full 55-passage session comes to about
39,000 tokens, which exceeds the 32K-token budget in the contribution guide even
though it stays under the validator's 100,000-character proxy. Splitting keeps
every trial: 84 participants × 2 batches = 168 lines, each roughly 19,000–21,000
tokens. No trials are dropped.

The instructions shown in the prompts are a faithful reconstruction of the
reading task, not a verbatim transcript. The EyeLink Experiment Builder project
distributed with the corpus contains an `Instruction_screen` node, but the text
of that screen was not saved in the released files (only the 55 passage screens
and the standard EyeLink camera-setup screen are recoverable), so the original
wording is not publicly available.

# Notes
- **Source encoding.** Both original files are Windows-1252 encoded, not UTF-8;
  `preprocess_data.py` reads them as `cp1252`.
- **`stimulus` comes from `IA_LABEL`, not `Word`.** `IA_LABEL` is what was drawn
  on screen. The `Word` column originates from the norming spreadsheet and
  contains artefacts — most visibly the word "true" stored as the boolean
  `TRUE` (text 3) — as well as sentence punctuation attached to tokens. The two
  columns disagree on 1.7% of rows. Reconstructing each passage from the
  processed `stimulus` values reproduces all 55 source passages.
- **`is_fixated` is derived from `rt > 0`, not from `IA_SKIP`.** `IA_SKIP` marks
  *first-pass* skipping, so 24,759 rows have `IA_SKIP == 1` despite having been
  fixated later during a regression. Using `IA_SKIP` would mislabel those words
  as unread.
- **Structurally missing values.** `first_fixation_duration`, `gaze_duration`,
  `go_past_time`, `is_regressed_into` and `is_regressed_out_of` are empty for
  the 33.4% of words that were never fixated. These measures are undefined for
  an unfixated word rather than missing data.
- **Words without cloze norms.** 84 of each participant's 2,743 words have no
  predictability values: the 55 passage-initial words (a cloze score requires
  preceding context) plus 29 proper nouns and hyphenated compounds where the
  norming study and the interest areas tokenise differently (e.g. "Rongorongo",
  "Gaga's", "profession--writing."). The norming file itself covers 2,688 words.
- **`word_position` comes from `IA_ID`,** which is complete and contiguous
  within each passage. The source `Word_Number` column is empty for
  passage-initial words.
- **The predictability norms are not exported as a second experiment.** They are
  aggregated over norming participants (response counts and proportions per
  word, with no participant identifiers), so they are not trial-level data.
- **No participant demographics.** Age, gender and language background are not
  distributed with the corpus, so no demographic fields are included.
