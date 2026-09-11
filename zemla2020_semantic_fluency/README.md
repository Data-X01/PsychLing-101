# zemla2020_semantic_fluency — Semantic fluency

Participants named as many members of a cued category as they could in three minutes, over nine rounds. The sample distributed with SNAFU.

> Zemla, J. C., Cao, K., Mueller, K. D., & Austerweil, J. L. (2020). SNAFU: The Semantic Network and Fluency Utility. *Behavior Research Methods*, 52(4), 1681–1699. https://doi.org/10.3758/s13428-019-01343-w

**Source data:** https://osf.io/asb7q/ (CC BY 4.0)

**Caveat.** This is the demonstration sample shipped with a methods paper about a software tool, not a reported experiment: three collections from 2015–2017, merged. The paper's validation analyses used a different corpus, absent from the deposit, so no published results exist against which to check this processing. Verification rests on structural agreement instead — `preprocess_data.py` reads the source back against the paper's own figures before dropping anything.

## Source and contribution are not the same size

| | Participants | Lists | Responses | Categories |
|---|---|---|---|---|
| **Source**, `snafu_sample.csv` as published | 82 | 807 | 24,572 | 6 |
| **Contribution**, `processed_data/` | 70 | 633 | 17,599 | 5 |
| The excluded collection | 12 | 174 | 6,973 | 1 |

The paper's figures describe the source; claims about this contribution use the second row. The scripts assert that the two account for each other exactly.

## Experiment2 is excluded

Neither the task code nor a procedural description survives for that collection. Its round time limit is not the documented one — two minutes for B1–B5 and four for B7–B13, against three everywhere else — and that figure exists only because it can be read back off the ceilings in the data. Once one parameter of the procedure is known to have differed, others may have differed too, the wording of the instructions among them. A prompt is a description of what happened to a participant, and for these twelve participants no such description can be built.

They are dropped rather than flagged: no rows in `processed_data/`, no prompts. Their raw rows stay in `original_data/` untouched, and anyone who wants to process them can.

## File numbering — read this first

Files are numbered by position in this contribution, not by the collection they hold.

| File | Collection | n | IDs | Categories | Lists | Responses |
|---|---|---|---|---|---|---|
| `exp1.csv` | Experiment1 | 20 | A101–A120 | animals, fruits, vegetables | 182 | 4,335 |
| `exp2.csv` | **Experiment3** | 50 | C101–C150 | animals, foods, tools | 451 | 13,264 |

**`exp2.csv` is not Experiment2.** That collection has no file at all. The prompts carry the same pairing in their `experiment` field; the mapping is declared in `OUTPUTS` and `INPUTS` at the top of the two scripts.

## Task

One category per round; the participant types items one at a time, pressing Enter after each. A round ends at the time limit — 180,000 ms, set by the task code (`timeperlist = 180`) and stated in the instructions, so documented rather than inferred. A round with five or fewer items is replayed with the same category, and the task's progress counter does not advance across the replay. Both retained collections ran the same design: three categories, three rounds each, pseudo-randomised so that no category repeats consecutively.

## Folder contents

```
zemla2020_semantic_fluency/
├── original_data/
│   ├── from_osf/         # osf.io/asb7q — data and analysis scripts
│   └── from_github/      # github.com/AusterweilLab/snafu-py — data and task code
├── preprocess_data.py
├── processed_data/       # exp1.csv, exp2.csv
├── CODEBOOK.csv
├── generate_prompts.py
├── prompts.jsonl.zip
└── README.md
```

`original_data/` keeps both published copies of `snafu_sample.csv` unmodified; the GitHub one is used because it alone carries `itemnum`, the presentation order, and because the task code exists only there.

## `processed_data/`

One row per response; within the two retained collections nothing is dropped. The files share a column layout, documented in `CODEBOOK.csv`. There is no column naming the collection — with one collection per file it would encode nothing. `rt` is the interval since the previous response, measured from round onset for the first item; `cumulative_rt` is the running total, and the two disagree in six lists, every row of which is flagged.

Problematic rows are flagged, not removed, following the project codebook, where `is_rt_outlier` marks outliers *removed from RT analyses* rather than from the data.

| Flag | Rows | exp1 / exp2 | Marks |
|---|---|---|---|
| `is_rt_outlier` | 232 | 61 / 171 | a latency that cannot be taken at face value |
| `is_repeated_response` | 242 | 103 / 139 | an item already given earlier in the same round |
| `is_category_mismatch` | 0 | 0 / 0 | a response whose category label disagrees with the rest of its list |
| `is_invalid` | 0 | 0 / 0 | a response that cannot be interpreted at all |

`is_rt_outlier` combines two symptoms: every row of a list whose timeline is broken, and rows with an interval of exactly zero, which is not a possible inter-item time. One such repair is documented in `parsedata.py`; the rest are not. `is_category_mismatch` finds nothing here because both cases in the source belonged to Experiment2, but the check still runs and fails the build if a new one appears. Five Experiment3 participants are missing individual lists and one has eight rounds rather than nine — gaps in the deposit, not in the processing.

## `prompts.jsonl.zip`

One JSON object per line, one per participant, 70 lines, both collections in one archive. Fields: `text`, `experiment`, `participant_id`, `rt`.

```
Round 1. Category: fruits. You have 3 minutes.
You say <<strawberry>> after <<5050>> ms.
You say <<tomato>> after <<2459>> ms.
```

Marking each item of the sequence follows `frank2013_reading` and `futrell2021_corpus`; marking the response together with its timing follows `hutchison2013_semantic` and `balota2007_naming`. Retrieval is sequential, and the pause before an item marks the boundary between semantic clusters.

The between-round screens are reproduced, since participants saw them, and the progress counter does not advance on a replayed round. Zero intervals appear as written, `after <<0>> ms`. One instruction serves every prompt with no value substituted into it: `generate_prompts.py` re-parses the task's own `main.html` on every run and stops if the wording has drifted from its templates. Flags are not carried into the prompts.

## Reproducing the processing

```bash
python preprocess_data.py     # original_data/ -> processed_data/exp1.csv, exp2.csv
python generate_prompts.py    # processed_data/ -> prompts.jsonl.zip
```

Relative paths, `pandas` the only dependency beyond the standard library. Both validate before writing and fail with a specific message rather than producing a silently wrong file; repeated runs produce a byte-identical archive.

## Open questions

- The instructions, between-round wording and consent procedure for Experiment2 are not in the deposit, which is why it is excluded.
- Why five of its participants ran 18 rounds of two minutes and seven ran 12 of four is not recoverable, nor why six of the twelve depart from strict alternation of the two categories.
- Demographics were collected, but the file is not in the deposit and the released data carry no demographic columns.

## Licence

CC BY 4.0, as is the article. Please cite the paper above.
