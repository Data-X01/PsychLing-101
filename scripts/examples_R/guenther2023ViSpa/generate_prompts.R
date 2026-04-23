suppressPackageStartupMessages({
  library(readr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = FALSE)
script_arg <- sub("^--file=", "", args[grep("^--file=", args)])
base_dir <- if (length(script_arg) > 0) {
  normalizePath(dirname(script_arg))
} else {
  normalizePath(".")
}

df <- read_csv(file.path(base_dir, "processed_data", "exp1.csv"), show_col_types = FALSE, progress = FALSE)

df <- df[order(df$participant_id, df$trial_id), , drop = FALSE]

df$participant_id <- match(df$participant_id, unique(df$participant_id))

participants <- unique(df$participant_id)
trials <- 0:max(df$trial_id)

instruction_lines <- c(
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
instruction <- paste0(paste(instruction_lines, collapse = "\n\n"), "\n")

out_path <- file.path(base_dir, "prompts.jsonl")
con <- file(out_path, open = "wb")
on.exit(close(con), add = TRUE)

for (participant in participants) {
  df_p <- df[df$participant_id == participant, , drop = FALSE]
  prompt <- instruction
  for (trial in trials) {
    row <- df_p[df_p$trial_id == trial, , drop = FALSE]
    if (nrow(row) > 0) {
      stimulus <- row$stimulus[1]
      best <- row$best[1]
      worst <- row$worst[1]
      datapoint <- sprintf(
        "Which look the most similar? %s. You choose <<%s>> as most similar. Which look the least similar? %s. You choose <<%s>> as least similar \n ",
        stimulus, best, stimulus, worst
      )
      prompt <- paste0(prompt, datapoint)
    }
  }
  prompt <- paste0(prompt, "\n")

  line <- paste0(
    '{"text": ', toJSON(prompt, auto_unbox = TRUE),
    ', "experiment": ', toJSON("guenther2023ViSpa", auto_unbox = TRUE),
    ', "participant_id": ', as.integer(participant),
    '}'
  )
  writeLines(line, con, sep = "\n")
}
