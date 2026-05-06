# =============================================================================
# preprocess_data.R
# PsychLing-101 preprocessing script for German PWI studies.
# Reads original_data/, applies feature engineering and column renaming,
# writes processed_data/data_german.csv.
# =============================================================================
rm(list = ls())

library(dplyr)
library(here)

here::i_am("preprocess_data.R")

# ---------------------------------------------------------------------------
# 1. Load German data from original_data/
# ---------------------------------------------------------------------------
de_files <- list.files(
  path    = here("original_data"),
  pattern = "^full_data_summarized_data_german_.*\\.csv$",
  full.names = TRUE
)
if (length(de_files) == 0) {
  stop("No full_data_summarized_data_german_*.csv found in original_data/.")
}
newest <- de_files[which.max(file.info(de_files)$mtime)]
df <- read.csv(newest, stringsAsFactors = FALSE)

# ---------------------------------------------------------------------------
# 2. Feature engineering
# ---------------------------------------------------------------------------
df$categorical_relation  <- df$categorical_relatedness
df$associative_relation  <- df$associative_relatedness
df$phonological_relation <- df$phonological_relatedness

df$distractor_modality <- case_when(
  df$context_type %in% c("auditory", "speech") ~ "audio",
  df$context_type %in% c(
    "text(superimposed)", "superimposed",
    "visual", "text (superimposed)"
  ) ~ "text",
  TRUE ~ df$context_type
)

df$familiarization    <- ifelse(df$familiarization == "yes", "yes", "no")
df$naming_condition   <- ifelse(df$pwi_type == "overt", "overt", "covert")
df$is_gamified          <- "no"
df$collection_setting   <- ifelse(df$setting == "online", "online", "offline")
df$has_additional_tasks <- ifelse(df$further_tasks == "yes", "yes", "no")

df$first_language <- "German"
df$exp_language <- "DE"

# ---------------------------------------------------------------------------
# 3. Study ID normalization
# ---------------------------------------------------------------------------
df$study_id <- case_when(
  df$experiment %in% c("jescheniak_2024_experiment1",
                       "jescheniak_2024_experiment2")                  ~ "jescheniak_2024",
  df$experiment %in% c("jescheniak_2024b_experiment1",
                       "jescheniak_2024b_experiment2",
                       "jescheniak_2024b_experiment3",
                       "jescheniak_2024b_experiment4")                 ~ "jescheniak_2024b",
  df$experiment %in% c("kurtz_2018_experiment1", "kurtz_2018_experiment2",
                       "kurtz_2018_experiment3")                       ~ "kurtz_2018",
  df$experiment %in% c("müller_2020_experiment1", "müller_2020_experiment2",
                       "müller_2020_experiment3")                      ~ "müller_2020",
  df$experiment == "mädebach_2018_Exp.1"                              ~ "mädebach_2018",
  df$experiment %in% c("Social_PWI_Exp-1", "Social_PWI_Exp-2",
                       "Social_PWI_Exp-3")                             ~ "social_pwi",
  df$experiment %in% c("PWI_Online_1", "PWI_Online_2",
                       "PWI_Online_3")                                 ~ "pwi_online",
  df$experiment %in% c("wöhner_2023_exp_01", "wöhner_2023_exp_02",
                       "wöhner_2023_exp_03", "wöhner_2023_exp_04",
                       "wöhner_2023_exp_05",
                       "wöhner_2023_exp_06")                           ~ "wöhner_2023",
  TRUE ~ df$experiment
)

