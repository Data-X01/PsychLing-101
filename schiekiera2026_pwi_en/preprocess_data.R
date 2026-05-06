# =============================================================================
# preprocess_data.R
# PsychLing-101 preprocessing script for English PWI studies.
# Reads original_data/, applies feature engineering and column renaming,
# writes processed_data/data_english.csv.
# =============================================================================
rm(list = ls())

library(dplyr)
library(here)

here::i_am("preprocess_data.R")

# ---------------------------------------------------------------------------
# 1. Load English data from original_data/
# ---------------------------------------------------------------------------
en_files <- list.files(
  path    = here("original_data"),
  pattern = "^full_data_summarized_data_english_.*\\.csv$",
  full.names = TRUE
)
if (length(en_files) == 0) {
  stop("No full_data_summarized_data_english_*.csv found in original_data/.")
}
newest <- en_files[which.max(file.info(en_files)$mtime)]
df <- read.csv(newest, stringsAsFactors = FALSE)

# ---------------------------------------------------------------------------
# 2. Feature engineering
# ---------------------------------------------------------------------------
df$categorical_relation  <- df$categorical_relatedness
df$associative_relation  <- df$associative_relatedness
df$phonological_relation <- df$phonological_relatedness

df$distractor_modality <- case_when(
  df$context_type == "speech" ~ "audio",
  df$context_type %in% c(
    "text(superimposed)", "text above/below the picture",
    "superimposed", "text (superimposed)"
  ) ~ "text",
  TRUE ~ df$context_type
)

df$familiarization    <- ifelse(df$familiarization == "yes", "yes", "no")
df$naming_condition   <- ifelse(df$pwi_type == "overt", "overt", "covert")
df$is_gamified          <- ifelse(df$pwi_type == "covert_gamified", "yes", "no")
df$collection_setting   <- ifelse(df$setting == "online", "online", "offline")
df$has_additional_tasks <- ifelse(df$further_tasks == "yes", "yes", "no")

# Derive first_language from `language` before overwriting it
df$first_language <- case_when(
  df$language == "English (Dutch native speakers)"  ~ "Dutch",
  df$language == "English (French native speakers)" ~ "French",
  TRUE ~ "English"
)
df$exp_language <- "EN"

# ---------------------------------------------------------------------------
# 3. Study ID normalization
# ---------------------------------------------------------------------------
df$study_id <- case_when(
  df$experiment %in% c("broos_2018_exp_phoneme_monitoring",
                       "broos_2018_exp_picture_naming")               ~ "broos_2018",
  df$experiment %in% c("de_zubicaray_2011_experiment1_AoA",
                       "de_zubicaray_2011_experiment2_FREQ")           ~ "de_zubicaray_2012",
  df$experiment %in% c("freund_2018_experiment1",
                       "freund_2018_experiment2")                      ~ "freund_2018",
  df$experiment %in% c("mascelloni_2021_experiment1_auditory",
                       "mascelloni_2021_experiment2_written")          ~ "mascelloni_2021",
  df$experiment %in% c("muylle_2024_exp1_L1_speaker",
                       "muylle_2024_exp2_L2_speaker")                  ~ "muylle_2024",
  df$experiment %in% c("vieth_2014a_experiment1",
                       "vieth_2014a_experiment2")                      ~ "vieth_2014a",
  df$experiment %in% c("vieth_2014b_experiment1", "vieth_2014b_experiment2",
                       "vieth_2014b_experiment3")                      ~ "vieth_2014b",
  df$experiment == "ward_2021_exp.1"                                   ~ "ward_2021",
  df$experiment %in% c("wei_2022_experiment1", "wei_2022_experiment1_game",
                       "wei_2022_experiment2", "wei_2022_experiment2_game",
                       "wei_2022_experiment3", "wei_2022_experiment3_game",
                       "wei_2022_experiment4", "wei_2022_experiment4_game") ~ "wei_2022",
  df$experiment %in% c("Cutting.1999.1", "Cutting.1999.2",
                       "Cutting.1999.3a.1", "Cutting.1999.3a.2")       ~ "cutting_1999",
  df$experiment %in% c("Gauvin.2018.1.fam", "Gauvin.2018.1.nofam",
                       "Gauvin.2018.2.fam", "Gauvin.2018.2.nofam")     ~ "gauvin_2018",
  df$experiment %in% c("Hutson.2014.1", "Hutson.2014.2")              ~ "hutson_2014",
  df$experiment %in% c("Sailor.2009.Exp1.150", "Sailor.2009.Exp1.minus150",
                       "Sailor.2009.Exp1.minus450", "Sailor.2009.Exp2.0",
                       "Sailor.2009.Exp2.300",
                       "Sailor.2009.Exp2.minus300")                    ~ "sailor_2009",
  TRUE ~ df$experiment
)

