#
#   Script written by Courtney Hilton on April 30, 2026
#   Preprocesses raw data in accordance with PsychLing101 requirements
#
# libraries ---------------------------------------------------------------

library(tidyverse)
library(here)

# load and format data ----------------------------------------------------

participant_ids <- sprintf("%03d", 1:40)

data_clean <- map(participant_ids, \(.participant_id) {
  participant_info <- read_tsv(here("original_data", paste0(.participant_id, "participant_info.txt")), col_types = "ccccci") |> 
    select(
      participant_id = Participant,
      handedness = Handedness,
      gender = Gender,
      first_language = Native_language,
      age = Age
    )
  
  trial_info <- read_tsv(here("original_data", paste0(.participant_id, "trial_log.txt")), col_types = "icccccccid") |> 
    select(
      trial_id = Trial,
      condition = Congruency,
      stimulus = Sentence,
      sentence_extraction = Sentence_extraction,
      comprehension_probe = Probe,
      probe_clause = Probe_clause,
      response = Response,
      accuracy = Accuracy,
      rt = RT
    )
    
  return( bind_cols(trial_info, participant_info) )
}) |> 
  list_c() |> 
  mutate(
    gender = case_when(
      gender == "F" ~ "female",
      gender == "f" ~ "female",
      gender == "Female" ~ "female",
      gender == "Male" ~ "male",
      gender == "M" ~ "male",
      gender == "m" ~ "male",
      .default = gender
    ),
    first_language = case_when(
      first_language == "english" ~ "English",
      first_language == "Eng" ~ "English",
      first_language == "dutch" ~ "Dutch",
      first_language == "hebrew" ~ "Hebrew",
      .default = first_language
    ),
    # NOTE: this wasn't explicitly part of the data, but fluency in English was a participation requirement
    # that was screened prior to the experiment so it can be inferred.
    other_languages = case_when(
      first_language == "Dutch" ~ "English (Fluent)",
      first_language == "Hebrew" ~ "English (Fluent)",
      .default = NA
    ),
    handedness = case_when(
      handedness == "Right" ~ "right",
      handedness == "R" ~ "right",
      handedness == "r" ~ "right",
      handedness == "L" ~ "left",
      handedness == "Left" ~ "left",
      .default = handedness
    ),
    # NOTE: this wasn't explicitly part of the original data, but as the experimenter 
    # of the original study I can confidently say all participants were at that time
    # residents in Australia
    country_of_residence = "Australia"
  )

annotate_stresses <- function(s, start = 2, step = 3) {
  # parse string into vector
  x <- strsplit(gsub("\\[|\\]|'", "", s), ",\\s*")[[1]]
  
  # apply transformation
  idx <- seq(start, length(x), by = step)
  x[idx] <- toupper(x[idx])
  
  # reassemble back to original format
  paste0("['", paste(x, collapse = "', '"), "']")
}

data_clean <- data_clean |> 
  rowwise() |> 
  mutate(
    stimulus = case_when(
      condition == "congruent" & sentence_extraction == "object" ~ capitalize_every_n_string(stimulus, start = 2, step = 3),
      condition == "incongruent" & sentence_extraction == "object" ~ capitalize_every_n_string(stimulus, start = 1, step = 3),
      condition == "congruent" & sentence_extraction == "subject" ~ capitalize_every_n_string(stimulus, start = 2, step = 2),
      condition == "incongruent" & sentence_extraction == "subject" ~ capitalize_every_n_string(stimulus, start = 1, step = 2),
      condition == "other" ~ capitalize_every_n_string(stimulus, start = 2, step = 2),
      .default = stimulus
    )
  )



# save data ---------------------------------------------------------------

write_csv(data_clean, file = here("processed_data", "exp1.csv"))

# -------------------------------------------------------------------------