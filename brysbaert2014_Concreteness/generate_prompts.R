# Generate Pormpts for: 
# Brysbaert, M., Warriner, A.B., & Kuperman, V. (2014).
# Concreteness ratings for 40 thousand generally known English word lemmas.
# Behavior Research Methods, 46(3), 904–911.
# https://doi.org/10.3758/s13428-013-0403-5
#
# Raw data source: https://osf.io/qpmf4/

## Niklas Jung
## 04/2026

library(dplyr)
library(jsonlite)
library(readr)

exp1 <- read_csv("processed_data/exp1.csv")

instructions <- "Some words refer to things or actions in reality, which you can experience directly through one of the five senses. We call these words concrete words. Other words refer to meanings that cannot be experienced directly but which we know because the meanings can be defined by other words. These are abstract words. Still other words fall in-between the two extremes, because we can experience them to some extent and in addition we rely on language to understand them. We want you to indicate how concrete the meaning of each word is for you by using a 5-point rating scale going from abstract to concrete. A concrete word comes with a higher rating and refers to something that exists in reality; you can have immediate experience of it through your senses (smelling, tasting, touching, hearing, seeing) and the actions you do. The easiest way to explain a word is by pointing to it or by demonstrating it (e.g. To explain 'sweet' you could have someone eat sugar; To explain 'jump' you could simply jump up and down or show people a movie clip about someone jumping up and down; To explain 'couch', you could point to a couch or show a picture of a couch). An abstract word comes with a lower rating and refers to something you cannot experience directly through your senses or actions. Its meaning depends on language. The easiest way to explain it is by using other words (e.g. There is no simple way to demonstrate 'justice'; but we can explain the meaning of the word by using other words that capture parts of its meaning). Because we are collecting values for all the words in a dictionary (over 60 thousand in total), you will see that there are various types of words, even single letters. Always think of how concrete (experience based) the meaning of the word is to you. In all likelihood, you will encounter several words you do not know well enough to give a useful rating. This is informative to us too, as in our research we only want to use words known to people. We may also include one or two fake words which cannot be known by you. Please indicate when you don't know a word by using the letter N (or n). So, we ask you to use a 5-point rating scale going from abstract to concrete and to use the letter N when you do not know the word well enough to give an answer."

# Build trial text per row first (vectorized)
exp1 <- exp1 %>%
  mutate(trial_text = if_else(
    !word_known,
    paste0("The word is '", stimulus, "'. Rate the word on a Likert-Scale from 1 to 5 (1,2,3,4,5) with 1 refering to most abstract (language based) and 5 refering to the most concrete (experience based). N means that you dont know the word well enough to give a rating.
 You respond <<N>>. \n"),
    paste0("The word is '", stimulus, "'. Rate the word on a Likert-Scale from 1 to 5 (1,2,3,4,5) with 1 refering to most abstract (language based) and 5 refering to the most concrete (experience based). N means that you dont know the word well enough to give a rating.
 You respond <<", response, ">>.\n")
  ))

# Then collapse all trials per participant in one summarise
prompts_df <- exp1 %>%
  arrange(participant_id, session_id) %>%
  group_by(participant_id, session_id) %>%
  summarise(
    text = paste0(instructions, paste0(trial_text, collapse = "")),
    age  = first(age),
    gender = first(gender),
    education = first(education), 
    country_of_residence = first(country_of_residence),
    first_language = first(first_language),
    
    .groups = "drop"
  ) %>%
  mutate(experiment = "brysbaert2014_concreteness")


## check how many tokens used
prompts_df %>%
  mutate(
    n_chars  = nchar(text),
    n_tokens_approx = n_chars / 4
  ) %>%
  summarise(
    min_tokens  = min(n_tokens_approx),
    max_tokens  = max(n_tokens_approx),
    mean_tokens = mean(n_tokens_approx),
    over_32k    = sum(n_tokens_approx > 32000)
  )

# Write to JSONL
con <- file("prompts.jsonl", "w")
for (i in seq_len(nrow(prompts_df))) {
  writeLines(toJSON(as.list(prompts_df[i, ]), auto_unbox = TRUE), con)
}
close(con)


# test jsonl output
#lines <- readLines("prompts.jsonl")
#parsed <- lapply(lines, fromJSON)



# Zip it
zip("prompts.jsonl.zip", "prompts.jsonl")
