# preprocess_data.R
# Preprocessing script for the Dutch Lexicon Project 1 (DLP1)
# Keuleers, E., Diependaele, K., & Brysbaert, M. (2010). Frontiers in Psychology, 1, 174.
# Source data: https://osf.io/uw7t6/
#
# This script reads the raw DLP1 trial-level file in original_data/, renames
# columns to match the canonical names in CODEBOOK.csv, and writes the tidy
# CSV exp1.csv into processed_data/.

# ---- Setup -----------------------------------------------------------------

required_pkgs <- c("readr", "dplyr")
to_install <- setdiff(required_pkgs, rownames(installed.packages()))
if (length(to_install) > 0) install.packages(to_install, repos = "https://cloud.r-project.org")

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
})

# Resolve paths relative to this script's location so it runs from anywhere.
script_dir <- tryCatch(
  dirname(normalizePath(sys.frame(1)$ofile)),
  error = function(e) getwd()
)
setwd(script_dir)

raw_dir <- "original_data"
out_dir <- "processed_data"
dir.create(out_dir, showWarnings = FALSE)

# ---- Read raw data ---------------------------------------------------------

cat("Reading raw data...\n")

# Trial-level data: one row per trial.
# The full file (dlp-trials.txt) is ~107 MB, so we use the block-50 (final
# block) version, which the original authors recommend for analyses
# unaffected by practice effects (~19,500 trials).
trials_raw <- read_tsv(
  file.path(raw_dir, "dlp-trials-block-50.txt"),
  show_col_types = FALSE
)

# ---- Tidy trial-level data -------------------------------------------------

cat("Tidying trial-level data...\n")

trials_tidy <- trials_raw |>
  transmute(
    participant_id = participant,
    trial_id       = trial,
    trial_order    = order,
    phase_id       = block,
    stimulus       = spelling,
    condition      = ifelse(lexicality == "W", "word", "nonword"),
    response       = ifelse(response == "W", "word", "nonword"),
    accuracy       = as.integer(accuracy),
    rt             = as.numeric(rt)
  )

# ---- Write output ----------------------------------------------------------

write_csv(trials_tidy, file.path(out_dir, "exp1.csv"))

cat("Done.\n")
cat("  exp1.csv: ", nrow(trials_tidy), "trial-level rows\n")
