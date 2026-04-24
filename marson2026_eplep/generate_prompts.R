# set the directory to source file location

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

processed_filenames <- list.files(path = "processed_data/",
                            recursive = TRUE)



out_path <- file.path(base_dir, "prompts.jsonl")
con <- file(out_path, open = "wb")
on.exit(close(con), add = TRUE)



for(exp_n in 1:length(processed_filenames)) {
df <- read_csv(file.path(base_dir, "processed_data", processed_filenames[exp_n]), show_col_types = FALSE, progress = FALSE)

df <- df[order(df$participant_id, df$trial_order), , drop = FALSE]

df$participant_id <- match(df$participant_id, unique(df$participant_id))

participants <- unique(df$participant_id)

for (participant in participants) {
  df_p <- df[df$participant_id == participant, , drop = FALSE]
  trials <- 1:max(df_p$trial_order)
  
  # assign random letters to button A and button L
  randindex <- floor(runif(2, 1, 27))
  while(randindex[1] == randindex[2]){
    randindex <- floor(runif(2, 1, 27))
  }
  press_A <- letters[randindex[1]]
  press_L <- letters[randindex[2]]
  
  instruction_lines <- c(
    "Instructions",
    "During this task you will see a + sign, followed by a string of letters.",
    "Your task is to decide whether the string of letters is an existing word or not (American spelling).",
    paste("If you think it is an existing word, you respond \"YES\" by pressing \"", press_A, "\" on the keyboard; if you think it is not an existing word, you respond \"NO\" by pressing \"", press_L, "\" on the keyboard.", sep=''),
    "If you are sure that the word exists, even though you don't know its exact meaning, you may still respond \"yes\".",
    "But if you are not sure if it is an existing word, you should respond \"no\".",
    "Please respond as quickly and accurately as possible.",
    "The test session is now about to start.",
    "This session will last around 20 minutes, but there will be one-minute breaks in between.",
    paste("You may decide to terminate each break and resume the session earlier - if you want - by pressing the", press_L, "key.", sep = ''),
    "During the testing session, you will not receive feedback on your performance.",
    "Please remember that the question will be \"is the letter string an existing word?\"",
    paste("To say \"YES\", press the \"", press_A, "\" key; to say \"NO\", press the \"", press_L, "\" key.", sep = '')
  )
  instruction <- paste0(paste(instruction_lines, collapse = "\n\n"), "\n")
  
  rts <- c()
  prompt <- instruction
  for (trial in trials) {
    row <- df_p[df_p$trial_order == trial, , drop = FALSE]
    if (nrow(row) > 0) {
      stimulus <- row$stimulus[1]
      accuracy <- row$accuracy[1]
      condition <- row$condition[1]
      
      if(accuracy==1 & (condition == "SW" | condition == "CW")){
        button <- press_A
      } else if(accuracy==0 & (condition == "SW" | condition == "CW")){
        button <- press_L
      } else if(accuracy==1 & (condition == "SPW" | condition == "CPW" | condition == "NW")){
        button <- press_L
      } else if(accuracy==0 & (condition == "SPW" | condition == "CPW" | condition == "NW")){
        button <- press_A
      }
      button
      
      if(is.na(row$rt[1])){
        datapoint <- sprintf(
          "You see %s. You did not respond in time\n ",
          stimulus
          )
        } else {
          datapoint <- sprintf(
            "You see %s. You press <<%s>>\n ",
            stimulus, button
          )
            }
      
      prompt <- paste0(prompt, datapoint)
    }
    rts <- c(rts,as.character(row$rt))
  }
  prompt <- paste0(prompt, "\n")
  
  rts <- as.integer(rts)
  rts_merged<-paste("[",paste0(rts, collapse = ","),"]",sep='')
  line <- paste0(
    '{"text": ', toJSON(prompt, auto_unbox = TRUE),
    ', "experiment": ', toJSON(paste("marson2026_eplep_exp",exp_n,sep=''), auto_unbox = TRUE),
    ', "participant_id": ', as.integer(participant),
    ', "age": ', as.integer(as.integer(row$age[1])),
    ', "rt": ', rts_merged,
    '}'
    )
  writeLines(line, con, sep = "\n")
}
}
close(con)
