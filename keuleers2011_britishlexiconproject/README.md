# British Lexicon Project (BLP)

This folder contains the standardized preprocessing scripts and LLM prompts for the **British Lexicon Project**, contributed to the PsychLing-101 database.

## Citation
Keuleers, E., Lacey, P., Rastle, K., & Brysbaert, M. (2012). The British Lexicon Project: Lexical decision data for 28,730 monosyllabic and disyllabic English words. *Behavior Research Methods*, 44(1), 287–304. https://doi.org/10.3758/s13428-011-0118-4

## Data Source
The raw trial-level data was obtained from the official OSF repository:
[https://osf.io/b5sdk/files/84efq](https://osf.io/b5sdk/files/84efq)

## Preprocessing Notes
The raw `blp-trials.txt` file was processed to align with the PsychLing-101 `CODEBOOK.csv`. To accommodate the 32,000 token limit during prompt generation, the 28,000+ trials per participant were effectively chunked into smaller blocks while maintaining the chronological order and instructions of the original lexical decision task.