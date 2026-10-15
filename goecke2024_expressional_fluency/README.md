# Goecke, Weiss, and Wilhelm (2024): expressional fluency

LOCAL PREPARATION. Processed CSVs, validation reports, local audit files, and one complete participant prompt preview have been generated with contributor approval. The reviewed German prompt representation has been approved and prompts.jsonl.zip has been generated and verified. Public sharing remains pending.

Study: Goecke, B., Weiss, S., & Wilhelm, O. (2024). “Driving Factors of Individual Differences in Broad Retrieval Ability: Gr Is More Than the Sum of Its Parts.” Journal of Experimental Psychology: Learning, Memory, and Cognition. [Paper DOI](https://doi.org/10.1037/xlm0001336). German task administration.

The paper identifies [OSF project erdxq](https://osf.io/erdxq/) as the study data and materials repository. Contribution source files were supplied locally by the contributor; the public-link reference does not assert that every local raw/scoring revision is identical to a current OSF file. Maintainers requested a separate contribution per verbal retrieval paradigm and German experiment representations.

## Sources and task mapping

The contributor confirmed the supplied Inquisit scripts as the administered versions. Raw exports supply response text, latency, and event order. Scoring versions are exactly those read by the supplied R widening scripts, with the case-only `Vs`/`VS` filename discrepancy resolved to the available file. Unselected earlier scoring versions are not copied.

| Source task | Condition | Variant | Limit (ms) | Original cues |
| --- | --- | --- | --- | --- |
| long_base | long | base | 240000 | Nennen Sie ein Synomym zu dem Begriff: / EINSAM |
| short_base | short | base | 90000 | Nennen Sie ein Synonym zu dem Begriff: / ENTSPANNEN; Nennen Sie ein Synonym zu dem Begriff: / SAUBER |

The supplied expressional-fluency materials contain only the base synonym tasks: EINSAM (240 seconds), ENTSPANNEN (90 seconds), and SAUBER (90 seconds). There is no expressional hard variant in the supplied files, and none is added to this contribution. The long synonym script has a cap of 36 submissions; each short synonym cue has a cap of 24. Additional hard tasks outside the paper's reported indicators are documented in the ideational- and word-fluency contributions.

## Contribution files and local review files

```text
goecke2024_expressional_fluency/
  original_data/
    raw/
    scored/
    task_materials/
    analysis_scripts/
  processed_data/
    exp1.csv          # generated and checked
    exp2.csv         # generated and checked
    validation.json     # generated and checked
  CODEBOOK.csv
  preprocess_data.py
  generate_prompts.py
  README.md
  prompts.jsonl.zip     # generated and checked
  local_audit.csv       # local review only; exclude from contribution
  prompt_preview.txt   # local review only; exclude from contribution
```

## Data model and exclusions

The processed filenames follow the repository's expN.csv convention. exp1.csv is the consolidated event table, with one row per recorded event. exp2.csv is the consolidated rating table, with one row per event and rater. The numbers identify two tables for the same paradigm; exp2.csv is not a second experiment. Long, short and available hard conditions remain identifiable through task metadata. Original raw exports and the scoring files selected by the supplied R scripts are combined reproducibly during preprocessing, including the selected scoring snippets. Individual rater values remain separate; responses are not duplicated into the event table or averaged across raters.

exp1.csv has one row per recorded event, including empty and control records and instruction abort records. Multiword entries stay intact. Repeated runs are retained separately. A session is one recorded day; it does not assert that experiments on that day were contiguous. Actual date/time and numerical subject remain in original_data for joining; processed tables omit them. Source start time orders runs, not individual responses. Within each run the script block sequence orders blocks; original source record order is retained within each block and numbered trial order is checked. Two word-long control events have blank trial numbers and keep their recorded positions. Any equal-start-time ties use filename and subject, so their cross-run order is not independently established.

Explicit R filters exclude 99TEST99, 04TEST04, 00TEST00, empty vpcode_hd1, and subject 811805689. Nonstandard IDs are retained in the local audit and unchanged sources; no IDs are guessed. The two raw code `8` records are instruction aborts. The study's later multivariate outlier selection is not applied. The contributor confirmed that 04VAIN01 is a genuine participant included in the published data. It is retained; the R exclusion of numerical subject 811805689 remains in effect. Consent-withdrawal IDs remain unknown; this preparation does not establish the published N=322 analysis sample.

exp2.csv holds each R-selected rater's event-linked scores and scored response string. The join uses normalized date, run start time, subject, participant code, block and original trial number, never edited response text. An unmatched or ambiguous rating goes to local_audit.csv, with its original values retained in original_data. Numeric flu is a count and can exceed 1; it is not binary accuracy. -99 flu becomes missing. Blank/NA rep becomes 0 following the R convention. Unresolved score strings such as `o` stay unresolved. No rating averaging, semantic recoding, automatic spelling corrections, or newly inferred repetition flags are applied. Blank output fields represent unavailable values except for response, where blank means a recorded empty field.

## Instructions and prompts

Instructions are extracted from the visible HTML body with original German wording; HTML entities and layout whitespace are normalized. IQX cue text preserves spelling, including the original “Synomym” typo. Each participant's complete available paradigm record is represented in one JSONL object with text, experiment, participant_id, and English metadata. Each run begins with its original instructions. Available transition wording precedes the next observed task block. An unavailable InstructionsSynBetween.htm page is omitted with the contributor's approval and documented in expressional metadata. Completion pages are not added because their display is not established by the last response record.

All retained recorded events appear exactly once. Response and available latency are inside the required double-angle delimiters. Empty input is described as “Keine Texteingabe aufgezeichnet”; it is not called a timeout. Control records retain the recorded key string. Ratings are available in the tidy rating table and are omitted from the behavioral prompt. No response is truncated, split, translated or corrected. Whole paradigms may include incomplete runs.

## Validation and supervised execution

Python 3 standard library is sufficient for preprocessing and the conservative prompt length check. The default length measure is UTF-8 byte count, an upper bound for cl100k_base/o200k_base byte-based BPE text token counts. It is reported as a bound, not as an exact token count. Optional exact checks require tiktoken and the selected encoding cache; installing or downloading them requires a separate approved step. The strict limit is below 32,000. Participants at or above the bound/selected tokenizer limit stop archive generation; responses are never silently shortened.

Run only after reviewing these commands with the contributor, in this folder:

```bash
python3 -B preprocess_data.py
python3 -B generate_prompts.py
```

These commands read sources and print validation reports without writing outputs. For complete preview prompts, add `--examples 3` to the second command. Both write commands have already been run with contributor approval. Their outputs now exist, so running either command again in this folder will stop rather than replace files. The commands below document reproduction in a fresh copy; any further file-changing run needs the contributor's approval:

```bash
python3 -B preprocess_data.py --write
python3 -B generate_prompts.py --write
```

Both scripts refuse to overwrite existing files. Prompt generation reads processed_data/exp1.csv directly, preserving each response string and recorded order. It validates CSV fields, numeric values, IDs, event ordering, task labels and participant/event totals against processed_data/validation.json. Original German instruction pages are read from task_materials and checked against their recorded SHA-256 hashes. Raw/scored preprocessing is not rerun by the prompt script; exp2.csv remains separate from the behavioral prompt. Source SHA-256 hashes, encodings, separators, header/row counts, extra fields, missing IDs, exact duplicate source rows, task labels/caps, latency values, German umlauts, unique IDs, order, join ambiguity, row reconciliation and reserved prompt symbols are checked. Unexpected named source columns stop processing. Nonempty unnamed scoring columns are preserved as positional JSON in source_extra_fields with a warning. Three such annotations occur in ideational scoring sources: one `1` and two `xxx`; their meaning is unverified. Dates parse as ISO or explicitly day-first source formats. Source spelling/mojibake in scoring files is preserved and differences are flagged.

## Privacy, scope, and sharing status

No covariates are included: working memory, crystallized intelligence, mental speed, secondary memory, age, and sex/gender are outside the approved contribution scope. Participant codes can link these data to other study files. Original exports contain recording dates/times and subject numbers. Free text needs a manual privacy review; a regex scan cannot establish that it contains no identifiers. Consent-withdrawal exclusions and permission to redistribute the original exports, scoring annotations, and task materials remain unverified. Local draft preparation is not public-release approval. The repository license does not establish source redistribution rights. The paper PDF, XLSX covariate codebook and unrelated tasks are not copied.

Before contribution: review the preserved unresolved scoring annotations; verify eligible participant IDs/public-sharing rights; confirm the exact commit file list and current repository LFS rules. The full German previews have been reviewed and output generation has been approved. No retained rating joins are unmatched or ambiguous. Exclude local_audit.csv and prompt_preview.txt. Git/GitHub actions are executed by the contributor one action at a time. No Git operation has been performed by these scripts.

Repository conventions checked against the current [PsychLing-101 README](https://github.com/Data-X01/PsychLing-101/blob/main/README.md) and [root CODEBOOK](https://github.com/Data-X01/PsychLing-101/blob/main/CODEBOOK.csv). Local CODEBOOK uses its Recommended Column Name,Description convention. Custom fields are documented in this contribution CODEBOOK. The 23 names absent from the repository-wide CODEBOOK need corresponding definitions there; a local CODEBOOK_additions.csv is prepared for the contributor to apply before staging. Existing canonical definitions are retained. Existing LFS rules are path-specific; assess the final outputs before adding any LFS rule.

## Local draft checks, 6 October 2026

The saved processed tables contain 331 participant records, 9,670 events and 19,340 linked rater records. Raw and scored row totals reconcile exactly after the documented exclusions. No unmatched or ambiguous retained ratings and no repeated participant/event/rater keys were found. These counts are local preparation counts; final public-sharing eligibility remains unverified.

Every copied source matched its original SHA-256 digest. Python syntax, unique output IDs, source and response order, task cues, rater joins, German umlauts, JSON serialization, instruction selection and one delimiter pair per recorded event passed the checks. The largest complete prompt was 4,753 UTF-8 bytes. Every prompt was below 32,000 bytes, providing a conservative token bound for the documented byte-based BPE tokenizers. Exact tokenizer counts were not measured. No participant exceeded this bound.

The processed_data directory now contains exp1.csv, exp2.csv, and validation.json. Saved CSV rows were read back and matched against the source-based preparation, including every response, score, and field. One complete prompt_preview.txt is available for local review. prompts.jsonl.zip has been written and independently checked against the saved exp1.csv. One ideational repetition value `o` and three unnamed ideational scoring annotations are preserved with warnings. Word and expressional scoring have no unresolved numeric values. No raw response text was altered.

## Generated files and preview review

| File | Data rows | Size (MB, decimal) | Purpose |
| --- | ---: | ---: | --- |
| `processed_data/exp1.csv` | 9,670 | 2.4672 | Recorded task events |
| `processed_data/exp2.csv` | 19,340 | 2.4061 | Event-linked rater scores |
| `processed_data/validation.json` | n/a | 0.0030 | Source checks, counts and warnings |
| `prompts.jsonl.zip` | 331 JSONL records | 0.0984 | Full participant prompts |
| `local_audit.csv` | 294 | 0.0268 | Local exclusion review; do not contribute |
| `prompt_preview.txt` | n/a | 0.0028 | One full participant prompt; local review only |

The full preview is participant `02YEIZ05`: 29 recorded events in 2 task runs, with conditions long / base, short / base. It includes 3 recorded empty entries and no control-key events. The file contains exactly the generator's prompt text, begins with the complete original instructions for the first recorded run, and has no review header, omitted response, or shortened section. Its UTF-8 byte length is 2,775. The preview participant is an illustrative example, not a participant selection rule.

To review the preview:

1. Open prompt_preview.txt and read each instruction section. Compare the German wording and task cues with the supplied task materials.
2. Check the numbered entries, recorded empty inputs, and latency wording. Confirm that this presentation reflects the task as administered.
3. Tell the assistant which wording or formatting needs changing, or approve the reviewed representation. The contributor reviewed these previews and approved archive generation. Any later revision still requires explicit approval.

The expressional preview omits the unavailable InstructionsSynBetween.htm page as already agreed. No substitute transition instruction is invented. Existing spelling errors in original cues and participant responses are preserved. Script generation covers every retained participant, not just this preview example.

All current files are below 100 MB. The largest generated file across the three paradigms is the word-fluency exp2.csv at 23,993,370 bytes. Archives have now been measured; check the current repository LFS rules before staging. This local preparation has performed no Git/GitHub action. The contributor will receive one action at a time for the fork, clone, branch, staging, commit, push and pull request, with its purpose and expected result.

## Saved prompt archive checks

The CSV-reading generator was checked against the existing archive: every JSONL byte, participant ID, metadata field and prompt text matched. Existing archives were retained without rewriting. Across the three paradigms this comparison covered 998 participant records. The contributor reviewed the original prompt representation before this change to CSV input.

The archive contains one UTF-8 prompts.jsonl member with 331 JSONL records and 9,670 represented events. Each record contains text, experiment and participant_id, with English metadata. Participant IDs are unique and match the retained processed event participants. Every response and available latency was compared in order with exp1.csv; the archived preview participant matches prompt_preview.txt exactly. ZIP integrity and JSON parsing passed. Archive size is 98,362 bytes; uncompressed JSONL size is 1,052,024 bytes.

The largest prompt is 4,753 UTF-8 bytes. Every record is below the conservative 32,000-token bound for the documented byte-based BPE tokenizers; exact token counts have not been measured. No record was truncated. The required response delimiters each occur once per recorded event.

A separate code audit of all eight raw exports and all uploaded scoring versions found the known codes 99TEST99, 04TEST04 and 00TEST00, with no additional code matching the screened test-like names. There are 503, 21 and 13 original raw rows respectively for these codes. They remain in unchanged original sources and local audit records. All three known test codes, missing IDs and code 8 are absent from the processed tables and archived participant IDs. 04VAIN01 is retained following the contributor's confirmation that it belongs in the published data. This check does not establish the status of every other participant code or resolve the unknown consent-withdrawal IDs.

## Copied source inventory

- `task_materials/synonym_base_long.iqx`
- `task_materials/InstructionsEnd.htm`
- `task_materials/InstructionsSyn_long.htm`
- `raw/wilhelm_retrieval_version2_synonym_base_long_raw_2206030851.csv` (utf-8-sig, ',' delimiter, 3598 records)
- `task_materials/synonym_base_short.iqx`
- `task_materials/InstructionsSyn.htm`
- `raw/wilhelm_retrieval_version2_synonym_base_short_raw_2206030842.csv` (utf-8-sig, ',' delimiter, 6170 records)
- `analysis_scripts/23_SynomeLong.R`
- `scored/synonym_base_long_JL1_19-04-2022_copy.csv` (utf-8-sig, ';' delimiter, 2209 records)
- `scored/synonym_long_JL_full_03-06-2022_snippet2.csv` (cp1252, ';' delimiter, 1389 records)
- `scored/synonym_base_long_KH1_19-04-2022.csv` (utf-8-sig, ';' delimiter, 2209 records)
- `scored/synonym_long_kh_full_03-06-2022_snippet2.csv` (utf-8-sig, ';' delimiter, 1389 records)
- `analysis_scripts/24_SynonymeShort.R`
- `scored/synonym_base_short_VS1_19-04-2022_copy.csv` (utf-8-sig, ';' delimiter, 3700 records)
- `scored/synonym_short_VS_full_03-06-2022_snippet2.csv` (utf-8-sig, ';' delimiter, 2470 records)
- `scored/synonym_base_short_KH1_19-04-2022_copy.csv` (utf-8-sig, ';' delimiter, 3700 records)
- `scored/synonym_short_kh_full_03-06-2022_snippet2.csv` (utf-8-sig, ';' delimiter, 2470 records)
- `analysis_scripts/README_VPCODES.txt`
