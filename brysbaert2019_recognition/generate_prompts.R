# Generate Prompts for:
# Brysbaert, M., Keuleers, E., & Mandera, P. (2019).
# Recognition Times for 54 Thousand Dutch Words: Data from the Dutch
# Crowdsourcing Project. Psychologica Belgica, 59(1), 281–300.
# https://doi.org/10.5334/pb.491
#
# Raw data source: https://osf.io/5fk8d/

## Niklas Jung
## 04/2026

library(dplyr)
library(jsonlite)
library(readr)

exp1 <- read_csv("processed_data/exp1.csv")

instructions <- "In this test you get 100 letter sequences, some of which are existing Dutch words and some of which are made-up nonwords. Indicate for each letter sequence whether it is a word you know or not. The test takes about 4 minutes and you can repeat it as often as you want (you will get new letter sequences each time). If you take part, you consent to your data being used for scientific analysis of word knowledge. Do not say yes to words you do not know, because yes-responses to nonwords are penalized heavily!"


exp1 <- exp1 %>%
  mutate(response = case_when(
    response == "W" ~ "word",
    response == "N" ~ "nonword",
    TRUE ~ response
  ))
# Build trial text per row (vectorized)
exp1 <- exp1 %>%
  mutate(trial_text = paste0(
    "The letter sequence is '", stimulus, "'. ",
    "You respond <<", response, ">> after <<", rt, ">> ms.\n"
  ))

# Collapse all trials per session in one summarise
prompts_df <- exp1 %>%
  arrange(participant_id, trial_order) %>%
  group_by(participant_id) %>%
  summarise(
    text     = paste0(instructions, paste0(trial_text, collapse = "")),
    gender = first(gender),
    age = first(age), 
    first_language = first(first_language), 
    handedness = first(handedness),
    .groups  = "drop") %>%
  mutate(experiment = "brysbaert2019_recognition")
         

## Check token usage
prompts_df %>%
  mutate(
    n_chars          = nchar(text),
    n_tokens_approx  = n_chars / 4
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

# Zip it
zip("prompts.jsonl.zip", "prompts.jsonl")
