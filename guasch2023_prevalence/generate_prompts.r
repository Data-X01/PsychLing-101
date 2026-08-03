
library(data.table)
library(jsonlite)

df <- fread("processed_data/exp1.csv")
setorder(df, session_id, trial_order)

randomized_choice_options <- function(num_choices = 2) {
  possible_keys <- c("q", "w", "e", "r", "t", "y", "u", "i", "o", "p")
  sample(possible_keys, num_choices)
}

con <- file("prompts.jsonl", open = "w")
participants <- unique(df$session_id)

for (pid in participants) {
  
  data_p <- df[session_id == pid]
  choice_options <- randomized_choice_options(num_choices = 2)
  yes_key <- choice_options[1]
  no_key  <- choice_options[2]
  
  data_p[, response := fifelse(
    accuracy == 1,
    fifelse(is_word == 1, yes_key, no_key),
    fifelse(is_word == 1, no_key, yes_key)
  )]
  
  instructions <- paste0(
    "En aquesta prova veuràs 120 cadenes de lletres, algunes de les quals són paraules en català, i altres són paraules inventades (pseudoparaules).\n",
    "La teva tasca consisteix en decidir si cada cadena de lletres és o no una paraula en català.\n",
    "Si coneixes la paraula prem <<", yes_key, ">> i si no la coneixes prem <<", no_key, ">>.\n",
    "La prova dura uns 4 minuts. Pots repetir-la tantes vegades com vulguis. Es presentaran noves cadenes de lletres cada vegada que repeteixis la prova.\n",
    "CONSELL: Respondre <<", yes_key, ">> a paraules que no existeixen penalitza molt la teva puntuació.\n"
  )
  
    trials_text <- paste0(
    "Assaig ", data_p$trial_order,
    ": La cadena és '", data_p$stimulus,
    "'. Tu prems <<", data_p$response, ">>.\n",
    collapse = ""
  )
  
  full_text <- paste0(instructions, trials_text)
  
  entry <- list(
    text = full_text,
    experiment = "guasch2023_prevalence",
    participant = pid,
    device = unique(data_p$device),
    age = unique(data_p$age),
    sex = unique(data_p$sex),
    raising = unique(data_p$raising),
    education = unique(data_p$education),
    proficiency = unique(data_p$proficiency),
    age_first_contact = unique(data_p$age_first_contact),
    mother_language = unique(data_p$mother_language),
    father_language = unique(data_p$father_language),
    exposure = unique(data_p$exposure),
    n_languages = unique(data_p$n_languages)
  )
  
  writeLines(toJSON(entry, auto_unbox = TRUE), con)
}

close(con)
