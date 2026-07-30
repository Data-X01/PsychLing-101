# ------------------------------------------------------------
# 1. Rename variables according to the CODEBOOK.csv
# ------------------------------------------------------------
rm(list = ls())  # clear environment

library(readr)
library(tidyverse)

df <- as.data.frame(read_csv("original_data/raw_data.csv"))

df <- df %>% 
  #filter(!is.na(critical_new)) %>% 
  rename(
    participant_id = "participant",
    first_language = "language",
    condition = "label_cond",
    list = "listname",
    stimulus1_image = "internal_name",
    stimulus2_label = "label_word",
    image_filename = "picture",
    response = "critical",
    response_order = "resp.order"
    ) %>% 
  mutate(stimulus2_present = if_else(is.na(stimulus2_label), "no", "yes")) %>%
  distinct(participant_id, stimulus1_image, response_order, .keep_all = TRUE)


# reorder columns
df <- df %>% 
  select(participant_id, age, gender, first_language, 
         trial_order, condition, list, trial_order,
         stimulus1_image, image_filename,
         stimulus2_label, stimulus2_present, 
         response, response_order)


#change to trial-level wide format (one row per trial, with separate columns for critical1, critical2, and critical3)
df_wide <- df %>%
  mutate(response_order = gsub("critical", "", response_order)) %>%   
  pivot_wider(
    id_cols = c(participant_id, age, gender, first_language, 
                condition, list, trial_order,
                stimulus1_image, image_filename,
                stimulus2_label, stimulus2_present),
    names_from = response_order,
    values_from = response,
    names_prefix = "response",
    values_fn = first        # <-- take first value if duplicates exist
  ) %>%
  relocate(response1, response2, response3, .after = stimulus2_present)

# save the preprocessed data
write_csv(df_wide, "processed_data/exp1.csv")

# ------------------------------------------------------------
# 2. Create a codebook
# ------------------------------------------------------------

codebook <- data.frame(
  `Column Name` = c(
    "participant_id",
    "age",
    "gender",
    "first_language",
    
    "condition",
    "list",
    "trial_order",
    
    "stimulus1_image",
    "image_filename",
    "stimulus2_label",
    "stimulus2_present",
    
    "response"
    
  ),
  Description = c(
    "Unique identifier assigned to each participant.",
    "Age of the participant at the time of the experiment.",
    "Self-reported gender identity of the participant.",
    "Participant's native language.",
    
    "Experimental condition assigned to the trial (positive label/negative label/no label).",
    "Experimental list number (0-2). Items were distributed across 3 lists.",
    "Presentation order within the session (0-23). The order in which the participant saw this trial.",
    
    "Which image was presented.",
    "Filename or identifier for the presented image.",
    "Which label (if any) was presented under the image.",
    "Whether stimulus 2 (label) was present (yes/no) under the image.",

    "Participant's response. Each participant produced 3 associations for a given stimulus (an image with or witout a label under it)."
  ),
  check.names = FALSE
)

# save
write_csv(codebook, "CODEBOOK.csv")

