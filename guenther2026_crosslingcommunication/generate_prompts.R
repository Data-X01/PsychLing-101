rm(list=ls())

#install.packages("tidyverse")
#install.packages("glue")
#install.packages("jsonlite")

library(tidyverse)
library(glue)
library(jsonlite)

setwd("C:/Users/tscha/PsychLing-101/guenther2026_crosslingcommunication")

df_phase1 <- read_csv2("processed_data/exp1.csv")
df_phase2 <- read_csv2("processed_data/exp2.csv")

ita_instruction <- paste0("In questo esperimento ti verranno presentate 12 parole Italiane. Il tuo compito consisterà nello scrivere quale potrebbe essere la traduzione tedesca per ciascuna parola. Ti preghiamo di fornire risposte che potrebbero sembrare realmente parole tedesche; in particolare, ti chiediamo di non rispondere con altre parole italiane (ad es. sinonimi o parole ortograficamente troppo simili a quella italiana di partenza) o con altre parole tedesche esistenti (o provenienti da altre lingue) che potresti casualmente conoscere. Allo stesso tempo è importante che ogni tua risposta sia leggibile, e che quindi non sia una serie casuale di caratteri.")
de_instruction  <- paste0("In einem anderen Experiment haben wir anderen Personen einzelne Wörter wie ,Apfel' gezeigt. Wir haben sie gebeten, diese Wörter durch jeweils ein anderes einzelnes Wort zu ersetzen, das die ursprüngliche Bedeutung so genau wie möglich wiedergibt, damit Sie als ratender Spieler die besten Chancen haben, sie richtig zu erraten. In diesem Experiment werden Ihnen also verschiedene einzelne Wörter vorgelegt, und Sie sollen erraten, welches Originalwort diese ersetzen könnten. Für jedes Wort müssen Sie 3 mögliche Originalwörter vorschlagen.")

experiment_ph1 <- "guenther2026_exp1"
experiment_ph2 <- "guenther2026_exp2"

# --- function ---
generate_prompts <- function(df, instruction, experiment, trial_text, phase) {
  
  participant_ids <- df %>% distinct(participant_id) %>% pull(participant_id) %>% sort()
  trial_idx       <- df %>% distinct(trial_order)   %>% pull(trial_order)   %>% sort()
  
  all_participants <- list()
  
  for (id in participant_ids) {
    df_current_id <- df[df$participant_id == id, ]
    
    trials_merged <- ""
    rt_list <- c()
    
    for (j in trial_idx) {
      df_current_id_trial <- df_current_id[df_current_id$trial_order == j, ]
      
      word       <- unique(df_current_id_trial$word)
      response_1 <- df_current_id_trial$response[df_current_id_trial$response_order == "response1"]
      response_2 <- df_current_id_trial$response[df_current_id_trial$response_order == "response2"]
      response_3 <- df_current_id_trial$response[df_current_id_trial$response_order == "response3"]
      rt         <- df_current_id_trial$rt[1]
      
      trial <- paste0(word, ". ", trial_text, " <<", response_1, ">>. <<", response_2, ">>. <<", response_3, ">>.")
      
      trials_merged <- paste0(trials_merged, trial, "\n")
      rt_list <- c(rt_list, rt)
    }
    
    RTs_text   <- paste0("[", paste(round(rt_list), collapse = ", "), "]")
    gender     <- df_current_id$gender[1]
    age        <- df_current_id$age[1]
    other_lang <- df_current_id$other_languages[1]
    
    result <- glue(
      "{{'text': '{instruction}\n{trials_merged}', ",
      "'experiment': '{experiment}', ",
      "'participant': '{id}', ",
      "'RTs': {RTs_text}, ",
      "'gender': '{gender}', ",
      "'age': {age}, ",
      "'other_languages': '{other_lang}'}}"
    )
    
    all_participants[[as.character(id)]] <- data.frame(
      participant_id  = id,
      exp_phase       = phase,
      gender          = gender,
      age             = age,
      other_languages = other_lang,
      trials_merged   = trials_merged,
      RTs_text        = RTs_text,
      result          = as.character(result),
      stringsAsFactors = FALSE
    )
  }
  
  do.call(rbind, all_participants)
}

# --- run for each phase ---
df_prompts_ph1 <- generate_prompts(
  df          = df_phase1,
  instruction = ita_instruction,
  experiment  = experiment_ph1,
  trial_text  = "Inserisci tre risposte",
  phase       = "ph1"
)

df_prompts_ph2 <- generate_prompts(
  df          = df_phase2,
  instruction = de_instruction,
  experiment  = experiment_ph2,
  trial_text  = "Gib drei Antworten ein",  # adjust to your actual German trial text
  phase       = "ph2"
)

# --- combine and write ---
df_prompts_all <- rbind(df_prompts_ph1, df_prompts_ph2)

writeLines(df_prompts_all$result, "prompts.jsonl")
