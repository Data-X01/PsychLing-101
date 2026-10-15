# Reference:
Wave 1: Siegelman, N., Schroeder, S., Acartürk, C., Ahn, H.-D., Alexeeva, S., Amenta, S., … Kuperman, V. (2022). Expanding horizons of cross-linguistic research on reading: The Multilingual Eye-movement Corpus (MECO). *Behavior Research Methods*, 54(6), 2843–2863. https://doi.org/10.3758/s13428-021-01772-6

Wave 2: Siegelman, N., Schroeder, S., Bao, Y. B., Acartürk, C., Agrawal, N., Bolliger, L. S., … Kuperman, V. (2025). Wave 2 of the Multilingual Eye-Movement Corpus (MECO): New text reading data across languages. *Scientific Data*, 12, 1183. https://doi.org/10.1038/s41597-025-05453-3

# Data source:
https://osf.io/3527a/ (MECO L1), **release 2.0, version 2.1** (2026-02-19). The project's own recommendation is to use the most recent release and version. The earlier versions on the same page (release 1.0, versions 1.0–1.3, and release 2.0, version 2.0) are not used.

**License.** The OSF node record of https://osf.io/3527a/ gives the license as CC BY 4.0 (CC-By Attribution 4.0 International, 2025). The downloaded archive itself contains no license file and none of its readme files mentions a license or terms of use; they ask only that the Wave 1 and Wave 2 papers above be cited.

`original_data/` contains these files, unmodified, from release 2.0 / version 2.1:

| file here | path in the OSF archive |
|---|---|
| `wave1/joint_l1_data_trimmed_version2.1.rda` | `release 2.0/version 2.1/wave 1/primary data/eye tracking data/` |
| `wave1/00_readme_variables.txt` | same folder |
| `wave1/supp_texts.csv` | `release 2.0/version 2.1/wave 1/auxiliary files/reading task materials/` |
| `wave2/joint_data_trimmed_wave2_version2.1.rda` | `release 2.0/version 2.1/wave 2/primary data/eye tracking data/` |
| `wave2/00_readme_variables.txt` | same folder |
| `wave2/supp_texts_wave2.xlsx` | `release 2.0/version 2.1/wave 2/auxiliary files/reading task materials/` |

The two `.rda` files are the word-level (interest-area) eye-tracking reports. The texts files are the reading materials, used by `preprocess_data.R` to identify which text each trial shows (see below).

# Description
MECO L1 is an eye-tracking corpus of text reading in the participants' first language, collected with the same materials, task template (SR Research Experiment Builder, EyeLink trackers) and processing pipeline (popEye) at many sites. Each participant read 12 short encyclopedic texts, one per screen, silently for comprehension, and pressed the space bar when done; each text was followed by four yes/no comprehension questions. The 12 topics are the same in every language (Janus, the shaka sign, doping, the thylacine, World Environment Day, the monocle, wine tasting, orange juice, beekeeping, national flags, the International Union for Conservation of Nature, vehicle registration plates). Some texts are matched translations across languages and others were written separately per language on the same topic (see the papers).

- **exp1.csv**: Wave 1. 580 participants in 13 samples, 855,462 rows, 5,240 texts read.
- **exp2.csv**: Wave 2. 654 participants in 16 samples, 978,811 rows, 5,605 texts read. Wave 2 also records the order in which the texts were presented (`trial_order`); Wave 1 does not (see Notes).

One row is one word (interest area) of one text read by one participant. Words that were never fixated are kept, with reading time 0 (see Notes).