replacements_de <- c(
  "EmoBlock_PWI"        = "abdel_rahman_unpublished_1_eeg",
  "PWI_COMP_EEG"        = "abdel_rahman_unpublished_2_comp",
  "PWI_Assblocking_neu" = "abdel_rahman_unpublished_3_ass",
  "PWI_Button_Press"    = "abdel_rahman_unpublished_4_button",
  "Aristei.2010"        = "aristei_2010",
  "Aristei.2013"        = "aristei_2013",
  "bürki_2022"          = "burki_2022",
  "Damian.2014.visible" = "damian_2014",
  "Jescheniak_2020"     = "jescheniak_2020",
  "mädebach_2018"       = "madebach_2018",
  "mädebach_2022"       = "madebach_2022",
  "müller_2020"         = "muller_2020",
  "social_pwi"          = "kuhlen_2022",
  "pwi_online"          = "vogt_2022",
  "wöhner_2023"         = "wohner_2023",
  "PWI1_Age"            = "lorenz_2018",
  "Ageing_PWI_double"   = "lorenz_2019",
  "Control_PWI_EEG"     = "lorenz_2021",
  "Control_PWI_EEG_AGE" = "lorenz_unpublished1_control_eeg_age",
  "PWI_EEG_AGE"         = "lorenz_unpublished2_eeg_age",
  "PWI1_CONTROL"        = "lorenz_unpublished3_control"
)
df$study_id <- ifelse(
  df$study_id %in% names(replacements_de),
  replacements_de[df$study_id], df$study_id
)
df$experiment <- ifelse(
  df$experiment %in% names(replacements_de),
  replacements_de[df$experiment], df$experiment
)
df$participant <- ifelse(
  df$participant %in% names(replacements_de),
  replacements_de[df$participant], df$participant
)

# Normalize sub-experiment IDs whose raw names don't get caught by
# replacements_de (multi-experiment studies routed via case_when above,
# plus umlaut-bearing experiment-level names).
experiment_id_normalizations_de <- c(
  "Social_PWI_Exp-1"       = "kuhlen_2022_experiment1",
  "Social_PWI_Exp-2"       = "kuhlen_2022_experiment2",
  "Social_PWI_Exp-3"       = "kuhlen_2022_experiment3",
  "PWI_Online_1"           = "vogt_2022_experiment1",
  "PWI_Online_2"           = "vogt_2022_experiment2",
  "PWI_Online_3"           = "vogt_2022_experiment3",
  "mädebach_2018_Exp.1"    = "madebach_2018_experiment1",
  "müller_2020_experiment1" = "muller_2020_experiment1",
  "müller_2020_experiment2" = "muller_2020_experiment2",
  "müller_2020_experiment3" = "muller_2020_experiment3",
  "wöhner_2023_exp_01"     = "wohner_2023_exp_01",
  "wöhner_2023_exp_02"     = "wohner_2023_exp_02",
  "wöhner_2023_exp_03"     = "wohner_2023_exp_03",
  "wöhner_2023_exp_04"     = "wohner_2023_exp_04",
  "wöhner_2023_exp_05"     = "wohner_2023_exp_05",
  "wöhner_2023_exp_06"     = "wohner_2023_exp_06"
)
df$experiment <- ifelse(
  df$experiment %in% names(experiment_id_normalizations_de),
  experiment_id_normalizations_de[df$experiment], df$experiment
)

# ---------------------------------------------------------------------------
# 4. Exclude technical errors; convert accuracy to binary
# ---------------------------------------------------------------------------
df <- df %>%
  filter(is.na(accuracy) | accuracy != "technical_error")

df$accuracy <- ifelse(
  is.na(df$accuracy), NA_integer_,
  ifelse(df$accuracy == "correct", 1L, 0L)
)

# ---------------------------------------------------------------------------
# 5. Final column selection — PsychLing-101 schema
# ---------------------------------------------------------------------------
df <- df %>%
  transmute(
    study_id,
    experiment_id            = experiment,
    participant_id           = sub(".*_([^_]+)$", "\\1", participant),
    trial_order              = trial - 1L,
    target_word_pwi              = target,
    distractor_word_pwi          = context,
    rt,
    accuracy,
    exp_language,
    first_language,
    familiarization,
    soa                      = SOA,
    naming_condition,
    has_additional_tasks,
    is_gamified,
    collection_setting,
    congruency,
    categorical_relation,
    associative_relation,
    phonological_relation,
    distractor_modality
  )

# ---------------------------------------------------------------------------
# 6. Write output
# ---------------------------------------------------------------------------
dir.create(here("processed_data"), showWarnings = FALSE)
out_path <- here("processed_data", "data_german.csv")
write.csv(df, out_path, row.names = FALSE)
message("data_german.csv written to ", out_path)
message("Rows: ", nrow(df), " | Participants: ",
        length(unique(df$participant_id)),
        " | Studies: ", length(unique(df$study_id)))
