library(dplyr)
library(readr)
library(jsonlite)
library(purrr)
library(stringr)
library(zip)

# -----------------------------
# Paths
# -----------------------------
input_file <- "processed_data/exp1.csv"
output_jsonl <- "prompts.jsonl"
output_zip <- "prompts.jsonl.zip"

# -----------------------------
# Read processed data
# -----------------------------
df <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(
    participant_id = as.character(participant_id),
    trial_id = suppressWarnings(as.integer(trial_id)),
    version = suppressWarnings(as.integer(version)),
    phase_id = as.character(phase_id),
    block = suppressWarnings(as.integer(block)),
    block_number = suppressWarnings(as.integer(block_number)),
    instruction_mapping = as.character(instruction_mapping),
    stimulus = as.character(stimulus),
    stimulus_location = as.character(stimulus_location),
    response = as.character(response),
    accuracy = suppressWarnings(as.integer(accuracy)),
    concreteness = as.character(concreteness),
    start_rt = suppressWarnings(as.numeric(start_rt)),
    end_rt = suppressWarnings(as.numeric(end_rt)),
    age = suppressWarnings(as.numeric(age)),
    gender = as.character(gender),
    handedness = as.character(handedness),
    device_type = as.character(device_type),
    item = suppressWarnings(as.integer(item))
  ) %>%
  arrange(participant_id, trial_id)

# -----------------------------
# Exact / near-verbatim text blocks from HTML
# -----------------------------
practice_instruction <- function(version) {
  common <- paste(
    "Welcome to the experiment. First, you will be given several training trials.",
    "In this experiment, you will see the nouns along with top and bottom borderlines.",
    "You will be asked to define whether a noun you see is abstract or concrete.",
    "ABSTRACT nouns refer to things that aren’t tangible — things we can’t see, touch, or physically experience.",
    "They are associated with ideas, qualities, emotions, or concepts.",
    "For example, words like freedom, happiness, love, and truth are abstract because they describe feelings, states of mind, or ideas that aren’t physically present.",
    "CONCRETE nouns, on the other hand, refer to things that we can perceive with our senses.",
    "They are associated with physical objects or things we can see, touch, taste, hear, or smell.",
    "For example, table, dog, apple, and car are concrete nouns because they represent things we can actually interact with in the real world."
  )
  
  if (version == 1) {
    rule <- paste(
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the top line.",
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the bottom line."
    )
  } else {
    rule <- paste(
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the top line.",
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the bottom line."
    )
  }
  
  paste(
    common,
    rule,
    "Drag the word to the top or bottom of the screen as if you are moving it out of the screen!",
    "The whole experiment will take about 25 minutes. You will have three breaks during the experiment.",
    "Please try to avoid any disturbance or distractions while performing the experiment.",
    "Click the button below to begin."
  )
}

main_instruction <- function(version) {
  if (version == 1) {
    rule <- paste(
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the top line.",
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the bottom line."
    )
  } else {
    rule <- paste(
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the top line.",
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the bottom line."
    )
  }
  
  paste(
    "Please note that there will no longer be any feedback on the correctness of your response during the individual trials.",
    "REMINDER:",
    rule,
    "Drag the word to the top or bottom of the screen as if you are moving it out of the screen!",
    "There will be three breaks during the experiment. When you are ready, please press the Begin button to start the experiment."
  )
}

changed_rule_screen <- function(version, accuracy_pct, mean_rt) {
  if (version == 1) {
    rule <- paste(
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the bottom line.",
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the top line."
    )
  } else {
    rule <- paste(
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the bottom line.",
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the top line."
    )
  }
  
  paste(
    "End of Block 2 of 4!",
    paste0("You responded correctly in <<", accuracy_pct, ">>% of the trials."),
    paste0("Your average reaction time was <<", mean_rt, ">> ms."),
    "In the next block, the instructions change. Please read them carefully:",
    rule,
    "Drag the word to the top or bottom of the screen as if you are moving it out of the screen!",
    "Press the Start button to start the practice block when you are ready."
  )
}

same_rule_rest_screen <- function(version, accuracy_pct, mean_rt) {
  if (version == 1) {
    rule <- paste(
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the bottom line.",
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the top line."
    )
  } else {
    rule <- paste(
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the bottom line.",
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the top line."
    )
  }
  
  paste(
    "End of Block 3 of 4!",
    paste0("You responded correctly in <<", accuracy_pct, ">>% of the trials."),
    paste0("Your average reaction time was <<", mean_rt, ">> ms."),
    "In the next block, the instructions remain the same.",
    rule,
    "Drag the word to the top or bottom of the screen as if you are moving it out of the screen!",
    "Press the Continue button to continue the experiment when you are ready."
  )
}

training_summary_1 <- function(accuracy_pct, mean_rt) {
  paste(
    "This is the end of the practice block!",
    paste0("You responded correctly in <<", accuracy_pct, ">>% of the trials."),
    paste0("Your average reaction time was <<", mean_rt, ">> ms."),
    "Please press the Continue button to continue the experiment."
  )
}

training_summary_2 <- function(version, accuracy_pct, mean_rt) {
  if (version == 1) {
    rule <- paste(
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the bottom line.",
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the top line."
    )
  } else {
    rule <- paste(
      "If you define a noun as a concrete, please, take it with your mouse and drag it as quickly as possible over the bottom line.",
      "If you define a noun as an abstract, please, take it with your mouse and drag it as quickly as possible over the top line."
    )
  }
  
  paste(
    "This is the end of the practice block!",
    paste0("You responded correctly in <<", accuracy_pct, ">>% of the trials."),
    paste0("Your average reaction time was <<", mean_rt, ">> ms."),
    "REMINDER:",
    rule,
    "Drag the word to the top or bottom of the screen as if you are moving it out of the screen!"
  )
}

