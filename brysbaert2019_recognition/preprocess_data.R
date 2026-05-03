### Preprocess Data from: Brysbaert, M., Keuleers, E., & Mandera, P. (2019).
# Recognition Times for 54 Thousand Dutch Words: Data from the Dutch
# Crowdsourcing Project. Psychologica Belgica, 59(1), 281–300.
# https://doi.org/10.5334/pb.491
#
# Raw data source: https://osf.io/5fk8d/
### Niklas Jung
### 04/2026

library(osfr)
library(vroom)
library(dplyr)
library(readr)
library(tibble)

# retrieve the project
project <- osf_retrieve_node("5fk8d")

# list all files
files <- osf_ls_files(project)
#print(files)

# download the tar.gz file
osf_download(files[files$name == "dutch-raw-data.tar.gz", ], path = ".")

untar("dutch-raw-data.tar.gz", exdir = "original_data")
list.files("original_data", recursive = TRUE)

df_raw <- vroom("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/lexical-decision.csv")

df_participant <- vroom("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/profiles.csv")

df_session <- vroom("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/sessions.csv")

meta_data_full <- merge(df_session, df_participant, by = "profile_id")

meta_data <- meta_data_full %>% 
  select(exp_id, gender, age, native_language, handedness) %>%
  mutate(gender = case_when(
    gender == "f" ~ "Female", 
    gender == "m" ~ "Male", 
    .default = gender
  ), 
  native_language = case_when(
    native_language == "Nederlands" ~ "Dutch", 
    .default = native_language
  ),
  handedness = case_when(
    handedness == "l" ~ "Left", 
    handedness == "r" ~ "Right"
  )
  )

df_raw_p <- merge(df_raw, meta_data, by = "exp_id")

#for testing on smaller data
#df_raw <- df_raw %>% slice_sample(n = 100000)

df <- df_raw_p %>%
  rename(
    participant_id = exp_id,
    stimulus       = spelling, 
    first_language = native_language
  ) %>%
  # keep only raw rt
  select(participant_id, gender, age, first_language, handedness, trial_order, stimulus, lexicality, response, rt, accuracy)


## Preprocessing

df <- df %>%
  # remove implausibly slow trials (paper threshold: 8000ms)
  filter(rt <= 8000 & rt > 0)


message("\n--- Processed data summary ---")
message("Rows            : ", nrow(df))
message("Participants    : ", n_distinct(df$participant_id))
message("Unique stimuli  : ", n_distinct(df$stimulus))

## Write to processed_data

if (file.exists("dutch-raw-data.tar.gz")) {
  file.remove("dutch-raw-data.tar.gz")
  message("Removed!")
} else {
  message("File not found")
}

write_csv(df, file = "processed_data/exp1.csv")



zip("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/lexical-decision.zip", "original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/lexical-decision.csv")

    
    # Then remove the original if you want
    if (file.exists("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/lexical-decision.csv") & file.exists("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/lexical-decision.zip")) {
      file.remove("original_data/dutch-vocabtest-20131203-cleaned-native.lang.nl/lexical-decision.csv") }
    
zip("processed_data/exp1.zip", "processed_data/exp1.csv" )

# Then remove the original if you want
if (file.exists("processed_data/exp1.csv") & file.exists("processed_data/exp1.zip")) {
  file.remove("processed_data/exp1.csv")
}
## Write codebook

write_codebook <- function(base_dir) {
  codebook_path <- file.path(base_dir, "CODEBOOK.csv")
  
  if (file.exists(codebook_path)) return(invisible(NULL))
  
  rows <- tribble(
    ~column_name,    ~Description,
    "participant_id","Session-level identifier (from exp_id); each participant may have multiple sessions",
    "gender",        "Gender (Male/Female/NA)",
    "age",           "Age (numeric)",
    "first_language","first language (dutch for all participants)",
    "handedness",    "Dominant Hand (Left/Right/NA)",
    "trial_order",   "Position of the trial within the session (0-indexed)",
    "stimulus",      "Dutch word or nonword presented to the participant (from spelling)",
    "lexicality",    "Whether the stimulus is a real word (W) or nonword (N) (from lexicality)",
    "response",      "Participant's response: W (word) or N (nonword)",
    "rt",            "Response time in milliseconds from stimulus onset to response",
    "accuracy",      "Whether the response was correct (1) or incorrect (0)"
  )
  
  write_csv(rows, codebook_path)
  message("CODEBOOK.csv written to: ", codebook_path)
}

write_codebook("/mnt/home/njung")