| wave | lab | first_language | participants | rows |
|---|---|---|---|---|
| 1 | du | Dutch | 45 | 67,595 |
| 1 | ee | Estonian | 52 | 60,130 |
| 1 | en | English | 46 | 84,610 |
| 1 | fi | Finnish | 49 | 66,151 |
| 1 | ge | German | 45 | 75,631 |
| 1 | gr | Greek | 45 | 61,578 |
| 1 | he | Hebrew | 47 | 66,381 |
| 1 | it | Italian | 54 | 86,960 |
| 1 | ko | Korean | 32 | 35,585 |
| 1 | no | Norwegian | 42 | 63,291 |
| 1 | ru | Russian | 46 | 68,331 |
| 1 | sp | Spanish | 48 | 87,275 |
| 1 | tr | Turkish | 29 | 31,944 |
| 2 | ba | Basque | 39 | 42,964 |
| 2 | bp | Portuguese (Brazil) | 56 | 89,457 |
| 2 | ch_s | Chinese (simplified script) | 39 | 56,461 |
| 2 | ch_t | Chinese (traditional script) | 38 | 51,931 |
| 2 | da | Danish | 28 | 36,212 |
| 2 | en_uk | English (UK sample) | 50 | 84,364 |
| 2 | ge_po | German (Potsdam sample) | 40 | 54,903 |
| 2 | ge_zu | German (Zurich sample) | 45 | 69,589 |
| 2 | hi_iiith | Hindi (Hyderabad sample) | 54 | 107,516 |
| 2 | hi_iitk | Hindi (Kanpur sample) | 57 | 108,759 |
| 2 | ic | Icelandic | 45 | 73,022 |
| 2 | no | Norwegian | 19 | 20,121 |
| 2 | ru_mo | Russian (Moscow sample) | 40 | 48,831 |
| 2 | se | Serbian | 43 | 49,561 |
| 2 | sp_ch | Spanish (Chile sample) | 45 | 67,896 |
| 2 | tr | Turkish | 16 | 17,224 |

`lab` keeps the MECO sample code; `first_language` holds the language name (in the CSV, without the sample in brackets). The codes `no` and `tr` occur in both waves but are different participants: participant identifiers do not overlap between waves.

**Split into exp1/exp2 by wave.** This follows the two published releases, each with its own paper, participants and version of the materials. It is provisional. In this repository `adelman2014_formpriming`, a multi-site study, keeps all sites in one file with a `lab` column, while `Pantelidou2026_wugTest` puts each language in its own exp file; MECO is both multi-site and multilingual, and a split by language or sample, with the wave as a column, would also be possible. The question is raised with the maintainers in the pull request.

## Column mapping
| column | source column | notes |
|---|---|---|
| `participant_id` | `uniform_id` | the identifier the MECO readme asks users to use; `subid`, `supplementary_id` and `trial` are not used |
| `lab` | `lang` | |
| `first_language` | — | from `lab` |
| `text_id` | `trialid`, corrected | see "Text identity" |
| `trial_order` | `trialnum` | exp2 only; unchanged, see "Presentation order" |
| `word_position` | `wordnum` | |
| `sentence_number` | `sentnum` | |
| `stimulus` | `word` | |
| `rt` | `dur` | 0 if never fixated |
| `first_fixation_duration` | `firstfix.dur` | |
| `gaze_duration` | `firstrun.dur` | |
| `go_past_time` | `firstrun.gopast` | 0 placeholders set to empty |
| `fixation_count` | `nfix` | 0 if never fixated |
| `run_count` | `nrun` | 0 if never fixated |
| `is_fixated` | `skip` | `1 - skip` |
| `is_first_pass_skipped` | `firstrun.skip` | |
| `is_regressed_into` | `reg.in` | |
| `is_regressed_out_of` | `reg.out` | |

Not carried over: `blink`, `reread`, `refix`, the first-run counts and regression flags (`firstrun.nfix`, `firstrun.refix`, `firstrun.reg.in`, `firstrun.reg.out`), selective go-past time (`firstrun.gopast.sel`), and the saccade and landing-position measures (`firstfix.sac.in/out`, `firstfix.launch`, `firstfix.land`, `firstfix.cland`, and the `singlefix.*` family). They remain available in `original_data/`.

