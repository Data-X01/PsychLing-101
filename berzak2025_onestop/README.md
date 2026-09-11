# Reference:
Berzak, Y., Malmaud, J., Shubi, O., Meiri, Y., Lion, E., & Levy, R. (2025). OneStop: A 360-Participant English Eye Tracking Dataset with Different Reading Regimes. *Scientific Data*, 12. https://doi.org/10.1038/s41597-025-06272-2

# Data source:
https://osf.io/2prdq/ (released under CC BY 4.0)

`original_data/` contains:
- `ia_Paragraph.csv.zip` — the Interest Area Report for paragraph reading across all four reading regimes, exactly as distributed in the OneStop All Regimes component.
- `session_summary.csv` — per-participant session statistics from the OneStop Metadata component, used here for comprehension and LexTALE scores.

# Description
Eye movements recorded with an EyeLink 1000 Plus while 360 native English
speakers read Guardian article paragraphs and answered a multiple-choice
comprehension question about each one. Each participant read 10 articles
paragraph by paragraph, then read two of those articles a second time. Half the
participants saw the comprehension question before reading each paragraph.

The dataset is split here by the reading-goal manipulation, which is its primary
contrast.

- **exp1.csv**: ordinary reading for comprehension. 180 participants, 1,266,284
  rows, 11,662 trials (9,718 first readings and 1,944 repeated readings).
- **exp2.csv**: information seeking, where the question was shown before the
  paragraph. 180 participants, 1,266,515 rows, 11,664 trials (9,720 first
  readings and 1,944 repeated readings).

One row is one word (interest area) read by one participant on one trial.
Paragraphs came in two versions, the original Guardian text (`Adv`) and a
simplified rewrite (`Ele`), and each has three possible comprehension questions,
giving 486 questions in total.

The trial counts match those published by the authors exactly, 19,438 first
readings and 3,888 repeated readings. The row counts plus the 99,360 practice
rows dropped here come to 2,632,159, the published number of recorded paragraph
word tokens.

# Prompts
In `prompts.jsonl`, each paragraph is one trial. Words are listed with the
**total reading time (dwell time) in milliseconds** marked with `<< >>`, and
words that never received a fixation are marked `<<not fixated>>`. The
comprehension question and its four answer options follow, with the option the
participant chose marked with `<< >>` and the feedback they received after it.
The `rt` metadata field lists the reading times of the fixated words only.

Trial layout follows the reading regime. In exp2 the question appears before the
paragraph as well as after it, matching the question preview page those
participants saw; in exp1 it appears only after.

Answers were displayed in a cross arrangement and selected with the four
directional buttons of a gamepad, not with named keys, so each participant is
assigned **four random letters**, one per on-screen answer position. All 360
participants receive distinct key sets and the draw is seeded for
reproducibility. Answer options are listed in the order they appeared on screen,
which the experiment randomised per trial and which is preserved in the
`answer_options` column.

Each session is split into **five consecutive batches** of trials, with the
batch number in the `batch` metadata field. A participant read about 65
paragraphs totalling roughly 7,000 words, far beyond the 32K-token budget in the
contribution guide. Five batches keeps the longest line at about 27,000 tokens.
No trials are dropped. 360 participants give 1,800 lines.

The instructions are a faithful reconstruction of the task rather than a
verbatim transcript. The paper reports that participants "were instructed to
read silently and to minimize head movement" and that the experiment opened with
two instruction pages, but the text of those pages is not published.

# Notes
- **Practice trials are excluded.** The authors describe the dataset as 19,438
  regular and 3,888 repeated-reading trials, which are the trials kept here.
  99,360 practice word rows were dropped.
- **Repeated readings are kept and flagged** in `is_repeated_reading`, so first
  and second readings can be separated or analysed together.
- **Answer options are stored once per trial.** The four options are joined
  into a single `answer_options` column, in the order they appeared on screen,
  on the row where `word_position` is 1, and are empty on the remaining rows of
  that trial. Repeating the option text on all 2.5 million word rows would have
  added several hundred MB of duplicated text. The question itself is carried on
  every row.
- **Derived annotations are not carried over.** The source report ships
  precomputed word frequency, GPT-2 surprisal, part-of-speech tags and
  dependency parses. These are model or corpus derived rather than observed, and
  are recomputable from the stimulus text, so they are dropped to keep the
  processed files to the measured data.
- **`is_fixated` is derived from `rt > 0`, not from `IA_SKIP`,** which marks
  first-pass skipping only. A first-pass skipped word may still have been
  fixated later during a regression.
- **Structurally missing values.** `first_fixation_duration`, `gaze_duration`,
  `go_past_time` and the regression columns are empty for words that were never
  fixated, where those measures are undefined rather than missing.
- **LexTALE scores are sparse in the source.** 260 of the 360 participants have
  no LexTALE score in `session_summary.csv`, so the column is empty for them.
- **Source size.** `ia_Paragraph.csv` is 5.6 GB uncompressed with 157 columns.
  `preprocess_data.py` streams it from the zip rather than loading it, and runs
  in about 90 seconds.
- **Expected validator warning.** The submission checker compares processed row
  counts against the CSVs in `original_data/` and reports a large expansion.
  This is expected, since the eye-tracking data sits inside `ia_Paragraph.csv.zip`
  and only `session_summary.csv`, which has one row per participant, is visible
  to that check.
