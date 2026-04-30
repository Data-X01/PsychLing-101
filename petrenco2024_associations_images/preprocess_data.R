# ------------------------------------------------------------
# 1. Rename variables according to the CODEBOOK.csv
# ------------------------------------------------------------
rm(list = ls())  # clear environment

library(readr)
library(tidyverse)

dat <- as.data.frame(read_csv("original_data/raw_data.csv"))

# rename variables according to the CODEBOOK.csv 
codebook <- as.data.frame(read_csv("CODEBOOK.csv"))

dat <- dat %>% 
  rename(
    participant_id = "participant",
    first_language = "language",
    phase_id = "type",
    condition = "label_cond",
    list = "listname",
    stimulus1_image = "internal_name",
    stimulus2_label = "label_word",
    image_filename = "picture",
    response ="critical",
    response_corrected = "critical_new",
    response_order = "resp.order"
    ) %>% 
  mutate(stimulus2_present = if_else(is.na(stimulus2_label), "no", "yes"))


#reorder columns
dat <- dat %>% 
  select(participant_id, age, gender, first_language, 
         trial_order, phase_id, condition, list, 
         stimulus1_image, stimulus2_label, stimulus2_present, 
         image_filename,
         response, response_corrected, response_order)


#change to trial-level wide format (one row per trial, with separate columns for critical1, critical2, and critical3)

dat_wide <- dat %>%
  pivot_wider(
    id_cols = c(
      participant_id, age, gender, first_language,
      trial_order, phase_id, condition, list,
      stimulus1_image, stimulus2_label, stimulus2_present,
      image_filename
    ),
    names_from = response_order,
    values_from = response_corrected,
    values_fn = \(x) x[1],   # handle duplicates
    names_prefix = "response",
    names_transform = list(response_order = ~ gsub("critical", "", .x))
  )

# save the preprocessed data
write_csv(dat_wide, "processed_data/tidy_data.csv")


# ------------------------------------------------------------
# 1. Build base codebook from ALL dataset variables
# ------------------------------------------------------------

codebook_tidy <- tibble(
  `Recommended Column Name` = names(dat)
)

# ------------------------------------------------------------
# 2. Join old descriptions where they exist
# ------------------------------------------------------------

codebook_tidy <- codebook_tidy %>%
  left_join(codebook, by = "Recommended Column Name")

# ------------------------------------------------------------
# 3. Define NEW variables manually (only missing ones)
# ------------------------------------------------------------

new_descriptions <- tibble(
  `Recommended Column Name` = c(
    "stimulus1_image",
    "stimulus2_label",
    "stimulus2_present",
    "response_order"
  ),
  Description = c(
    "Which image was presented",
    "Which label (if any) was presented under the image",
    "Whether stimulus 2 (label) was present (yes/no)",
    "The order of the responses the participant made"
  )
)

# ------------------------------------------------------------
# 4. Merge new definitions into codebook
# ------------------------------------------------------------

codebook_tidy <- codebook_tidy %>%
  left_join(new_descriptions, by = "Recommended Column Name") %>%
  mutate(
    Description = coalesce(Description.y, Description.x)
  ) %>%
  select(`Recommended Column Name`, Description)

# ------------------------------------------------------------
# 5. Save final codebook
# ------------------------------------------------------------

write_csv(codebook_tidy, "processed_data/codebook_tidy.csv")






# ------------------------------------------------------------
# CREATE FILTERED CODEBOOK WITH SAME STRUCTURE AS ORIGINAL
# ------------------------------------------------------------

# get renamed variable mapping (old -> new)
name_map <- tibble::tibble(
  old_name = c(
    "participant",
    "language",
    "type",
    "label_cond",
    "listname",
    "internal_name",
    "label_word",
    "picture",
    "critical",
    "critical_new",
    "resp.order"
  ),
  new_name = c(
    "participant_id",
    "first_language",
    "phase_id",
    "condition",
    "list",
    "stimulus1_image",
    "stimulus2_label",
    "image_filename",
    "response",
    "response_corrected",
    "response_order"
  )
)

# keep only relevant rows from old codebook
codebook_tidy <- codebook %>%
  filter(`Recommended Column Name` %in% names(dat))

# save
write_csv(codebook_tidy, "processed_data/codebook.csv")