# Corrections to the source data
**Text identity.** The source column `trialid` is documented as the text number (1–12), and for almost all trials it is. For six participants it runs one behind the text actually shown on a stretch of trials; in each case the stretch follows a text that is absent from the participant's data, as if the numbering had closed the gap. `preprocess_data.R` therefore identifies the text of every trial from its words. It concatenates the trial's interest areas in order and compares their character 6-grams with each of the 12 texts of that sample in the reading materials (`supp_texts.csv`, `supp_texts_wave2.xlsx`), ignoring whitespace, quotation marks, zero-width characters, the line-break markers and the `*` word separators of the Chinese materials. Every trial matches exactly one text: at least 99.3% of its 6-grams are found in that text, and at most 10% in any other. The result is cross-checked against the source column `itemid`, which carries the text number up to a constant offset per sample (+1 for `ru` and `ru_mo`, −1 for `ba`, 0 elsewhere); the two agree on every trial of every participant, and the script stops if they ever disagree. The corrected trials are:

| participant | source `trialid` → `text_id` |
|---|---|
| ee_9 | 4→5, 5→6, 6→7, 7→8, 8→9, 9→10, 10→11 |
| ee_22 | 1→2, 2→3, 3→4, 4→5, 6→7 |
| ru_8 | 4→5, 5→6, 6→7, 7→8, 8→9, 9→10, 10→11, 11→12 |
| ic_6 | 7→8, 9→10, 10→11 |
| en_uk_46 | 11→12 |
| en_uk_57 | 9→10, 10→11, 11→12 |

The same matching also confirms that the word strings in the data reproduce the reading materials: all 348 sample × text combinations match apart from quotation marks, and a handful of single-character differences between the materials file and what the data record (a zero-width character in Chinese and Hindi, full-width digits in traditional Chinese, one letter each in a Danish and a Hindi text).

**Duplicate rows.** In Wave 2, all 1,400 rows of participant `da_16` appear twice in the source, identical in every column. The copies are dropped (980,211 source rows → 978,811).

# Prompts
In `prompts.jsonl`, each text is one trial, headed by its text number (`Text 5:`) and listed in the order the participant read it: by `trial_order` in Wave 2 and by `text_id` in Wave 1. Words are listed with the **total reading time in milliseconds** marked with `<< >>`; words that never received a fixation are marked `<<not fixated>>`. The `rt` metadata field lists the reading times of the fixated words only. Further metadata fields: `first_language`, `lab`, and `texts` (the text numbers in the line, in reading order). The prompts are written in English with the words in the original language and script.

**Chunks of six texts.** A session of 12 texts does not fit the 32K-token budget in every language. Each participant's texts are split, in reading order, into lines of six consecutive texts, so a complete session becomes two lines; participants with fewer texts get fewer or shorter lines. Exp1 gives 1,061 lines and exp2 1,149, 2,210 in total. No trials are dropped. The chunk size was measured on every line under three tokenisers:

| texts per line | longest line (characters) | cl100k_base | o200k_base | Qwen2.5 |
|---|---|---|---|---|
| 6 (used) | 43,199 | 22,226 | 18,940 | 25,357 |

The longest lines are Hindi under the Qwen2.5 tokeniser. A single text takes at most 5,161 Qwen2.5 tokens, so seven texts per line could reach about 29,500, too close to the limit; four per line would have given three lines per session instead of two. `generate_prompts.py` checks every line against the 100,000-character limit of `scripts/validate_submission.py` and, when `tiktoken` is installed, against 32,000 cl100k tokens; the chunking itself does not depend on the tokeniser, and the archive is reproduced byte for byte on re-running.

**Instructions** are reconstructed from the procedure described in the two papers ("Each of the 12 passages appeared on a separate screen, with participants instructed to read them silently for comprehension and press the space bar when finished", Wave 2 paper, Methods); the wording of the instruction screen is not published.

**Empty interest areas are not shown, so the prompts have fewer word lines than the CSVs have rows.** 21 interest-area positions (10 in Wave 1, 11 in Wave 2) have an empty `stimulus`. They sit between two sentences, where the source text had a double space, and are not words; a few received fixations landing on that space. Their rows are kept in the CSV files and left out of the prompts:

| | CSV rows | rows with empty `stimulus` | `Word` lines in the prompts |
|---|---|---|---|
| exp1 | 855,462 | 266 | 855,196 |
| exp2 | 978,811 | 303 | 978,508 |

Because these positions are skipped, the `Word` numbers in a prompt jump by one at each of them (`Word 8`, then `Word 10`); the numbers are `word_position` and match the CSV. `generate_prompts.py` checks the line counts above on every run.

