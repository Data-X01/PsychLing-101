# Reference:
Guasch, M., Boada, R., Duñabeitia, J. A., & Ferré, P. (2023). Prevalence norms for 40,777 Catalan words: An online megastudy of vocabulary size. Behavior Research Methods, 55, 3198–3217. https://doi.org/10.3758/s13428-022-01959-5

# Data source:
https://doi.org/10.6084/m9.figshare.16622536.v3

# Description
- Participants judged whether each of the 120 letter strings in a session corresponded to a word they knew in Catalan, or whether it was a pseudoword. Responses were binary (“yes”/“no”).
- The dataset comprises 24,557,400 data points, with 120 trials per session across 204,645 sessions, including 40,777 distinct Catalan words and 30,243 pseudowords. In each session, a 70/30 ratio was used (i.e., 84 words and 36 pseudowords).
- The dataset includes sociolinguistic information about participants.

# CODEBOOK Deviations
This dataset includes variables that differ from the standard PsychLing-101 CODEBOOK in naming or definition:
session_id,Unique identifier assigned to each experimental session.
device,Type of input device used (e.g., touch device or keyboard).
sex,Biological sex of the participant.
raising,Place where the participant spent their early childhood.
education,Highest level of education completed or currently in progress.
proficiency,Self-reported proficiency in Catalan, with values ranging from 1 (none) to 7 (native-like).
age_first_contact,Age at which the participant was first exposed to Catalan.
mother_language,Language spoken by the participant’s mother.
father_language,Language spoken by the participant’s father.
exposure,Self-reported proportion of daily exposure to Catalan, ranging from 0 (never) to 100 (always), measured in 10-point increments.
n_languages,Number of languages the participant reports speaking, including Catalan (from 1 to 7 or more).
trial_order,Sequential order of trial presentation within each participant, ranging from 1 to 120.
is_word,Binary indicator of whether the stimulus is a real Catalan word (1) or a pseudoword (0).