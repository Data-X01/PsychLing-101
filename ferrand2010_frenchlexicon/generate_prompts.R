# =============================================================================
# generate_prompts.R
# -----------------------------------------------------------------------------
# Adapted from the guenther2023ViSpa pipeline 
# French Lexicon Project (Ferrand et al., 2010)
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

EXPERIMENT_NAME <- "ferrand2010frenchlexicon"

# Instructions from paper
INSTRUCTION <- "Dans cet exercice, une série de chaînes de lettres vous sera présentée. 
Pour chaque chaîne, vous devez déterminer, le plus rapidement et le plus précisément possible, s'il s'agit d'un vrai mot de la langue française ou non.
Appuyez sur le bouton « oui » si la chaîne de lettres correspond à un vrai mot.
Appuyez sur le bouton « non » si la chaîne de lettres ne correspond pas à un vrai mot."

# Trial sentence template. `%s` placeholders are filled with the response (oui, non)
TRIAL_TEMPLATE <- "Essai %d : Le mot est « %s ». Vous appuyez sur <<%s>>.\n"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

# Build JSON manually so separators match Python's json.dumps output
# String escaping handled by jsonlite
format_jsonl_line <- function(text, experiment, participant_id, rt) {
  paste0(
    '{"text": ',            toJSON(text,           auto_unbox = TRUE),
    ', "experiment": ',     toJSON(experiment,     auto_unbox = TRUE),
    ', "participant_id": ', toJSON(participant_id, auto_unbox = TRUE),
    ', "rt": ',             toJSON(as.integer(rt), auto_unbox = FALSE),
    '}'
  )
}

# Build the full prompt for one participant: instruction + replay of trials.
build_participant_prompt <- function(df_participant, trial_indices) {
  
  prompt <- INSTRUCTION
  for (trial in trial_indices) {
    row <- df_participant[df_participant$trial_id == trial, , drop = FALSE]
    if (nrow(row) > 0) {
      prompt <- paste0(prompt, sprintf(TRIAL_TEMPLATE, trial + 1, row$stimulus, row$response))
    }
  }
  paste0(prompt, "\n")
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main <- function() {
  df <- read_csv("processed_data/exp1.csv", show_col_types = FALSE)

  df <- df[order(df$participant_id, df$trial_id), , drop = FALSE]
  df$participant_id <- match(df$participant_id, unique(df$participant_id))
  
  participants <- unique(df$participant_id)
  trial_indices <- 0:max(df$trial_id)
  
  con <- file("prompts.jsonl", open = "wb")
  on.exit(close(con), add = TRUE)
  
  # loop over sessions to make 2 shorter prompts per participant 
  for (p in participants) {
    for (s in c("session_1", "session_2")) {
      df_p   <- df[df$participant_id == p & df$session_id == s, , drop = FALSE]
      prompt <- build_participant_prompt(df_p, trial_indices)
      line   <- format_jsonl_line(prompt, EXPERIMENT_NAME, p, df_p$rt)
      writeLines(line, con, sep = "\n")
    }
  }
  
  zip("prompts.jsonl.zip", "prompts.jsonl")
  file.remove("prompts.jsonl")
  cat("Done. Written", length(participants)*2, "prompts to prompts.jsonl.zip\n")
}

if (sys.nframe() == 0) {
  main()
}