# Notes
- **Unfixated words.** The source leaves every measure empty when a word was never fixated (`skip = 1`). As in `luke2018_provo` and `berzak2025_onestop`, `rt`, `fixation_count` and `run_count` are set to 0 for these rows, and `first_fixation_duration`, `gaze_duration`, `go_past_time` and the regression flags stay empty. This is exactly how `luke2018_provo` codes them (checked on its exp1.csv: all 76,846 unfixated rows have `rt` 0, counts 0 and empty durations). The 0 in `rt` means that no reading time accumulated on the word, not a measured reading of 0 ms; `is_fixated` separates the two cases, and no fixated word has `rt` 0. For the two counts, 0 is simply the true value. 25.5% of Wave 1 rows and 24.9% of Wave 2 rows are unfixated words.
- **Go-past time.** popEye stores `firstrun.gopast = 0` for words that were skipped during first-pass reading and fixated only later, where go-past time is undefined; the zeros coincide exactly with `firstrun.skip = 1`. They are set to empty. Go-past time is also empty in the source for about 5,000 fixated words per wave, almost all among the last three words of a text, where the reader did not move past the word before the trial ended.
- **First run.** In popEye, the "first run" measures (`gaze_duration`, `first_fixation_duration`) refer to the first run on the word whenever it occurred, so for a first-pass skipped word they describe its first later visit. `is_first_pass_skipped` identifies these words.
- **Texts removed by the authors.** The source files contain only the texts that passed the authors' eye-tracking quality checks. 119 of 580 Wave 1 participants and 98 of 654 Wave 2 participants have all 12 texts; the others have between 3 and 11. Every text that is present is complete, with all its interest areas.
- **Presentation order.** Wave 2 records the experiment's trial counter, `trialnum`, kept unchanged as `trial_order`. It counts the practice text where there was one, so texts sit at positions 2–13 in most samples and 1–12 in the Basque and Norwegian samples, which had no practice text in the numbering (as the Wave 2 materials note). For all but 14 participants `trial_order` follows `text_id`. The exceptions are 14 Danish participants (da_8, da_10, da_11, da_14, da_17, da_18, da_20, da_28, da_39, da_40, da_48, da_59, da_65, da_69): their text 12 sits at position 1, the slot the practice text occupies in the other samples, followed by texts 1–11 at positions 2–12. The pattern is the same for every Danish participant who has text 12 except da_16 (position 13), so it is taken as the real order: these participants read text 12 first, and their prompts list it first. Wave 1 has no trial counter; the source documents `trialid` as the position of the text in the session, and apart from the six participants corrected above it equals `text_id`, so Wave 1 prompts follow `text_id`. exp1.csv has no `trial_order` column rather than one filled by assumption.
- **Comprehension data are not included.** The release contains per-question comprehension accuracy for both waves (`joint_l1_acc_full_breakdown.rda`, `joint_l1_wave2_acc_full_breakdown_trimmed.rda`), but they are left out of the CSVs and the prompts, for three reasons: the files record only whether each answer was correct (0/1), not the answer the participant gave; the wording of the questions is distributed for Wave 1 (`comp-questions.xlsx`) but not for Wave 2; and the files contain answers for texts whose eye-tracking data were removed, so they do not line up with the reading data.
- **Documentation mismatch.** The Wave 2 primary-data readme describes `joint_comp_L1_Wave2_trimmed.rda` as the number of correct responses "out of a total of 24 questions", but the data contain 48 questions per participant (12 texts × 4), the same as Wave 1. Noted, not changed.
- **Not included** from the release: fixation and saccade reports, sentence-, passage- and reading-rate files, individual-differences data (CFT, LEAP-Q and the per-site tests), the bibliometric database, descriptive statistics, back-translations, Coh-Metrix and LSA similarity files, the bitmaps of the Wave 2 texts and the analysis code. MECO L2 (English as a second language) is a separate OSF project (https://osf.io/q9h43/) and is not part of this contribution.
- **Expected validator warning.** `original_data/` holds no CSV of trial data (the source is `.rda`), so the validator skips its original-vs-processed row comparison.