replacements_en <- c(
  "deZubicaray.2013" = "de_zubicaray_2013",
  "wouter_2018"      = "broos_2018"
)
df$study_id <- ifelse(
  df$study_id %in% names(replacements_en),
  replacements_en[df$study_id], df$study_id
)
df$experiment <- ifelse(
  df$experiment %in% names(replacements_en),
  replacements_en[df$experiment], df$experiment
)
df$participant <- ifelse(
  df$participant %in% names(replacements_en),
  replacements_en[df$participant], df$participant
)

# Normalize sub-experiment IDs that the raw data stored in CamelCase.dot
# format. The replacements_en vector above only covers study-level IDs;
# these four studies arrive with granular per-experiment values that need
# their own mapping.
experiment_id_normalizations <- c(
  "Cutting.1999.1"             = "cutting_1999_experiment1",
  "Cutting.1999.2"             = "cutting_1999_experiment2",
  "Cutting.1999.3a.1"          = "cutting_1999_experiment3a_1",
  "Cutting.1999.3a.2"          = "cutting_1999_experiment3a_2",
  "Gauvin.2018.1.fam"          = "gauvin_2018_experiment1_fam",
  "Gauvin.2018.1.nofam"        = "gauvin_2018_experiment1_nofam",
  "Gauvin.2018.2.fam"          = "gauvin_2018_experiment2_fam",
  "Gauvin.2018.2.nofam"        = "gauvin_2018_experiment2_nofam",
  "Hutson.2014.1"              = "hutson_2014_experiment1",
  "Hutson.2014.2"              = "hutson_2014_experiment2",
  "Sailor.2009.Exp1.150"       = "sailor_2009_experiment1_soa150",
  "Sailor.2009.Exp1.minus150"  = "sailor_2009_experiment1_soa_minus150",
  "Sailor.2009.Exp1.minus450"  = "sailor_2009_experiment1_soa_minus450",
  "Sailor.2009.Exp2.0"         = "sailor_2009_experiment2_soa0",
  "Sailor.2009.Exp2.300"       = "sailor_2009_experiment2_soa300",
  "Sailor.2009.Exp2.minus300"  = "sailor_2009_experiment2_soa_minus300",
  "ward_2021_exp.1"            = "ward_2021_experiment1",
  "de_zubicaray_2011_experiment1_AoA"  = "de_zubicaray_2012_experiment1_AoA",
  "de_zubicaray_2011_experiment2_FREQ" = "de_zubicaray_2012_experiment2_FREQ"
)
df$experiment <- ifelse(
  df$experiment %in% names(experiment_id_normalizations),
  experiment_id_normalizations[df$experiment], df$experiment
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
out_path <- here("processed_data", "data_english.csv")
write.csv(df, out_path, row.names = FALSE)
message("data_english.csv written to ", out_path)
message("Rows: ", nrow(df), " | Participants: ",
        length(unique(df$participant_id)),
        " | Studies: ", length(unique(df$study_id)))
