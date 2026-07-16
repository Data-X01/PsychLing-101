# =============================================================================
# generate_prompts.R
# -----------------------------------------------------------------------------
# Adapted from the guenther2023ViSpa pipeline 
# Calgary Semantic Decision Project (Pexman et al., 2016)
#
# Reads processed/exp1.csv and writes one JSON prompt per participant to prompts.jsonl.zip
#
# =============================================================================

library(tidyverse)
library(jsonlite)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

# -----------------------------------------------------------------------------
# INSTRUCTION
# -----------------------------------------------------------------------------

EXPERIMENT_NAME <- "pexman2016calgary"

# Instructions from paper
INSTRUCTION <- "In this task, you will see a series of words presented one at a time. For each word, you need to decide whether it refers to something concrete or abstract.
Concrete words are defined as things or actions in reality, which you can experience directly through your senses. These words are experience-based. Night, bridle, and lynx are examples of concrete words.
Abstract words are defined as something you cannot experience directly through your senses or actions. These words are language-based, as their meaning depends on other words. Have, limitation, and outspokenness are examples of abstract words.
Note that words are not restricted to nouns — verbs and adjectives can also be concrete or abstract."

# Feedback for incorrect responses and timeouts
TRIAL_CORRECT   <- "Trial %d: The word is '%s'. You press <<%s>>.\n"
TRIAL_INCORRECT <- "Trial %d: The word is '%s'. You press <<%s>>. Incorrect.\n"
TRIAL_TIMEOUT   <- "Trial %d: The word is '%s'. No response detected.\n"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

# Build JSON manually so separators match Python's json.dumps output
# String escaping handled by jsonlite
format_jsonl_line <- function(text, experiment, participant_id, rt, age, gender) {
  paste0(
    '{"text": ',            toJSON(text,           auto_unbox = TRUE),
    ', "experiment": ',     toJSON(experiment,     auto_unbox = TRUE),
    ', "participant_id": ', toJSON(participant_id, auto_unbox = TRUE),
    ', "rt": ',             toJSON(as.integer(rt), auto_unbox = FALSE, na = "null"),
    ', "age": ',            toJSON(as.integer(age), auto_unbox = TRUE, na = "null"),
    ', "gender": ',         toJSON(as.character(gender), auto_unbox = TRUE, na = "null"),
    '}'
  )
}

# Build the full prompt for one participant: instruction + replay of trials.
build_participant_prompt <- function(df_participant, trial_indices) {
  
  # Dominant hand for this participant
  dominant_hand <- df_participant$ehi_class[1]
  
  if (dominant_hand == "R") {
    concrete_hand <- "right"
    abstract_hand <- "left"
  } else if (dominant_hand == "L") {
    concrete_hand <- "left"
    abstract_hand <- "right"
  } else {
    # Ambidextrous (so preferred writing hand)
    concrete_hand <- "dominant"
    abstract_hand <- "non-dominant"
  }
  # Add instruction based on handedness
  instruction <- paste0(
    INSTRUCTION,
    sprintf("Press the %s button for concrete words and the %s button for abstract words.\n\n",
            concrete_hand, abstract_hand)
  )
  
  prompt <- instruction
  for (trial in trial_indices) {
    row <- df_participant[df_participant$trial_id == trial, , drop = FALSE]
    if (nrow(row) > 0) {
      if (is.na(row$response) || row$response == "T") {
        prompt <- paste0(prompt, sprintf(TRIAL_TIMEOUT, trial + 1, row$stimulus)) # Trial info + feedback if timeout or no response 
      } else if (row$accuracy == 1L) {
        response_hand <- ifelse(row$response == "C", concrete_hand, abstract_hand)
        prompt <- paste0(prompt, sprintf(TRIAL_CORRECT, trial + 1, row$stimulus, response_hand)) # Trial info + no feedback if response correct
      } else {
        response_hand <- ifelse(row$response == "C", concrete_hand, abstract_hand)
        prompt <- paste0(prompt, sprintf(TRIAL_INCORRECT, trial + 1, row$stimulus, response_hand)) # Trial info + feedback if not correct
      }
    }
  }  
  paste0(prompt, "\n")
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main <- function() {
  df <- read_csv("processed_data/exp1.csv", show_col_types = FALSE)

  df <- df[order(df$participant_id, df$trial_order), , drop = FALSE]
  df$participant_id <- match(df$participant_id, unique(df$participant_id))
  
  participants <- unique(df$participant_id)
  trial_indices <- 0:max(df$trial_id)
  
  con <- file("prompts.jsonl", open = "wb")
  
  for (p in participants) {
    df_p   <- df[df$participant_id == p, , drop = FALSE]
    prompt <- build_participant_prompt(df_p, trial_indices)
    line   <- format_jsonl_line(prompt, EXPERIMENT_NAME, p,
                                df_p$rt, df_p$age[1], df_p$gender[1])
    writeLines(line, con, sep = "\n")
  }
  
  close(con) # manually because it omitted the last participant when done like in guenther script
  zip("prompts.jsonl.zip", "prompts.jsonl")
  file.remove("prompts.jsonl")
  cat("Done. Written", length(participants), "prompts to prompts.jsonl.zip\n")
}

if (sys.nframe() == 0) {
  main()
}
