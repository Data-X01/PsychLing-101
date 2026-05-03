# Reference

Hutchison, K. A., Balota, D. A., Neely, J. H., Cortese, M. J., Cohen-Shikora, E. R., Tse, C.-S., Yap, M. J., Bengson, J. J., Niemeyer, D., & Buchanan, E. (2013). The semantic priming project. *Behavior Research Methods*, 45, 1099–1114.

# Data source

https://doi.org/10.3758/s13428-012-0304-z

# Description

The Semantic Priming Project (SPP) collected speeded naming and lexical decision data for 1,661 target words following related and unrelated prime words, across four universities (Montana State, SUNY Albany, University of Nebraska–Omaha, Washington University). Stimuli were prime–target pairs drawn from the Nelson et al. (1999) word association norms.

Two prime types were used:
- **first_associate**: The prime word is the cue for which the target is the most common free-association response.
- **other_associate**: The prime word is a different cue (2nd–Nth most common) for which the target is also a free-association response.

Two levels of stimulus onset asynchrony (SOA) were tested per session:
- **200 ms** (short): thought to reflect automatic priming mechanisms.
- **1,200 ms** (long): thought to additionally involve intentional/strategic mechanisms.

Related and unrelated conditions were created by randomly re-pairing related prime–target pairs within the first-associate and other-associate sets.

## exp1.csv — Lexical Decision Task (LDT)

512 participants (mean age 21.1 years, 58% female) completed two sessions each. Each session contained a 200-ms SOA block and a 1,200-ms SOA block (counterbalanced). Each participant responded to 1,661 prime–target trials; half of the word targets were replaced by pronounceable nonwords per participant, resulting in approximately equal numbers of word and nonword trials.

Participants pressed "/" for a real word target and "z" for a nonword target. The `response` column encodes the actual key pressed as "word" or "nonword" (inferred from target accuracy and lexicality).

## exp2.csv — Speeded Naming

256–257 participants (mean age 21.3 years, 59% female) completed two sessions each. The structure was the same as LDT but all targets were real words. Participants named the target aloud into a microphone as quickly and accurately as possible. Naming latency was scored by the computer and manually coded for accuracy. The `response` column contains the experimenter's coding: "correct", "unsure", "mispronunciation", or "extraneous" (e.g., microphone false trigger). Trials flagged as microphone errors (`micerror`) have `rt` set to NaN.

# Prompts

`prompts.jsonl.zip` contains one JSON line per participant:

- **exp1 (LDT)**: yes/no key assignments are randomized per participant. Each trial shows: `Trial N: Cue: 'CUE' → Target: 'target'. You press <<key>>. RT: <<RT>> ms.` Trials with missing RT show `<<not recorded>>`.
- **exp2 (Naming)**: Each trial shows: `Trial N: Cue: 'CUE' → Target: 'target'. Naming time: <<RT>> ms.` Trials with missing RT (microphone error or no detection) show `<<not recorded>>`.

The prime word is referred to as "cue" in both instructions to avoid giving the model meta-knowledge about the semantic priming manipulation. The `rt` field in each JSON entry contains the list of valid (non-NaN) reaction times in milliseconds, in trial order.
