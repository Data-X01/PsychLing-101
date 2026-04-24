# Reference:
Frank, S.L., Fernandez Monsalve, I., Thompson, R.L., & Vigliocco, G. (2013). Reading-time data for evaluating broad-coverage models of English sentence processing. *Behavior Research Methods*, 45, 1182–1190.

# Data source:
https://link.springer.com/article/10.3758/s13428-012-0313-y (supplementary materials)

# Description
Two psycholinguistic studies on English sentence reading.

- **exp1.csv**: Self-paced reading (SPR). 117 participants read 362 sentences one word at a time by pressing a button. Word-level reading times (ms) are recorded. After some sentences, a yes/no comprehension question was presented.
- **exp2.csv**: Eye-tracking (ET). 43 participants (17 monolingual, 26 multilingual) read 205 sentences (the 205 shortest sentences from the full set). Unlike SPR, each sentence was displayed in full on the screen and participants read at their own natural pace, with eye movements tracked by SR Research EyeLink II (500 Hz). Participants pressed a mouse button to advance to the next sentence; yes/no comprehension questions were answered via left/right mouse buttons. Four word-level reading time measures are recorded: first fixation, first-pass, right-bounded, and go-past. A fixation time of 0 indicates the word was not fixated before a later word was fixated first; these are stored as NaN in the processed data.

# Prompts
In `prompts.jsonl`, reading times are marked with `<< >>`. The `rt` field used in prompts corresponds to:
- **exp1 (SPR)**: key-press reaction time (ms) per word.
- **exp2 (ET)**: first fixation duration (ms) per word — the duration of only the first fixation on that word. Words that were not fixated (i.e., the participant's eyes moved past the word without landing on it) are recorded as `<<not fixated>>`. Note that exp2.csv also contains three additional eye-tracking measures (first-pass, right-bounded, go-past); see CODEBOOK.csv for definitions.

# Notes
- Three typos found after SPR data collection were corrected in the ET stimuli (sentences 43, 269, 337). The original (uncorrected) sentences are used in exp1.csv; the corrected versions are used in exp2.csv.
- ET participant #20 scored only 14.5% correct on comprehension questions, likely due to confusion about response buttons. This participant is retained in exp2.csv but flagged via the raw accuracy value.
- `first_language` is coded as "English" for native speakers (age_en == 0) and left as NaN for non-native speakers (native language not recorded in original data).
