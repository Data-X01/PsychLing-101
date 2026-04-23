suppressPackageStartupMessages({
  library(readr)
})

ensure_processed_dir <- function(base_dir) {
  processed_dir <- file.path(base_dir, "processed_data")
  dir.create(processed_dir, showWarnings = FALSE, recursive = TRUE)
  processed_dir
}

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

preprocess <- function(base_dir) {
  original_path <- file.path(base_dir, "original_data", "data_study1_ratings_words_complete.txt")
  processed_dir <- ensure_processed_dir(base_dir)
  write_codebook(base_dir)

  df <- read_tsv(original_path, show_col_types = FALSE, progress = FALSE)

  for (col in c("option1", "option2", "option3", "option4")) {
    if (!col %in% names(df)) df[[col]] <- ""
  }
  df$stimulus <- paste(
    trimws(as.character(df$option1)), trimws(as.character(df$option2)),
    trimws(as.character(df$option3)), trimws(as.character(df$option4)),
    sep = "; "
  )

  if ("trial_id" %in% names(df)) {
    df$trial_id <- as.integer(factor(df$trial_id, levels = unique(df$trial_id)))
  }

  cols <- c("participant_id", "trial_id", "stimulus", "best", "worst")
  cols <- cols[cols %in% names(df)]
  df_out <- df[, cols, drop = FALSE]

  sort_cols <- intersect(c("participant_id", "trial_id"), names(df_out))
  df_out <- df_out[do.call(order, df_out[sort_cols]), , drop = FALSE]

  write_csv(df_out, file.path(processed_dir, "exp1.csv"))
}

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
