# Reference:
Adelman, J. S., Johnson, R. L., McCormick, S. F., McKague, M., Kinoshita, S., Bowers, J. S., Perry, J. R., Lupker, S. J., Forster, K. I., Cortese, M. J., Scaltritti, M., Aschenbrenner, A. J., Coane, J. H., White, L., Yap, M. J., Davis, C., Kim, J., & Davis, C. J. (2014). A behavioral database for masked form priming. *Behavior Research Methods*, 46(4), 1052–1067. https://doi.org/10.3758/s13428-013-0442-y

# Data source:
https://adelmanlab.org/fpp/ (linked from the paper as the project's data archive)

`original_data/` contains:
- `FPP_text_files.zip` — the archive of trial-level text files exactly as distributed by the authors (`FPP/MP_data.txt`, `FPP/spelling_data.txt`, `FPP/vocab_data.txt`). Only `MP_data.txt` is used here.
- `fpp_stimuli.csv` — the target strings and all 28 primes per target, extracted from the `primes and targets` sheet of the authors' `FPP.xlsx`, keyed to `targetNum`/`lexStatus` via the `trial by trial` sheet.
- `fpp_participant_scores.csv` — per-participant vocabulary and spelling accuracy, extracted from the `vocabulary scores` and `spelling scores` sheets of the same workbook.

The full `FPP.xlsx` (232 MB) is not redistributed here because of its size; the
three files above carry everything the pipeline needs. The extraction was
verified by checking every prime in the trial-by-trial sheet against the
stimulus table: 21,000 checks, no mismatches.

# Description
A single large multi-site masked form priming experiment. 1,015 participants at
14 universities each completed 840 primed lexical decision trials, crossing 420
word targets and 420 nonword foils with 28 prime types.

- **exp1.csv**: 852,600 rows = 1,015 participants × 840 trials. One row per
  trial, with the target, the prime actually shown, the prime type, the
  response, accuracy and response time.

Each trial presented a fixation cross for 300 ms, a blank screen for 200 ms, a
`##########` forward mask for 500 ms, then the prime in lower case at
five-eighths size for 50 ms, then the target in upper case until a response or
2000 ms. Corrective feedback followed incorrect responses and timeouts.

Overall accuracy is 91.7%, with 3,999 timeouts (0.5% of trials).

## Prime types
Codes are relative to a six-letter target `123456`; `d` is a random letter not
in the target, `D` a repeated one.

| Condition | Code | Prime type | Example (DESIGN) |
|---|---|---|---|
| ID | 123456 | Identity | design |
| TL12 | 213456 | Initial transposition | edsign |
| TL34 | 123546 | Medial transposition | desgin |
| TL56 | 123465 | Final transposition | desing |
| NATL24 | 143256 | 2-apart transposition | degisn |
| NATL25 | 153426 | 3-apart transposition | dgsien |
| DL-1M | 12356 | Medial deletion | dsign |
| DL-1F | 12345 | Final deletion | desig |
| DL-2M | 1256 | Central double-deletion | degn |
| T-All | 214365 | All-transposed | edisng |
| TH | 456123 | Transposed-halves | igndes |
| SUB3 | 123/456 | Half | des |
| RH | 321654 | Reversed-halves | sedngi |
| IH | 415263 | Interleaved-halves | idgens |
| RF | 165432 | Reversed-except-initial | dngise |
| SN-I | d23456 | Initial substitution | pesign |
| SN-M | 123d56 | Medial substitution | desihn |
| SN-F | 12345d | Final substitution | desigj |
| N1R | 13d456/124d56 | Neighbor-once-removed | dslign |
| DSN-M | 12dd56 | Central double-substitution | dewvgn |
| IL-1M | 123d456 | Central insertion | desrign |
| IL-2M | 123dd456 | Central double-insertion | desaxign |
| IL-2MR | 123DD456 | Central double-insertion, repeated letter | deshhign |
| EL | 1dddd6 | Central quadruple-substitution | dzbtkn |
| IL-1I | d123456 | Prefix | mdesign |
| IL-1F | 123456d | Suffix | designl |
| ALD-PW | dddddd | Unrelated pseudoword | voctal |
| ALD-ARB | dddddd | Unrelated arbitrary | cbhaux |

# Prompts
In `prompts.jsonl`, responses are marked with `<< >>`. Each participant is
assigned **two random letters**, one for "word" and one for "nonword", so the
key mapping varies across participants; the draw is seeded for reproducibility.
The original apparatus used left and right buttons rather than named keys.

Feedback text appears only where participants actually received it — `Incorrect.`
after an incorrect response and `No response detected.` after a timeout. Correct
trials carry no feedback text.

**Primes in the prompts.** The instructions reproduce what participants were
told, which "described the sequence of events omitting mention of the prime"
(paper, p. 11) — the primes were forward-masked and shown for 50 ms, and
participants were not informed of them. The trial lines nonetheless record the
prime that was displayed, since the prime is the experimental manipulation this
database exists to capture; without it the dataset reduces to an unexplained
lexical decision. If the maintainers would prefer target-only trial lines, that
is a one-line change to `TRIAL_*` in `generate_prompts.py`.

# Notes
- **Negative RTs in the source.** `RT` in `MP_data.txt` is stored as a negative
  number on incorrect trials, with the magnitude being the response time; a
  value of exactly -2000 marks a timeout. The correspondence is exact: all
  70,736 negative RTs are incorrect trials and all 781,864 positive RTs are
  correct ones. `rt` here stores the magnitude and `accuracy` carries
  correctness.
- **Practice trials.** Source `trialNum` runs 29–868 because the first 28 trials
  of each session were practice and are not distributed. Trials are renumbered
  1–840.
- **All trials are included.** The authors' `FPP.xlsx` carries trial- and
  participant-level exclusion flags (`RTok`, `SubjAcc`, `SubjCB`, `Use`) used
  for the analyses in the paper. Those filters are not applied here, since this
  repository asks for unaggregated, unfiltered trial-level data. As a result the
  condition means computed from `exp1.csv` run about 3.7 ms below the published
  means, uniformly across all 28 conditions; the rank order is essentially
  unchanged (Spearman ρ = 0.99 against the published values).
- **Response recovery.** The source records accuracy, not which button was
  pressed. Because the task had exactly two alternatives, the response is
  recovered from `accuracy` and `stimulus_type`, and left empty for timeouts.
- **Excel corruption in the workbook.** In `FPP.xlsx` the `subID` field is
  coerced to date serials (e.g. "1-2" becomes 41306). The pipeline therefore
  reads trials from the plain-text `MP_data.txt`, which is unaffected, and uses
  the workbook only for stimuli and participant scores.
- **No participant demographics.** Age, gender and language background are not
  distributed with the database. The vocabulary and spelling scores are included
  instead as participant-level covariates.
- **Expected validator warning.** The submission checker compares the row count
  of `processed_data/` against the CSVs in `original_data/` and reports a 460x
  expansion. This is expected: the trial data lives inside
  `FPP_text_files.zip` (the authors' original archive, kept zipped to avoid
  committing a 110 MB text file), so only the small stimulus and score tables
  are visible to that check. `MP_data.txt` contains exactly 852,600 trial rows,
  matching `exp1.csv` one to one.