final_screen <- function(version, accuracy_pct, mean_rt) {
  if (version == 1) {
    paste(
      "This is the end of the experiment. Thank you for your participation!",
      paste0("You responded correctly in <<", accuracy_pct, ">>% of the trials."),
      paste0("Your average reaction time was <<", mean_rt, ">> ms."),
      "Please press the Next button to receive the Prolific Completion URL."
    )
  } else {
    paste(
      "This is the end of the experiment. Thank you for your participation!",
      paste0("You responded correctly in <<", accuracy_pct, ">>% of the trials."),
      paste0("Your average reaction time was <<", mean_rt, ">> ms."),
      "Before you receive the Prolific Completion URL, we will ask you one last question.",
      "Please press the Next button."
    )
  }
}

# -----------------------------
# Helpers
# -----------------------------
trial_feedback_text <- function(acc) {
  ifelse(acc == 1, "Correct!", "Wrong!")
}

safe_mean_rt_correct <- function(dat) {
  x <- dat %>%
    filter(accuracy == 1) %>%
    pull(end_rt)
  
  if (length(x) == 0 || all(is.na(x))) {
    return(NA_integer_)
  }
  
  as.integer(round(mean(x, na.rm = TRUE)))
}

safe_accuracy_pct <- function(dat) {
  if (nrow(dat) == 0) {
    return(NA_integer_)
  }
  as.integer(round(mean(dat$accuracy, na.rm = TRUE) * 100))
}


make_trial_text <- function(row, show_feedback = FALSE) {
  feedback_text <- ""
  
  if (show_feedback) {
    feedback_text <- ifelse(row$accuracy == 1, " Correct!", " Wrong!")
  }
  
  paste0(
    "Trial ", row$trial_id, ": ",
    "The word is \"", row$stimulus, "\". ",
    "You moved it to the <<", row$response, ">> line. ",
    "Movement started after <<", row$start_rt, ">> ms and ended after <<", row$end_rt, ">> ms.",
    feedback_text
  )
}



block_end_screen <- function(version, block_number, dat_block) {
  acc_pct <- safe_accuracy_pct(dat_block)
  mean_rt <- safe_mean_rt_correct(dat_block)
  
  if (block_number == 0) {
    return(training_summary_1(acc_pct, mean_rt))
  }
  if (block_number == 2) {
    return(changed_rule_screen(version, acc_pct, mean_rt))
  }
  if (block_number == 3) {
    return(training_summary_2(version, acc_pct, mean_rt))
  }
  if (block_number == 4) {
    return(same_rule_rest_screen(version, acc_pct, mean_rt))
  }
  if (block_number == 5) {
    return(final_screen(version, acc_pct, mean_rt))
  }
  
  return(NULL)
}

block_start_screen <- function(version, block_number) {
  if (block_number == 0) {
    return(practice_instruction(version))
  }
  if (block_number == 1) {
    return(main_instruction(version))
  }
  return(NULL)
}

# -----------------------------
# Build one participant prompt
# -----------------------------
make_participant_prompt <- function(dat) {
  dat <- dat %>%
    arrange(trial_id)
  
  version_value <- unique(dat$version)[1]
  
  
  segments <- list()
  
  block_ids <- dat %>%
    pull(block_number) %>%
    unique() %>%
    sort(na.last = TRUE)
  
  for (b in block_ids) {
    dat_block <- dat %>%
      filter(block_number == b) %>%
      arrange(trial_id)
    
    start_screen <- block_start_screen(version_value, b)
    if (!is.null(start_screen)) {
      segments[[length(segments) + 1]] <- start_screen
    }
    
    is_training_block <- b %in% c(0, 3)
    
    for (i in seq_len(nrow(dat_block))) {
      row_i <- dat_block[i, ]
      
      segments[[length(segments) + 1]] <- make_trial_text(
        row_i,
        show_feedback = is_training_block
      )
    }
    
    end_screen <- block_end_screen(version_value, b, dat_block)
    if (!is.null(end_screen)) {
      segments[[length(segments) + 1]] <- end_screen
    }
  }
  
  full_text <- paste(segments, collapse = "\n\n")
  
  list(
    participant_id = unique(dat$participant_id),
    experiment = "tsaregorodtseva2026_mousetracking",
    age = unique(dat$age),
    gender = unique(dat$gender),
    text = full_text
  )
}

# -----------------------------
# Create prompt records
# -----------------------------
prompt_records <- df %>%
  group_by(participant_id) %>%
  group_split() %>%
  map(make_participant_prompt)

# -----------------------------
# Write JSONL
# -----------------------------
con <- file(output_jsonl, open = "w", encoding = "UTF-8")
for (rec in prompt_records) {
  writeLines(toJSON(rec, auto_unbox = TRUE), con = con)
}
close(con)

# -----------------------------
# Zip
# -----------------------------
if (file.exists(output_zip)) {
  file.remove(output_zip)
}
zip::zipr(zipfile = output_zip, files = output_jsonl)
file.remove(output_jsonl)

# -----------------------------
# Checks
# -----------------------------
cat("Saved ZIP:", output_zip, "\n")
cat("Number of participant prompts:", length(prompt_records), "\n")