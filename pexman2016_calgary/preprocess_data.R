# preprocess_data.R
# Calgary Semantic Decision Project (Pexman et al., 2016)
# https://doi.org/10.3758/s13428-016-0720-6
# 312 participants, 10,000 words, ~312,000 trials
# Output: exp1.csv, CODEBOOK
#
# -----------------------------------------------------------------------------

library(tidyverse)
library(openxlsx)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

## Load raw files
items <- read.xlsx("original_data/13428_2016_720_MOESM2_ESM.xlsx")
trials <- read.xlsx("original_data/13428_2016_720_MOESM3_ESM.xlsx")

## Clean item lvl
items_clean <- items %>%
  # Need these two from item lvl
  select(Word, Concrete_rating) %>% 
  # Make lowercase to match files
  mutate(Word = str_to_lower(Word)) %>% 
  # Rename concrete rating
  rename(concrete_rating = Concrete_rating)

## Clean trial lvl
trials_clean <- trials %>%
  # All to character to catch all weird NAs
  mutate(across(everything(), as.character)) %>%
  # Clean NAs
  mutate(across(everything(), ~na_if(., "#NULL!"))) %>%
  # Make lowercase to match files
  mutate(Word = str_to_lower(Word)) %>%
  # Make trial id for each participant
  group_by(Participant) %>%
  mutate(trial_id = row_number() - 1) %>%
  ungroup()

## Merge items to trials
df <- trials_clean %>%
  left_join(items_clean, by = "Word")

## Rename and Recode
# Rename
df <- df %>%
  rename(
    participant_id = Participant,
    stimulus       = Word,
    accuracy       = Word.ACC,
    rt             = RTclean,
    rt_raw         = RTraw,
    rt_zscore      = zRTclean,
    trial_order    = FullRunOrder,
    list_order     = ListRunOrder,
    phase_id       = TrialBlock,
    age            = Age,
    gender         = Gender,
    list           = VersionNum,
    naart_score    = NAART,
    ehi_score      = EHI,
    ehi_class      = EHI_LRA,
    response       = ResponseAC,
    prev_rt        = prevtrialRT,
    prev_acc       = prevtrialACC
  ) %>%
  mutate(
    # Characters back to integers
    participant_id = as.integer(participant_id),
    accuracy  = as.integer(accuracy),
    rt       = as.integer(rt),
    rt_raw   = as.integer(rt_raw),
    age      = as.integer(age),
    list     = as.integer(list),
    prev_acc = as.integer(prev_acc),
    # Recode condition 
    condition = case_when(
      WordTypeAC == "C" ~ "concrete",
      WordTypeAC == "A" ~ "abstract",
    ),
    # Rename blocks
    phase_id = case_when(
      phase_id == 1 ~ "block_1",
      phase_id == 2 ~ "block_2",
      phase_id == 3 ~ "block_3",
      phase_id == 4 ~ "block_4",
    ),
    # RT outliers (when raw RT exists but clean RT is missing it means trial was recorded but excluded)
    is_rt_outlier = !is.na(rt_raw) & is.na(rt),
  )

## All together
df <- df %>%
  select(
    participant_id, age, gender, naart_score, ehi_score, ehi_class,
    trial_id, trial_order, list_order, list, phase_id,
    condition, stimulus, accuracy, rt, response,
    is_rt_outlier, rt_raw, rt_zscore,
    prev_rt, prev_acc, concrete_rating
  ) %>%
  arrange(participant_id, trial_id)

## Save as csv
dir.create("processed_data")
write_csv(df, "processed_data/exp1.csv", na = "")

## Update codebook
# Read codebook
codebook <- read_csv("../CODEBOOK.csv")

# Rename and change descriptions
colnames(codebook) <- c("column_name", "description")
codebook$description[codebook$column_name == "list"]     <- "Experimental list number (1-10)."
codebook$description[codebook$column_name == "response"] <- "A=abstract, C=concrete, T=timed out."
codebook$description[codebook$column_name == "trial_order"] <- "Sequential position of the trial in the full experiment (25-1024; 1-24 absent as those were practice trials)."
codebook$description[codebook$column_name == "phase_id"] <- "Experimental block (block_1 to block_4). Each block contains 250 trials. Mandatory 3-minute break after block_2."

# New variables
new_codebook <- data.frame(
  column_name = c("concrete_rating", "naart_score", "ehi_score", "ehi_class", 
                  "rt_raw", "rt_zscore", "list_order", "prev_rt", "prev_acc"),
  description = c(
    "Mean concreteness rating from Brysbaert et al. (2013) norms (scale 1-5; 1=abstract to 5=concrete).",
    "Participant score on the North American Adult Reading Test (NAART35; Uttl 2002). Index of vocabulary and verbal ability.",
    "Raw score on the Edinburgh Handedness Inventory (-100=fully left-handed to +100=fully right-handed).",
    "Handedness classification derived from EHI score (L=left-handed, R=right-handed, A=ambidextrous). Used to assign response hand per condition.",
    "Raw unprocessed response time for the trial in milliseconds, before any cleaning or outlier removal.",
    "Z-scored RT within each participant x block. Minimizes influence of individual differences in processing speed.",
    "Sequential position of the trial within its assigned list (1-250).",
    "Cleaned RT (ms) on the immediately preceding trial. NA if previous trial was incorrect or an outlier.",
    "Accuracy on the immediately preceding trial (1=correct, 0=incorrect/timed-out/NA). Used for post-error slowing control."
  )
)

# Add new codebook
codebook <- rbind(codebook, new_codebook)

# Delete if not in df
codebook <- codebook %>% 
  filter(column_name %in% names(df))

# Save as csv
write_csv(codebook, "CODEBOOK.csv")
