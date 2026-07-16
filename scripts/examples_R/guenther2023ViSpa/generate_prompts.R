# =============================================================================
# generate_prompts.R
# -----------------------------------------------------------------------------
# Native-R port of guenther2023ViSpa/generate_prompts.py.
#
# Reads the tidy per-trial CSV written by preprocess_data.R and produces one
# narrative prompt per participant, serialized as JSONL (one JSON object per
# line) for downstream LLM evaluation.
#
# Pipeline:
#   processed_data/exp1.csv
#     |
#     v
#   prompts.jsonl
#     each line: {"text": <prompt>, "experiment": "guenther2023ViSpa",
#                 "participant_id": <int>}
#
# Each participant's prompt consists of:
#   1. The task instructions shown to the human participant
#   2. A chronological replay of the participant's trials, one line per trial,
#      phrased as "Which look the most similar? ... You choose <<X>> ..."
#
# Usage:
#   Rscript generate_prompts.R
#
# Requires: readr, jsonlite  (install.packages(c("readr", "jsonlite")))
# =============================================================================

suppressPackageStartupMessages({
  library(readr)
  library(jsonlite)
})

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

EXPERIMENT_NAME <- "guenther2023ViSpa"

# The instruction block shown to participants. Lines are joined with a blank
# line between them ("\n\n"), matching the rendered form of the Python
# triple-quoted string literal in the source pipeline.
INSTRUCTION_LINES <- c(
  "Instructions",
  "In the following study, you will be presented with sets of four word pairs.",
  "Your task is to judge which of the objects described by these four pairs look the most similar and which the least similar. Of course, you will have to pick two different pairs for these two questions.",
  "As an example, consider the four following pairs:",
  "bottle - pyramid\ndog - wolf\nlamp - soldier\ncar - street",
  "A reasonable answer in this case could be that dog - wolf look the most similar, while car - street look the least similar.",
  "Note that you should only consider visual similarity for this task, and ignore other types of similarity (for example, even though cars and roads often occur together, they do not look similar).",
  "The study will not continue unless you give a response. Thus, if you want to pause the study, you can delay your response until you want to continue.",
  "By pressing the ESC key, you will end the fullscreen mode. This does not hinder you from continuing the experiment, but you cannot switch back to fullscreen mode. If possible, we want to ask you to stay in fullscreen mode for the whole duration of the experiment.",
  "The study will start with two practice trials in which you receive feedback."
)
INSTRUCTION <- paste0(paste(INSTRUCTION_LINES, collapse = "\n\n"), "\n")

# Trial sentence template. `%s` placeholders are filled with, in order:
#   stimulus, best, stimulus, worst.
TRIAL_TEMPLATE <- paste0(
  "Which look the most similar? %s. You choose <<%s>> as most similar. ",
  "Which look the least similar? %s. You choose <<%s>> as least similar \n "
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

# Resolve base_dir to the directory containing this script (so relative paths
# work no matter which cwd the user runs Rscript from).
script_base_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  script_arg <- sub("^--file=", "", args[grep("^--file=", args)])
  if (length(script_arg) > 0) normalizePath(dirname(script_arg)) else normalizePath(".")
}

# Serialize a single participant's record as one JSONL line.
#
# We build the JSON manually (rather than calling toJSON on the whole list) so
# that the separators match Python's default `json.dumps` output used by the
# `jsonlines` library: ", " between fields and ": " after each key. jsonlite's
# built-in compact mode omits those spaces, which would produce a byte-level
# mismatch with the reference Python pipeline.
#
# We still delegate the *string escaping* of `text` and `experiment` to
# jsonlite::toJSON so that embedded quotes, backslashes, and newlines are
# encoded correctly.
format_jsonl_line <- function(text, experiment, participant_id) {
  paste0(
    '{"text": ',           toJSON(text,       auto_unbox = TRUE),
    ', "experiment": ',    toJSON(experiment, auto_unbox = TRUE),
    ', "participant_id": ', as.integer(participant_id),
    '}'
  )
}

# Build the full prompt for one participant: instruction + replay of trials.
build_participant_prompt <- function(df_participant, trial_indices) {
  prompt <- INSTRUCTION
  for (trial in trial_indices) {
    row <- df_participant[df_participant$trial_id == trial, , drop = FALSE]
    if (nrow(row) > 0) {
      prompt <- paste0(
        prompt,
        sprintf(TRIAL_TEMPLATE, row$stimulus[1], row$best[1], row$stimulus[1], row$worst[1])
      )
    }
  }
  paste0(prompt, "\n")
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main <- function() {
  base_dir <- script_base_dir()
  df <- read_csv(
    file.path(base_dir, "processed_data", "exp1.csv"),
    show_col_types = FALSE, progress = FALSE
  )

  # Stable participant/trial ordering, then remap raw (anonymized) participant
  # IDs to 1..N in first-appearance order. `match(x, unique(x))` is the idiom
  # equivalent to pandas' `map({p: i+1 for i, p in enumerate(unique)})`.
  df <- df[order(df$participant_id, df$trial_id), , drop = FALSE]
  df$participant_id <- match(df$participant_id, unique(df$participant_id))

  participants   <- unique(df$participant_id)
  trial_indices  <- 0:max(df$trial_id)  # mirrors Python range(max + 1)

  out_path <- file.path(base_dir, "prompts.jsonl")
  con <- file(out_path, open = "wb")
  on.exit(close(con), add = TRUE)

  for (p in participants) {
    df_p   <- df[df$participant_id == p, , drop = FALSE]
    prompt <- build_participant_prompt(df_p, trial_indices)
    line   <- format_jsonl_line(prompt, EXPERIMENT_NAME, p)
    writeLines(line, con, sep = "\n")
  }
}

if (sys.nframe() == 0) {
  main()
}
