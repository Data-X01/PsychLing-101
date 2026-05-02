# preprocess_data.R
# French Lexicon Project (Ferrand et al., 2010)
# https://doi.org/10.3758/BRM.42.2.488
# 974 participants, 38,840 words + 38,840 nonwords, ~1,950,000 trials
# Output: processed_data/exp1.csv, CODEBOOK.csv
#
# -----------------------------------------------------------------------------

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

library(archive)
library(data.table)
library(tidyverse)

## Load raw file
archive_extract("original_data/results.tt.rar", dir = "original_data")

df <- fread("original_data/results.tt.txt", 
               encoding = "Latin-1", 
                 fill = TRUE, 
                sep = "auto")

##Clean data
# Delete V7-8
df <- df %>% select(-V7, -V8)

# Rename 
df <- df %>%
  rename(
    participant_id = V1,
    item_id = V2,
    stimulus = V3,
    rt = V4,
    accuracy = V5,
    condition  = V6,
    )

# Fix Encoding
df <- df %>% mutate(stimulus = iconv(stimulus, from = "latin1", to = "UTF-8"))

# Fix broken rows
df <- df %>%
  mutate(condition = if_else(stimulus %in% c("choque", "conducteurs", "rêvez", "quelles", "hebdo") & 
                               !condition %in% c("mot", "nonmot"), "mot", condition))

## Add variables
# Response 
df <- df %>%
  mutate(response = case_when(
    accuracy == 1 & condition == "mot" ~ "oui",
    accuracy == 1 & condition == "nonmot" ~ "non",
    accuracy == 0 & condition == "mot"~ "non",
    accuracy == 0 & condition == "nonmot" ~ "oui"
  ))

# Rt outliers and rt_zscore
df <- df %>%
  group_by(participant_id) %>%
  mutate(rt_zscore = (rt - mean(rt)) / sd(rt)) %>%
  ungroup() %>%
  mutate(is_rt_outlier = rt < 200 | rt > 2000 | abs(rt_zscore) > 3)

# Trial id for each participant
df <- df %>% 
  group_by(participant_id) %>%
  mutate(trial_id = row_number() - 1) %>%
  ungroup()

# Session id for each participant
df <- df %>%
  group_by(participant_id) %>%
  mutate(session_id = if_else(row_number() <= 1000, "session_1", "session_2")) %>%
  ungroup()

# Phase id for each participant
df <- df %>%
  group_by(participant_id) %>%
  mutate(phase_id = case_when(
    row_number() <= 250 ~ "block_1",
    row_number() <= 500 ~ "block_2",
    row_number() <= 750 ~ "block_3",
    row_number() <= 1000 ~ "block_4",
    row_number() <= 1250 ~ "block_5",
    row_number() <= 1500 ~ "block_6",
    row_number() <= 1750 ~ "block_7",
    row_number() <= 2000 ~ "block_8"
  )) %>%
  ungroup()

## All together
df <- df %>%
  select(participant_id, trial_id, phase_id, 
         session_id, item_id, condition, stimulus, 
         response, accuracy, rt, rt_zscore, is_rt_outlier) %>%
  arrange(participant_id, trial_id)

## Save as csv
dir.create("processed_data")
write_csv(df, "processed_data/exp1.csv", na = "")

## Update codebook
# Read codebook
codebook <- read_csv("../CODEBOOK.csv")
colnames(codebook) <- c("column_name", "description")

# Update existing descriptions
codebook$description[codebook$column_name == "phase_id"] <- "Experimental block of 250 trials (block_1 to block_8 across two sessions) seperated by 5-min breaks."
codebook$description[codebook$column_name == "condition"] <- "Stimulus type: mot = word, nonmot = nonword"
codebook$description[codebook$column_name == "is_rt_outlier"] <- "Flag RT outliers like in the paper: RT < 200 ms, RT > 2000 ms, or rt-zscore > 3."
codebook$description[codebook$column_name == "response"] <- "Participant's response (Is the stimulus a word?): oui = yes, non = no "

# New variables
new_codebook <- data.frame(
  column_name = c("item_id", "session_id", "rt_zscore"),
  description = c(
    "Unique identifier for each stimulus item.",
    "Experimental session (session_1 or session_2). Sessions were run on different days separated by no more than 1 week.",
    "Z-scored RT within each participant. Minimizes influence of individual differences in processing speed."
  )
)

# Add new codebook
codebook <- rbind(codebook, new_codebook)

# Delete if not in df
codebook <- codebook %>%
  filter(column_name %in% names(df))

# Save as csv
write_csv(codebook, "CODEBOOK.csv")
