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

# save data ---------------------------------------------------------------

write_csv(data_clean, file = here("exp1.csv"))

# -------------------------------------------------------------------------