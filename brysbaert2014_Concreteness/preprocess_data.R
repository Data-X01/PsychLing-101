### Preprocess Data from: Brysbaert, M., Warriner, A.B., & Kuperman, V. (2014).
# Concreteness ratings for 40 thousand generally known English word lemmas.
# Behavior Research Methods, 46(3), 904–911.
# https://doi.org/10.3758/s13428-013-0403-5
#
# Raw data source: https://osf.io/qpmf4/
### Niklas Jung 
### 04/2026


library(dplyr)
library(readr)
library(tibble)
library(stringr)

## read data 

# original data must be in same dir
stopifnot("original_data" %in% list.files())

load("original_data/concreteness_trial.rda")


df_raw <- concreteness.participant

df <- df_raw %>%
  rename(
    participant_id     = Worker_code,        # anonymized ID — this is the real one
    age                = Answer.QAge,
    gender             = Answer.QGender,
    education          = Answer.QEducation,
    first_language     = Answer.QLang,
    handedness         = Answer.QHand,
    state_raised       = Answer.QRaised,     # US state before age 7
    stimulus           = Word,
    response           = Rating,
    session_duration_s = WorkTimeInSeconds
  ) %>%
  # Drop raw MTurk ID (privacy) and approval rate columns (infrastructure)
  select(-WorkerId,
         -LifetimeApprovalRate,
         -Last30DaysApprovalRate,
         -Last7DaysApprovalRate)


# Handle "n"/"N" = participant didn't know the word
df <- df %>%
  mutate(
    country_of_residence = "US", 
    word_known = if_else(response %in% c("n", "N"), FALSE, TRUE)
  )



# fix spelling differences in first_language (ALL have english as first language)
english_variants <- c(
  "English", "english", "ENGLISH", "Eglish", "ENglish", "Englsih",
  "English5", "English-", "eNGLISH", "Engish", "Englis", "Engllish",
  "nglish", "englidh", "Englisih", "Enlish", "englis", "Enlgish",
  "English,", "enlish", "Englishq", "American English", "ENGLLISH",
  "enlgish", "english5", "Englisg", "english ny", "english ph",
  "english californion", "englih", "Emglish", "Englosh", "Englishh",
  "eng", "Englilsh", "English (American)", "engllsh", "Engilsh",
  "\"English,", "Englis5", "american english", "Wnglish", "Elglish",
  "englosh"
)

df <- df %>%
  mutate(first_language = if_else(first_language %in% english_variants, 
                                  "English", 
                                  first_language))


df <- df %>%
  mutate(
    age = str_remove(age, "\\s*years?"),  # remove "years" / "year"
    age = as.numeric(age),
    age = if_else(age < 16 | age > 120, NA_real_, age)  # implausible values → NA
  )


### Add if teh word is normal trial or calibrator or control word

calibrator_words <- c("shirt", "Inf", "gas", "grasshopper", "marriage", 
                      "kick", "polite", "whistle", "theory", "sugar")

control_words <- c("adolescence", "aspect", "banality", "bottle", "cold",
                   "diving", "equanimity", "fishing", "fourth", "gnat",
                   "grisly", "harpsichord", "heroin", "impossible", "lathe",
                   "loquacity", "milk", "mist", "monument", "pen",
                   "pineapple", "saddle", "same", "science", "sigh",
                   "snap", "sock", "sympathy", "tumble")

df <- df %>%
  mutate(word_type = case_when(
    stimulus %in% calibrator_words ~ "calibrator",
    stimulus %in% control_words    ~ "control",
    TRUE                           ~ "normal"
  ))

# Add trial_order per participant
# -----------------------------------------------------------------------------
# The raw data has no explicit trial order column; we derive it from row
# position within each participant's session.


df <- df %>%
  arrange(participant_id) %>%
  group_by(participant_id) %>%
  mutate(
    session_id = ceiling(row_number() / 339)
  ) %>%
  ungroup()



#  Basic validation

#  Every row should have a stimulus
missing_stimulus <- sum(is.na(df$stimulus))
if (missing_stimulus > 0) {
  warning(missing_stimulus, " rows with missing stimulus. Inspect before proceeding.")
}

# 5c. Summary
message("\n--- Processed data summary ---")
message("Rows            : ", nrow(df))
message("Participants    : ", n_distinct(df$participant_id))
message("Unique stimuli  : ", n_distinct(df$stimulus))

## write df to processed_data

write_csv(df, file = "processed_data/exp1.csv")


# write codebook as csv for this study
write_codebook <- function(base_dir) {
  codebook_path <- file.path(base_dir, "CODEBOOK.csv")
  
  if (file.exists(codebook_path)) return(invisible(NULL))
  
  rows <- tribble(
    ~column_name,        ~description,
    "participant_id",    "Anonymized participant ID (derived from Worker_code)",
    "age",               "Participant age in years (from Answer.QAge)",
    "gender",            "Self-reported gender: Female / Male / Unspecified (from Answer.QGender)",
    "education",         "Highest completed education level (from Answer.QEducation)",
    "first_language",    "Participant's self-reported language(s) (from Answer.QLang)",
    "handedness",        "Participant's dominant hand: Left / Right / Unspecified (from Answer.QHand)",
    "country_of_residence", "Country of residence (all US, state specified in next var",
    "state_raised",      "US state where participant lived most of the time before age 7 (from Answer.QRaised)",
    "session_duration_s","Time in seconds between accepting and submitting the MTurk assignment (from WorkTimeInSeconds)",
    "stimulus",          "Stimulus word presented to the participant (from Word)",
    "response",          "Concreteness rating 1-5, or N / n for unknown (see new variable word_known)",
    "word_known",        "FALSE if participant indicated they did not know the word (Rating was 'n' or 'N')",
    "word_type",         "Is trial part of control word or calibrator (that everyone gets)",
    "session_id",        "Participants could do the task multiple times. Each one is noted by session_id (max (90)."
  )
  
  write_csv(rows, codebook_path)
  message("CODEBOOK.csv written to: ", codebook_path)
}

# Usage:
write_codebook("F:/PsychLing/PsychLing-101/brysbaert2014_Concreteness")
