# Schiekiera et al. (2026) - Picture–Word Interference: English Studies

## Citation

```bibtex
@misc{schiekiera2026pwi_dataset,
  title        = {A harmonized trial-level dataset of picture-word interference},
  author       = {Schiekiera, Louis and Abdel Rahman, Rasha and Gruber, Vincent
                  and B{\"u}rki, Audrey and Lorenz, Antje and Stark, Kirsten
                  and G{\"u}nther, Fritz},
  year         = {2026},
  howpublished = {Preprint, PsyArXiv},
  url          = {https://osf.io/preprints/psyarxiv/xp69t_v1}
}
```

## References
- Broos, W. P. J., Duyck, W., & Hartsuiker, R. J. (2018). Are higher-level processes delayed in second language word production? Evidence from picture naming and phoneme monitoring. *Language, Cognition and Neuroscience, 33*(10), 1219–1234. https://doi.org/10.1080/23273798.2018.1457168

- Catling, J. C., Dent, K., Johnston, R. A., & Balding, R. (2010). Age of Acquisition, Word Frequency, and Picture–Word Interference. *Quarterly Journal of Experimental Psychology, 63*(7), 1304–1317. https://doi.org/10.1080/17470210903380830

- Cutting, J. C., & Ferreira, V. S. (1999). Semantic and phonological information flow in the production lexicon. *Journal of Experimental Psychology: Learning, Memory, and Cognition, 25*(2), 318–344. https://doi.org/10.1037/0278-7393.25.2.318

- de Zubicaray, G. I., Hansen, S., & McMahon, K. L. (2013). Differential processing of thematic and categorical conceptual relations in spoken word production. *Journal of Experimental Psychology: General, 142*(1), 131–142. https://doi.org/10.1037/a0028717

- de Zubicaray, G. I., Miozzo, M., Johnson, K., Schiller, N. O., & McMahon, K. L. (2012). Independent Distractor Frequency and Age-of-Acquisition Effects in Picture–Word Interference: fMRI Evidence for Post-lexical and Lexical Accounts according to Distractor Type. *Journal of Cognitive Neuroscience, 24*(2), 482–495. https://doi.org/10.1162/jocn_a_00141

- Freund, M., & Nozari, N. (2018). Is adaptive control in language production mediated by learning? *Cognition, 176*, 107–130. https://doi.org/10.1016/j.cognition.2018.03.009

- Gauvin, H. S., Jonen, M. K., Choi, J., McMahon, K., & De Zubicaray, G. I. (2018). No lexical competition without priming: Evidence from the picture–word interference paradigm. *Quarterly Journal of Experimental Psychology, 71*(12), 2562–2570. https://doi.org/10.1177/1747021817747266

- Hutson, J., & Damian, M. F. (2014). Semantic gradients in picture-word interference tasks: Is the size of interference effects affected by the degree of semantic overlap? *Frontiers in Psychology, 5*. https://doi.org/10.3389/fpsyg.2014.00872

- Mascelloni, M., McMahon, K. L., Piai, V., Kleinman, D., & De Zubicaray, G. (2021). Mediated phonological–semantic priming in spoken word production: Evidence for cascaded processing from picture–word interference. *Quarterly Journal of Experimental Psychology, 74*(7), 1284–1294. https://doi.org/10.1177/17470218211010591

- Muylle, M., & Jarema, G. (2024). The role of orthography and phonology during L1 vs. L2 typed production. *The Mental Lexicon, 19*(1), 100–110. https://doi.org/10.1075/ml.24022.muy

- Sailor, K., Brooks, P. J., Bruening, P. R., Seiger-Gardner, L., & Guterman, M. (2009). Exploring the time course of semantic interference and associative priming in the picture–word interference task. *Quarterly Journal of Experimental Psychology, 62*(4), 789–801. https://doi.org/10.1080/17470210802254383

- Spinelli, G., Perry, J. R., & Lupker, S. J. (2019). Adaptation to conflict frequency without contingency and temporal learning: Evidence from the picture–word interference task. *Journal of Experimental Psychology: Human Perception and Performance, 45*(8), 995–1014. https://doi.org/10.1037/xhp0000656

