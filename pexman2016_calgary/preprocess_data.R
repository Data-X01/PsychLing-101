# preprocess_data.R
# Calgary Semantic Decision Project (Pexman et al., 2016)
# https://doi.org/10.3758/s13428-016-0720-6
# 312 participants, 10,000 words, ~312,000 trials
# Output: exp1.csv, CODEBOOK
#  
# -------------------------------------------------------------------------

library(tidyverse)
library(openxlsx)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

## Load the raw Excel files ---------------------------------------------
items <- read.xlsx("original_data/13428_2016_720_MOESM2_ESM.xlsx")
trials <- read.xlsx("original_data/13428_2016_720_MOESM3_ESM.xlsx")

## Clean the Item Data (Word Ratings) -----------------------------------
items_clean <- items %>%
  # Basic cleaning (extra spaces and make lowercase to match both files)
  mutate(
    Word = str_to_lower(str_trim(Word)),
    concrete_rating = as.numeric(Concrete_rating)
  ) %>%
  # We only need these two columns for our project
  select(Word, concrete_rating) %>%
  # Remove duplicates just in case
  distinct(Word, .keep_all = TRUE)

## Clean the Trial Data ------------------------------------------------
trials_clean <- trials %>%
  # Put everything to character first so we can search for "#NULL!"
  mutate(across(everything(), as.character)) %>%
  # Excel often imports empty cells as "#NULL!" or "", let's fix that first
  mutate(across(everything(), ~na_if(., "#NULL!"))) %>%
  mutate(across(everything(), ~na_if(., ""))) %>%
  
  # Normalize Word column so it matches our items list
  mutate(Word = str_to_lower(str_trim(Word))) %>%
  
  # Make trial_id for each participant
  group_by(Participant) %>%
  mutate(trial_id = row_number() - 1) %>%
  ungroup()

## Merge the Word Ratings into the Trials -------------------------------
df <- trials_clean %>%
  left_join(items_clean, by = "Word")

## Rename and Recode ---------------------------------------------------
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
   
    # Convert character to numbers
    participant_id = as.integer(participant_id),
    accuracy  = as.integer(accuracy),
    rt       = as.integer(rt),
    rt_raw   = as.integer(rt_raw),
    age      = as.integer(age),
    list     = as.integer(list),
    prev_acc = as.integer(prev_acc),

    # Recode experimental condition
    condition = case_when(
      WordTypeAC == "C" ~ "concrete",
      WordTypeAC == "A" ~ "abstract",
      TRUE ~ NA_character_
    ),
    
    # Clean up gender 
    gender = case_when(
      gender %in% c("M", "MALE", "Male", "m") ~ "M",
      gender %in% c("F", "FEMALE", "Female", "f") ~ "F",
      gender %in% c("O", "OTHER", "Other", "o") ~ "O",
      TRUE ~ NA_character_
    ),
    
    # Rename blocks to make it clearer
    phase_id = case_when(
      phase_id == 1 ~ "block_1",
      phase_id == 2 ~ "block_2",
      phase_id == 3 ~ "block_3",
      phase_id == 4 ~ "block_4",
      TRUE ~ NA_character_
    ),
    
    # RT outliers (when raw RT exists but clean RT is missing it means trial was recorded but excluded)
    is_rt_outlier = !is.na(rt_raw) & is.na(rt),
    
    # Fix response (replaced "0" with NA)
    response = if_else(response == "0", NA_character_, response)
  )

## Final Organization ----------------------------------------------------
df <- df %>%
  select(
    participant_id, age, gender, naart_score, ehi_score, ehi_class,
    trial_id, trial_order, list_order, list, phase_id,
    condition, stimulus, accuracy, rt, response,
    is_rt_outlier, rt_raw, rt_zscore,
    prev_rt, prev_acc, concrete_rating
  ) %>%
  arrange(participant_id, trial_id)

## Save as csv ------------------------------------------------------
dir.create("processed_data", showWarnings = FALSE)
write_csv(df, "processed_data/exp1.csv", na = "")

## Update codebook -------------------------------------------------------

# Descriptions
new_codebook_entries <- data.frame(
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

# Read existing codebook
codebook <- read_csv("../CODEBOOK.csv", show_col_types = FALSE)

# Rename and change descriptions
colnames(codebook) <- c("column_name", "description")
codebook$description[codebook$column_name == "list"]     <- "Experimental list number (1-10)."
codebook$description[codebook$column_name == "response"] <- "A=abstract, C=concrete, T=timed out."
codebook$description[codebook$column_name == "trial_order"] <- "Sequential position of the trial in the full experiment (25-1024; 1-24 absent as those were practice trials)."
codebook$description[codebook$column_name == "phase_id"] <- "Experimental block (block_1 to block_4). Each block contains 250 trials. Mandatory 3-minute break after block_2."

# Add new codebook rows
codebook <- rbind(codebook, new_codebook_entries)

# Delete rows that are not in df
codebook <- codebook %>% 
  filter(column_name %in% names(df))

# Save as csv
write_csv(codebook, "CODEBOOK.csv")



##### List_order redundant, remove it? ######




