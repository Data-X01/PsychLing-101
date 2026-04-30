
library(data.table)
library(jsonlite)

df <- fread("processed_data/exp1.csv")
setorder(df, session_id, trial_order)

df[, response := fifelse(
  accuracy == 1,
  fifelse(is_word == 1, "yes", "no"),
  fifelse(is_word == 1, "no", "yes")
)]

instructions <- paste0(
  "En aquesta prova veuràs 120 cadenes de lletres, algunes de les quals són paraules en català, i altres són paraules inventades (pseudoparaules).\n",
  "La teva tasca consisteix en decidir si cada cadena de lletres és o no una paraula en català.\n",
  "Si coneixes la paraula prem el botó SÍ i si no la coneixes prem el botó NO.\n",
  "La prova dura uns 4 minuts. Pots repetir-la tantes vegades com vulguis. Es presentaran noves cadenes de lletres cada vegada que repeteixis la prova.\n",
  "CONSELL: Respondre SÍ a paraules que no existeixen penalitza molt la teva puntuació.\n"
)

con <- file("prompts.jsonl", open = "w")

participants <- unique(df$session_id)

for (pid in participants) {
  
  data_p <- df[session_id == pid]
  
  trials_text <- paste0(
    "Trial ", data_p$trial_order,
    ": The string is '", data_p$stimulus,
    "'. You press <<", data_p$response, ">>.\n",
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
