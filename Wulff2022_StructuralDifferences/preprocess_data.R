# Dependencies -----------------------------------------------------------------

install.packages("tidyverse")
library(tidyverse)

# Read raw data ----------------------------------------------------------------

study1_fluency <- read_csv("original_data/Study1_Fluency.csv")
study2_fluency <- read_csv("original_data/Study2_Fluency.csv")
study2_similarity <- read_csv("original_data/Study2_SimRatings.csv")

codebook <- read_csv("../CODEBOOK.csv")

# Convert study data -----------------------------------------------------------

exp1 <- study1_fluency |> 
  rename(
    participant_id = id,
    stimulus = cat,
    rt = time,
    response = word,
    response_corrected = correct,
    trial_order = round,
    participant_age_group = group, # new
    gender = sex
  ) |> 
  mutate(trial_order = trial_order - 1) |> 
  mutate(
    participant_age_group = if_else(
      participant_age_group == "young", "younger", "older"
    )
  )

exp2 <- study2_fluency |> 
  rename(
    participant_id = id,
    rt = time,
    response = word,
    response_corrected = correct,
    participant_age_group = group,
    gender = sex
  ) |> 
  mutate(
    participant_age_group = if_else(
      participant_age_group == "young", "younger", "older"
    )
  )

exp3 <- study2_similarity |> 
  rename(
    participant_id = id,
    participant_age_group = group,
    gender = sex,
    phase_id = part,
    stimulus_pair_id = pair_id,
    rt = time,
    response = rating,
    stimulus_left = left_word,
    stimulus_right = right_word,
    stimulus_is_reversed = rev
  ) |> 
  mutate(
    participant_age_group = if_else(
      participant_age_group == "young", "younger", "older"
    )
  ) |> 
  mutate(rt = rt * 1000) |> # convert to milliseconds
  select(-c(norm_rating, pair, revPair)) # remove redundant variables

# Create own codebook.csv ------------------------------------------------------

to_keep <- unique(c(names(exp1), names(exp2), names(exp3)))

codebook_own <- codebook |> 
  rename(column_name = `Recommended Column Name`, description = Description) |> 
  filter(column_name %in% to_keep)

new_cols <- to_keep[!(to_keep %in% codebook_own$column_name)]
new_descriptions <- c(
    "Age group label: younger or older",
    "Unique id of the stimulus pair.",
    "Word (animal) presented on the left side of the rating screen.",
    "Word (animal) presented on the right side of the rating screen.",
    "In retest phase, is this stimulus reversed (TRUE), or not (FALSE). NA in test phase."
  )

codebook_own <- codebook_own |> 
  bind_rows(tibble(column_name = new_cols, description = new_descriptions))

# Export processed files -------------------------------------------------------

codebook_own |> write_csv("codebook.csv")
exp1 |> write_csv("processed_data/exp1.csv")
exp2 |> write_csv("processed_data/exp2.csv")
exp3 |> write_csv("processed_data/exp3.csv")





