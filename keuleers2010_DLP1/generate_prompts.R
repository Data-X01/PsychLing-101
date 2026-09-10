# generate_prompts.R
# Generates one natural-language prompt per participant for the
# Dutch Lexicon Project 1 (DLP1).
#
# Reference:
#   Keuleers, E., Diependaele, K., & Brysbaert, M. (2010). Practice effects in
#   large-scale visual word recognition studies: A lexical decision study on
#   14,000 Dutch mono- and disyllabic words and nonwords.
#   Frontiers in Psychology, 1, 174. https://doi.org/10.3389/fpsyg.2010.00174
#
# Procedure (from the original paper, pp. 3-4):
#   - Each trial: two short vertical fixation lines appear above and below the
#     centre of the screen, with a gap between them.
#   - 500 ms later, the stimulus appears in lowercase in the gap; the
#     fixation lines remain on screen.
#   - The stimulus stays on screen until the participant responds, or 2,000 ms
#     timeout.
#   - Participants used their dominant hand for "word" responses and their
#     non-dominant hand for "nonword" responses (external response box).
#   - 500 ms blank inter-stimulus interval before the next trial.
#   - 58 test blocks of 500 trials; participants aimed for >= 85% accuracy.
#
# This script:
#   - Reads the standardized trial-level data in processed_data/exp1.csv.
#   - For each participant, randomly assigns one of "a" / "l" to "word" and
#     the other to "nonword", to prevent an LLM from relying on a memorized
#     key mapping (per the binz2022heuristics example).
#   - Writes the original-style instructions, then replays each trial in
#     presentation order, with the participant's response wrapped in << >>.
#   - Stays well under the 32K token budget per participant.
#
# Output: prompts.jsonl  +  prompts.jsonl.zip

# ---- Setup -----------------------------------------------------------------

required_pkgs <- c("readr", "dplyr", "jsonlite")
to_install <- setdiff(required_pkgs, rownames(installed.packages()))
if (length(to_install) > 0) install.packages(to_install, repos = "https://cloud.r-project.org")

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(jsonlite)
})

# Resolve the script's directory so the script runs from anywhere.
script_dir <- tryCatch(
  dirname(normalizePath(sys.frame(1)$ofile)),
  error = function(e) getwd()
)
setwd(script_dir)

processed_dir <- "processed_data"
out_jsonl     <- "prompts.jsonl"
out_zip       <- "prompts.jsonl.zip"

EXPERIMENT_ID <- "keuleers2010_DLP1"

# Token budget. ~1 token per 4 chars; aim for ~25k tokens to stay comfortably
# below the 32k cap.
CHAR_BUDGET <- 100000

# Reproducible per-participant key randomization.
set.seed(2025)

# ---- Read processed data ---------------------------------------------------

cat("Reading processed data...\n")
trials <- read_csv(
  file.path(processed_dir, "exp1.csv"),
  show_col_types = FALSE
)

# Sort within participant by presentation order.
trials <- trials |> arrange(participant_id, trial_order)

participants <- sort(unique(trials$participant_id))
cat("Found", length(participants), "participants.\n")

# ---- Helpers ---------------------------------------------------------------

# Authentic instruction block. Mirrors the procedure described in
# Keuleers, Diependaele, & Brysbaert (2010), pp. 3-4.
build_instructions <- function(word_key, nonword_key) {
  paste0(
    "You are taking part in a Dutch visual lexical decision experiment. ",
    "On each trial, two short vertical fixation lines appear above and ",
    "below the centre of the screen. Five hundred milliseconds later, a ",
    "letter string appears in lowercase between the fixation lines. ",
    "Your task is to decide as quickly and accurately as possible whether ",
    "the letter string is a real Dutch word or a nonword (a pronounceable ",
    "letter string that is not a Dutch word, e.g. 'flummol').\n",
    "If the letter string is a real Dutch WORD, press the button \"",
    word_key, "\".\n",
    "If the letter string is a NONWORD, press the button \"",
    nonword_key, "\".\n",
    "The letter string disappears as soon as you respond, or after 2,000 ",
    "ms (whichever comes first). There is then a 500 ms blank interval ",
    "before the next trial. Try to keep your accuracy above 85% across ",
    "the block.\n\n"
  )
}

# Convert a participant's response to the key they would have pressed under
# the per-participant key mapping.
response_to_key <- function(response, word_key, nonword_key) {
  ifelse(response == "word", word_key,
    ifelse(response == "nonword", nonword_key, "no response")
  )
}

# Format a single trial line. RTs are integers in milliseconds.
format_trial <- function(idx, stimulus, response, key_pressed,
                         accuracy, rt) {
  feedback <- ifelse(accuracy == 1, "Correct.", "Incorrect.")
  if (identical(response, "timeout") || is.na(rt)) {
    sprintf(
      "Trial %d: The letter string is '%s'. You do not respond in time. %s\n",
      idx, stimulus, feedback
    )
  } else {
    sprintf(
      "Trial %d: The letter string is '%s'. You press <<%s>> after %d ms. %s\n",
      idx, stimulus, key_pressed, as.integer(rt), feedback
    )
  }
}

# ---- Build prompts ---------------------------------------------------------

cat("Building prompts...\n")

if (file.exists(out_jsonl)) file.remove(out_jsonl)
con <- file(out_jsonl, open = "w", encoding = "UTF-8")
on.exit(if (isOpen(con)) close(con), add = TRUE)

for (pid in participants) {

  # Per-participant random key assignment.
  keys <- sample(letters, 2)
  word_key    <- keys[1]
  nonword_key <- keys[2]

  pdat <- trials |> filter(participant_id == pid)

  instructions <- build_instructions(word_key, nonword_key)

  trial_lines   <- character(0)
  rts_kept      <- integer(0)
  running_chars <- nchar(instructions)
  trial_counter <- 0L

  for (i in seq_len(nrow(pdat))) {
    trial_counter <- trial_counter + 1L
    line <- format_trial(
      idx         = trial_counter,
      stimulus    = pdat$stimulus[i],
      response    = pdat$response[i],
      key_pressed = response_to_key(pdat$response[i], word_key, nonword_key),
      accuracy    = pdat$accuracy[i],
      rt          = pdat$rt[i]
    )

    if (running_chars + nchar(line) > CHAR_BUDGET) {
      trial_counter <- trial_counter - 1L
      break
    }
    trial_lines <- c(trial_lines, line)
    rt_value <- if (is.na(pdat$rt[i])) NA_integer_ else as.integer(pdat$rt[i])
    rts_kept <- c(rts_kept, rt_value)
    running_chars <- running_chars + nchar(line)
  }

  full_text <- paste0(instructions, paste(trial_lines, collapse = ""))

  record <- list(
    text           = full_text,
    experiment     = EXPERIMENT_ID,
    participant_id = as.integer(pid),
    rt             = rts_kept
  )

  writeLines(
    toJSON(record, auto_unbox = TRUE, dataframe = "rows", na = "null"),
    con
  )

  cat(sprintf(
    "  participant %s: %d trials, %d chars (~%d tokens)\n",
    pid, length(trial_lines), running_chars, as.integer(running_chars / 4)
  ))
}

close(con)

# ---- Zip the JSONL ---------------------------------------------------------

cat("Zipping...\n")
if (file.exists(out_zip)) file.remove(out_zip)
zip_status <- utils::zip(out_zip, files = out_jsonl)
if (zip_status != 0) {
  warning("zip() returned non-zero status; you may need to zip manually.")
}

cat("Done.\n")
cat("  Wrote:", out_jsonl, "\n")
cat("  Wrote:", out_zip,   "\n")