- Vieth, H. E., McMahon, K. L., & De Zubicaray, G. I. (2014a). Feature overlap slows lexical selection: Evidence from the picture–word interference paradigm. *Quarterly Journal of Experimental Psychology, 67*(12), 2325–2339. https://doi.org/10.1080/17470218.2014.923922

- Vieth, H. E., McMahon, K. L., & De Zubicaray, G. I. (2014b). The roles of shared vs. distinctive conceptual features in lexical access. *Frontiers in Psychology, 5*. https://doi.org/10.3389/fpsyg.2014.01014

- Ward, E., Brownsett, S., McMahon, K. L., & De Zubicaray, G. I. (2021, March 4). *Inter-subject variability in spoken verb production: Effects of hierarchy and transitivity*. https://doi.org/10.31234/osf.io/3wg5j

- Wei, H. T., Hu, Y. Z., Chignell, M., & Meltzer, J. A. (2022). Picture-Word Interference Effects Are Robust With Covert Retrieval, With and Without Gamification. *Frontiers in Psychology, 12*, 825020. https://doi.org/10.3389/fpsyg.2021.825020

- Wei, H. T., Kulzhabayeva, D., Erceg, L., Robin, J., Hu, Y. Z., Chignell, M., & Meltzer, J. A. (2024). Cognitive components of aging-related increase in word-finding difficulty. *Aging, Neuropsychology, and Cognition, 31*(6), 987–1019. https://doi.org/10.1080/13825585.2024.2315774

## Data Source

Aggregated trial-level data from 17 published and unpublished picture–word interference (PWI) studies in English. Original data were collected across multiple laboratories; see individual study references within `original_data/` for provenance details.

## Task Description

In the picture–word interference (PWI) paradigm participants see line drawings of everyday objects while a distractor word is presented simultaneously or at a specific stimulus onset asynchrony (SOA). Their task is either to name the picture aloud (**overt** naming) or to silently retrieve the name and respond via button press (**covert** naming), while ignoring the distractor word. The central dependent variable is reaction time (RT) in milliseconds.

### Prompt template

```
You will see line drawings of everyday objects on the screen. Each picture is shown
together with a [visually presented / auditorily played] distractor word [SOA clause].
Your task is to name the object in the picture aloud as quickly and accurately as
possible, while ignoring the distractor word. [optional setting / familiarization /
gamified / condition clauses]

Trial 1: Picture of a {target_word}; distractor "{distractor_word}" [{condition}].
Response correct. RT: <<{rt}>> ms.
Trial 2: …
```

## Dataset Details

- **Total trials**: 218,075
- **Participants**: 748
- **Studies**: 17
- **Study IDs**: broos_2018, catling_2010, cutting_1999, de_zubicaray_2012, de_zubicaray_2013, freund_2018, gauvin_2018, hutson_2014, mascelloni_2021, muylle_2024, sailor_2009, spinelli_2019, vieth_2014a, vieth_2014b, ward_2021, wei_2022, wei_2024
- **Language**: EN
- **Naming conditions**: overt, covert

## Exclusion Criteria

Trials marked as `technical_error` in the `accuracy` column were removed during preprocessing. Study-specific exclusion criteria (RT cutoffs, accuracy thresholds) are documented in the original publications.

## Notes on Prompts

Participants from `vieth_2014b_experiment3` have unusually long sessions (~2,500 trials). These are split into three records (`_part1` / `_part2` / `_part3`) to stay within the 32,000-token limit. All other over-budget participants are split into two records.

## Files

- `original_data/`: Raw data files from individual studies
- `processed_data/data_english.csv`: Cleaned trial-level data
- `preprocess_data.R`: Preprocessing script
- `generate_prompts.py`: Script to generate LLM prompts (outputs `prompts.jsonl`)
- `prompts.jsonl`: Participant-level prompts
- `CODEBOOK.csv`: Variable descriptions
- `variable_name_mapping.md`: Mapping from pre-merge variable names to final schema
