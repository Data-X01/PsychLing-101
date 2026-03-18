# aguasvivas2018_spalex

## Citation
Aguasvivas, J., Carreiras, M., Brysbaert, M., Mandera, P., Keuleers, E., & Duñabeitia, J. A. (2018).
SPALEX: A Spanish Lexical Decision Database From a Massive Online Data Collection.
*Frontiers in Psychology*, 9, 2156. https://doi.org/10.3389/fpsyg.2018.02156

## Data source
https://www.frontiersin.org/articles/10.3389/fpsyg.2018.02156/full

## Description
Large-scale Spanish lexical decision dataset collected online.
Participants saw Spanish letter strings one at a time and decided
whether each was a real word (W) or a nonword (NW).

## Paradigm
Lexical decision task (Spanish)

## Key variables
- participant: participant ID (exp_id in original data)
- trial: trial number within participant session
- stimulus: Spanish letter string shown
- condition: word / nonword
- rt: reaction time in milliseconds
- correct: 1 = correct response, 0 = incorrect

## Participants
227,655 participants, 22,765,418 trials total

## Notes
- Raw data encoded as UTF-8
- Trials with missing accuracy or RT were excluded
- Original column `lexicality` (W/NW) mapped to `condition` (word/nonword)
