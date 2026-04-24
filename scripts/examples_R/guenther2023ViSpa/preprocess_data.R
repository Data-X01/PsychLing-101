# =============================================================================
# preprocess_data.R
# -----------------------------------------------------------------------------
# Native-R port of guenther2023ViSpa/preprocess_data.py.
#
# Reads the raw TSV collected for the ViSpa visual-similarity judgement task
# and emits a tidy, per-trial CSV that downstream prompt generation consumes.
#
# Pipeline:
#   original_data/data_study1_ratings_words_complete.txt   (raw TSV, 33,055 rows)
#     |
#     v
#   processed_data/exp1.csv
#     columns: participant_id, trial_id, stimulus, best, worst
#
# Side effect: writes CODEBOOK.csv if it does not already exist.
#
# Usage:
#   Rscript preprocess_data.R
#
# Requires: readr  (install.packages("readr"))
# =============================================================================

suppressPackageStartupMessages({
  library(readr)
})

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

# Create processed_data/ if it does not yet exist. Returns the directory path.
ensure_processed_dir <- function(base_dir) {
  processed_dir <- file.path(base_dir, "processed_data")
  dir.create(processed_dir, showWarnings = FALSE, recursive = TRUE)
  processed_dir
}

# Idempotently write a CODEBOOK.csv describing the output columns. If the file
# already exists we leave it untouched so hand-curated edits are preserved.
write_codebook <- function(base_dir) {
  codebook_path <- file.path(base_dir, "CODEBOOK.csv")
  if (file.exists(codebook_path)) {
    return(invisible(NULL))
  }
  codebook <- data.frame(
    column_name = c("participant_id", "trial_id", "stimulus", "best", "worst"),
    description = c(
      "Anonymized participant ID",
      "Trial order index (factorized from raw trial_id)",
      "Four options concatenated as 'opt1; opt2; opt3; opt4'",
      "Participant's 'best' choice string",
      "Participant's 'worst' choice string"
    ),
    stringsAsFactors = FALSE
  )
  write.csv(codebook, codebook_path, row.names = FALSE)
}

# -----------------------------------------------------------------------------
# Core preprocessing
# -----------------------------------------------------------------------------

preprocess <- function(base_dir) {
  original_path <- file.path(
    base_dir, "original_data", "data_study1_ratings_words_complete.txt"
  )
  processed_dir <- ensure_processed_dir(base_dir)
  write_codebook(base_dir)

  # The raw file is TSV with a JSON-encoded `responses` column that contains
  # embedded quotes. readr::read_tsv handles RFC-style quoting correctly; base
  # R's read.delim tends to mis-parse these rows.
  df <- read_tsv(original_path, show_col_types = FALSE, progress = FALSE)

  # Ensure all four option columns exist, even if the raw file is missing one.
  # The original Python pipeline makes the same defensive check.
  option_cols <- c("option1", "option2", "option3", "option4")
  for (col in option_cols) {
    if (!col %in% names(df)) df[[col]] <- ""
  }

  # Concatenate the four options into a single stimulus string,
  # e.g. "apple - peach; dog - wolf; lamp - soldier; car - street".
  df$stimulus <- paste(
    trimws(as.character(df$option1)),
    trimws(as.character(df$option2)),
    trimws(as.character(df$option3)),
    trimws(as.character(df$option4)),
    sep = "; "
  )

  # Replace the raw trial identifier with a 1..N trial-order index.
  #
  # Gotcha: we must pass `levels = unique(...)` so that factor levels are
  # assigned in first-appearance order. This mirrors pandas' `factorize()`.
  # Without this, R's default `factor()` would sort levels alphabetically and
  # produce different integer labels than the Python pipeline.
  if ("trial_id" %in% names(df)) {
    df$trial_id <- as.integer(factor(df$trial_id, levels = unique(df$trial_id)))
  }

  # Keep only the columns we need, in canonical order.
  out_cols <- c("participant_id", "trial_id", "stimulus", "best", "worst")
  out_cols <- out_cols[out_cols %in% names(df)]
  df_out <- df[, out_cols, drop = FALSE]

  # Stable sort: participant, then trial within participant.
  sort_cols <- intersect(c("participant_id", "trial_id"), names(df_out))
  df_out <- df_out[do.call(order, df_out[sort_cols]), , drop = FALSE]

  write_csv(df_out, file.path(processed_dir, "exp1.csv"))
}

# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
# When run via `Rscript`, resolve base_dir to the script's own directory so
# relative paths (original_data/, processed_data/) work regardless of cwd.

if (sys.nframe() == 0) {
  args <- commandArgs(trailingOnly = FALSE)
  script_arg <- sub("^--file=", "", args[grep("^--file=", args)])
  base_dir <- if (length(script_arg) > 0) {
    normalizePath(dirname(script_arg))
  } else {
    normalizePath(".")
  }
  preprocess(base_dir)
}
