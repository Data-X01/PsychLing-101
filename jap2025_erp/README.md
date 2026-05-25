# jap2025_indonesian_verb_bias_erp

## Citation

Jap, B. A. J., & Hsu, Y.-Y. (2025). An ERP study on verb bias and thematic
role assignment in standard Indonesian. *Scientific Reports*, *15*, 11847.
https://doi.org/10.1038/s41598-025-96240-y

## Data source

Original data publicly available on OSF:
https://osf.io/g96va/

## Description

ERP study investigating how verb-bias information (active-bias vs. passive-bias
verbs) affects thematic role assignment during sentence comprehension in
Standard Indonesian (Bahasa Indonesia). Participants read sentences in three
conditions — Active, Agent-Before Passive (AB_Passive), and Patient-Before
Passive (PB_Passive) — presented word-by-word via RSVP (500 ms/word), while
64-channel EEG was recorded. Yes/no comprehension probes appeared after a
subset of trials.

ERP amplitudes (N400 and P600) were extracted at three critical word positions:
the main VERB (position 3), the post-verbal adverb ADV (position 4), and the
head noun of the second argument NP (NP2_w2, position 6).

## Structure

- `original_data/`  — raw per-participant amplitude CSVs (E01–E45)
- `processed_data/exp1.csv` — standardised trial-level ERP data (122,535 rows)
- `processed_data/prompts.jsonl.zip` — PsychLing-101 LLM prompts (45 participants)
- `preprocess_data.py` — preprocessing script
- `generate_prompts.py` — prompt generation script
- `CODEBOOK.csv` — variable descriptions

## Participants

45 adult speakers of Standard Indonesian (Bahasa Indonesia).

## Stimuli & Design

**200 experimental trials per participant**, drawn from:
- 30 active-bias verbs × 2 NP-role versions (patient-before / agent-before) → 60 passive sentences
- 30 passive-bias verbs × 2 NP-role versions → 60 passive sentences  
- 80 active-voice sentences (one active version per verb, counterbalanced)

Each verb appears **once per participant** in exactly one condition via a Latin-square
counterbalancing scheme across two lists (List 1: E01–E22; List 2: E23–E45).
This means the same verb-stem can generate different surface sentences across
participants (e.g., *NP-agent ditampar oleh NP-patient* vs. *NP-patient ditampar
oleh NP-agent*), resulting in **159 unique sentence surface forms** across the
full dataset.

Sentence structure for all experimental items:
`NP1 [itu] VERB ADV [oleh] NP2 PP`
- Active:      NP1 = Agent, VERB = active (meN-), NP2 = Patient
- AB_Passive:  NP1 = Agent-role NP, VERB = passive (di-), NP2 = Patient-role NP (reversed)
- PB_Passive:  NP1 = Patient-role NP, VERB = passive (di-), NP2 = Agent-role NP

ERP targets (marked `is_erp_target = 1`): VERB, ADV, NP2_w2

## ERP components

| Component | Time window | Electrode cluster |
|-----------|-------------|-------------------|
| N400 | 300–500 ms | Centroparietal |
| P600 | 500–800 ms | Centroparietal |