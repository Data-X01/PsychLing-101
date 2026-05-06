# =============================================================================
# generate_prompts.R
# -----------------------------------------------------------------------------
# Reads processed_data/exp1.csv and produces one prompt per participant,
# serialized as JSONL (one JSON object per line), then zipped.
#
# Experiment: Participants viewed images. In label conditions (positive/negative),
# a word appeared under the image 3 seconds after image onset. In the no-label
# condition, no word was shown. Participants generated 3 associations per image.

# Reads the tidy per-trial CSV written by preprocess_data.R and produces one
# narrative prompt per participant, serialized as JSONL (one JSON object per
# line) for downstream LLM evaluation.
#
# Pipeline:
#   processed_data/exp1.csv
#     |
#     v
#   prompts.jsonl
#     each line: {"text": <prompt>, "experiment": "petrenco2024_associations_images",
#                 "participant_id": <int>}
#
# Each participant's prompt consists of:
#   1. The task instructions shown to the human participant
#   2. A chronological replay of the participant's trials, one line per trial,
#      phrased as "What are the first 3 words that come to your mind when you think about this? ... You generate <<X>>,<<X>>,<<X>> ..."
#
# Usage:
#   Rscript generate_prompts.R
#
# Requires: readr, jsonlite  (install.packages(c("readr", "jsonlite")))
#
# Output: prompts.jsonl.zip
#   each line: {
#     "text": <chr>,
#     "experiment": <chr>,
#     "participant_id": <chr>,
#     "age": <dbl>,
#     "gender": <chr>,
#     "first_language": <chr>,
#     "list": <chr>
#   }
#
# Output: prompts.jsonl.zip
# =============================================================================

rm(list = ls())

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(purrr)
  library(jsonlite)
  library(zip)
})

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

EXPERIMENT_NAME <- "petrenco2024_associations_images" 

INSTRUCTIONS <- paste(
  "Experiment task",
  "You will first see <b>an image depicting a situation or a creature(s)",
  "In some cases you will then read words that will appear under the image.",
  "After you have looked at the image and read the word (if there is one), you will be asked to list the 3 first associations that come to your mind when you think about the creatures or situations depicted in the image.",
  "Try not to think too much and type in the first words that you thought of. Ensure they are different from each other.",
  "Once you have looked at the image, read the word, and proceeded to the next screen to type in the associations, you cannot go back to the previous screen with the image.",
  "Please pay attention and provide your associations immediately after viewing the image and reading the word (if there is one).",
  "Please pay attention during the task and try to come up with the associations right after you looked at the image and read the word (if there is one).",
  "You will not be able to type in the words that appeared under the images.",
  "If you do, you will be asked to match the requested format.",
  "Use letters only, no spaces, no punctuation, and no special characters",
  "Do not rush, the Continue button will be disabled for the first 5 seconds after the image presentation.",
  sep = "\n\n"
)

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

input_file   <- "processed_data/exp1.csv"
output_jsonl <- "prompts.jsonl"
output_zip   <- "prompts.jsonl.zip"

# -----------------------------------------------------------------------------
# Read data
# -----------------------------------------------------------------------------

df <- read_csv(input_file, show_col_types = FALSE)

# Validate required columns
required_cols <- c(
  "participant_id", "trial_order", "condition",
  "stimulus1_image", "stimulus2_label", "stimulus2_present",
  "image_filename", "response1", "response2", "response3",
  "age", "gender", "first_language", "list"
)
missing_cols <- setdiff(required_cols, names(df))
if (length(missing_cols) > 0) {
  stop("Missing required columns in exp1.csv: ",
       paste(missing_cols, collapse = ", "))
}

df <- df %>% arrange(participant_id, trial_order)

# -----------------------------------------------------------------------------
# Build prompt for one participant
# -----------------------------------------------------------------------------

make_participant_prompt <- function(dat) {
  
  dat <- dat %>% arrange(trial_order)
  
  trial_lines <- map_chr(seq_len(nrow(dat)), function(i) {
    row <- dat[i, ]
    
    trial_num <- i  # 1-indexed
    
    # Stimulus line depends on condition
    if (!is.na(row$stimulus2_present) && row$stimulus2_present == "yes") {
      stimulus_line <- sprintf(
        "Trial %d: The image <%s> appears on the screen. Three seconds later, the word '%s' appears under the image.",
        trial_num, row$image_filename, row$stimulus2_label
      )
    } else {
      stimulus_line <- sprintf(
        "Trial %d: The image <%s> appears on the screen.",
        trial_num, row$image_filename
      )
    }
    
    # Response line: 3 associations marked with << >>
    response_line <- sprintf(
      "You generate the following associations: <<%s>>, <<%s>>, <<%s>>.",
      row$response1, row$response2, row$response3
    )
    
    paste(stimulus_line, response_line, sep = "\n")
  })
  
  full_text <- paste0(
    INSTRUCTIONS, "\n\n",
    paste(trial_lines, collapse = "\n\n")
  )
  
  list(
    text           = full_text,
    experiment     = EXPERIMENT_NAME,
    participant_id = unique(dat$participant_id),
    age            = unique(dat$age),
    gender         = unique(dat$gender),
    first_language = unique(dat$first_language),
    list           = unique(dat$list)
  )
}

# -----------------------------------------------------------------------------
# Generate one record per participant
# -----------------------------------------------------------------------------

prompt_records <- df %>%
  group_by(participant_id) %>%
  group_split() %>%
  map(make_participant_prompt)

# -----------------------------------------------------------------------------
# Write JSONL
# -----------------------------------------------------------------------------

con <- file(output_jsonl, open = "w", encoding = "UTF-8")
for (rec in prompt_records) {
  writeLines(toJSON(rec, auto_unbox = TRUE), con = con)
}
close(con)

# -----------------------------------------------------------------------------
# Zip and clean up
# -----------------------------------------------------------------------------

if (file.exists(output_zip)) file.remove(output_zip)
zip::zipr(zipfile = output_zip, files = output_jsonl)
file.remove(output_jsonl)

# -----------------------------------------------------------------------------
# Summary and token limit check (~4 chars per token, 32K limit)
# -----------------------------------------------------------------------------

cat("Saved:", output_zip, "\n")
cat("Participants:", length(prompt_records), "\n")

char_limit <- 32000 * 4
texts      <- map_chr(prompt_records, "text")
over_limit <- which(nchar(texts) > char_limit)

if (length(over_limit) > 0) {
  warning("Participants exceeding ~32K token limit: ",
          paste(map_chr(prompt_records[over_limit], "participant_id"),
                collapse = ", "))
} else {
  cat("All prompts within 32K token limit.\n")
}

