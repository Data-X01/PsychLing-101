# zemla2020_semantic_fluency — Semantic fluency across six categories

## Dataset

This contribution adds the semantic fluency sample distributed with SNAFU (Zemla, Cao, Mueller and Austerweil, 2020) to PsychLing-101.

In the semantic fluency task a participant is given a category and lists as many members of it as they can within a fixed time. The task is one of the oldest in psychology and is still used clinically, because the number of items produced and the way they cluster are sensitive to memory impairment. Responses are not produced at random: they arrive in semantically related runs, and the pause before each item is longer at the boundary between one run and the next, which is why the inter-item interval is treated as data rather than metadata.

> Zemla, J. C., Cao, K., Mueller, K. D., & Austerweil, J. L. (2020). SNAFU: The Semantic Network and Fluency Utility. *Behavior Research Methods*, 52(4), 1681–1699. https://doi.org/10.3758/s13428-019-01343-w

**Source data:** https://osf.io/asb7q/ (CC BY 4.0)

**Important caveat.** The paper is a methods paper about a software tool, not a report of these data. This file is the sample dataset distributed with SNAFU: three separate collections made between 2015 and 2017, merged for demonstration. The paper's validation analyses were run on a different corpus, which is not part of the deposit. Consequently there are no published results computed on these particular data against which the processing could be checked. Verification here rests on structural agreement instead: the paper states 807 lists from 82 participants totalling 24,572 responses, and the processed file reproduces all three figures exactly.

## Task

Each round presents one category. The participant types items one at a time and presses Enter after each. Each entry fades from the screen over 800 ms. A round ends when the time limit expires. If five or fewer items were produced, the round is replayed with the same category and the progress counter does not advance.

Between rounds the participant is told how many items they produced and, on the ordinary between-round screen, how many rounds they have completed. The replay screen gives the item count only, with no round counter.

## Design

82 participants, 807 lists, 24,572 responses across six categories. The sample comprises three collections that differ in categories, number of rounds and time limit.

| Group | n | Participant IDs | Categories | Rounds | Limit per round |
|---|---|---|---|---|---|
| Experiment1 | 20 | A101–A120 | animals, fruits, vegetables | 9 | 3 min |
| Experiment2 | 12 | B1–B5, B7–B13 | animals, supermarket items | 18 (B1–B5), 12 (B7–B13) | 2 min (B1–B5), 4 min (B7–B13) |
| Experiment3 | 50 | C101–C150 | animals, foods, tools | 9 | 3 min |

Experiment1 and Experiment3 follow the task code included in the deposit: three categories, each presented three times, in pseudo-randomised order such that no category repeats consecutively. Experiment2 alternates two categories, though only six of its twelve participants alternate strictly throughout. The other six have one or two positions where the same category runs twice; both rounds of every such pair run the full time limit, so these are not replays, and no task code survives to explain them.

## Folder contents

```
zemla2020_semantic_fluency/
├── original_data/
│   ├── from_osf/         # osf.io/asb7q — data and analysis scripts
│   └── from_github/      # github.com/AusterweilLab/snafu-py — data and task code
├── preprocess_data.py
├── processed_data/       # exp1.csv
├── CODEBOOK.csv
├── generate_prompts.py
├── prompts.jsonl.zip
└── README.md
```

### Two sources

`snafu_sample.csv` appears in both the OSF deposit and the SNAFU GitHub repository. The two copies are identical row for row; the GitHub version additionally carries an `itemnum` column giving the position of each item within its list, and names the interval column `rt` rather than `RT`. The GitHub copy is used, because item position is the presentation order and deriving it from row position would depend on the file never having been re-sorted. Both copies are kept unmodified.

The task itself — the instruction text, the between-round screens and the timing parameters — exists only in the GitHub repository, under `fluency_task/`, and is not part of the OSF deposit. It is included here because the prompts are built from it.

## `processed_data/exp1.csv`

One row per response, 24,572 rows. No rows are dropped. Problematic rows are flagged instead, following the convention encoded in the project codebook, where `is_rt_outlier` is defined as marking outliers *removed from RT analyses* rather than removed from the data.

**Timing.** `rt` is the interval since the previous response; for the first item in a round it is measured from the start of the round. The cumulative time from the start of the round is kept in a separate column. The two agree in 798 of 807 lists.

**Reconstructed time limits.** The time limit is documented only for Experiment1 and Experiment3, where the task code sets 180 s. For Experiment2 no task code survives, and the limit is inferred from the data: no response by B1–B5 exceeds 120,000 ms and none by B7–B13 exceeds 240,000 ms, with both ceilings dense and no intermediate values. The script derives this rather than hard-coding participant IDs, but the value is a reconstruction and is marked as such in the codebook. Experiment1 and Experiment3 overshoot 180,000 ms by up to 12.8 s in a handful of rounds, consistent with timer drift in a background browser tab rather than with a different limit.

### Flags

- **`is_rt_outlier`, 310 rows.** 287 rows in nine lists where the cumulative time does not agree with the running sum of intervals, plus 23 further rows with an interval of exactly zero, which is not a possible inter-item time. (There are 25 such rows; two of them fall inside those nine lists and are already counted.) One case is documented by the authors: a comment in `parsedata.py` records that reaction times were lost for one participant when items entered on a single line were separated by hand. The remaining cases are undocumented.
- **`is_repeated_response`, 314 rows in 193 lists.** Items repeated within the same round. The instruction asked participants not to repeat, but the task did not prevent it.
- **`is_category_mismatch`, 2 rows.** Two responses carry a category label different from the rest of their list. Both are boundary artefacts rather than participant behaviour, and the arithmetic identifies them: `hotsauce` in list B13/5 continues list B13/4, whose cumulative time ends at 230,646 ms, and 230,646 + 4,696 = 235,342, the cumulative time of the stray row. `fish` in list B9/0 is the missing first response of list B9/4 by the same argument. The labels are left as recorded and only flagged.
- **`is_invalid`, 0 rows.** No response is uninterpretable.

One further irregularity is reported by the script and not flagged, since it is a formatting artefact rather than a data fault: one response carries a trailing space, left as recorded. A second is neither reported nor flagged, since it is participant behaviour: C148 began a tools round with stationery and drifted into animals, with timing continuous throughout.

Five participants in Experiment3 are missing individual lists, and participant B6 is absent from the series entirely. One participant (C118) has eight rounds rather than nine, a truncated session. These are gaps in the deposit, not in the processing.

## `prompts.jsonl.zip`

One JSON object per line, one line per participant, 82 lines. Fields: `text`, `experiment`, `participant_id`, `rt`.

Each response is marked together with its inter-item interval:

```
Round 1. Category: fruits. You have 3 minutes.
You say <<strawberry>> after <<5050>> ms.
You say <<tomato>> after <<2459>> ms.
```

Marking every item of the sequence separately follows `frank2013_reading` and `futrell2021_corpus`; marking the response and its timing together follows `hutchison2013_semantic`, `miklashevsky2017_LDT_RussianNouns` and `balota2007_naming`. Both are appropriate here because retrieval is sequential — which item follows which is the phenomenon under study — and because the pause before an item marks the boundary between semantic clusters.

The between-round screens are reproduced, since participants did see them. The progress counter does not advance on a replayed round, matching the task code, which decrements it. The 25 zero intervals appear in the text as written, `after <<0>> ms`; they are faithful to the source and are flagged in `exp1.csv` for anyone who needs to exclude them.

### Instruction provenance differs by group

The instruction text is taken from the task code in the deposit. Two values in it are participant-specific and are substituted: the time limit and the total number of rounds. Everything else is reproduced word for word, and the generation script re-parses the source HTML on every run and fails if the text has drifted. This is why `generate_prompts.py` reads `original_data/from_github/fluency_task/web_version/main.html` at all rather than carrying its own copy of the wording: on each run it strips the markup from the instructions, between-round and replay screens, substitutes the original values back into its templates, and compares the two, so the quoted text cannot silently fall out of step with the task it claims to reproduce.

- **Experiment1 — original.** The task code is this group's own: same three categories, same nine rounds, same three minutes.
- **Experiment3 — adapted.** Same procedure and same parameters, confirmed by the paper's method section; only the categories differ. The wording is carried over from the Experiment1 code.
- **Experiment2 — adapted, parameters reconstructed.** No task code survives for this group. The wording is carried over, the round count comes from the data and the time limit is the reconstruction described above. The sentence telling participants that a category may repeat is omitted for this group, since it alternates two categories and the claim is not established for it.

Flags are not carried into the prompts; they are properties of the records, not of what the participant saw.

## Reproducing the processing

From inside this folder:

```bash
python preprocess_data.py     # original_data/ -> processed_data/exp1.csv
python generate_prompts.py    # processed_data/ -> prompts.jsonl.zip
```

Both use relative paths and need only `pandas` beyond the standard library. Both validate before writing and fail with a specific message rather than producing a silently wrong file. Repeated runs produce a byte-identical archive.

## Open questions

- The instruction text, the between-round wording and the consent procedure for Experiment2 are not in the deposit.
- Why five participants in Experiment2 received 18 rounds of two minutes and seven received 12 rounds of four is not recoverable from the files.
- Demographics were collected — the task includes a post-experiment survey recording gender and age — but the resulting file is not in the deposit and the released data carry no demographic columns.

## Licence

The OSF project is released under CC BY 4.0, as is the article. Please cite the paper above when using this contribution.
