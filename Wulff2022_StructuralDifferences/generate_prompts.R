# Dependencies -----------------------------------------------------------------

install.packages(c("tidyverse", "jsonlite"))
library(tidyverse)
library(jsonlite)

# Read preprocessed data -------------------------------------------------------

exp1 <- read_csv("processed_data/exp1.csv") |> arrange(participant_id, trial_order, rt)
exp2 <- read_csv("processed_data/exp2.csv") |> arrange(participant_id, rt)
exp3 <- read_csv("processed_data/exp3.csv")

# Create prompts Experiment 1 --------------------------------------------------

exp1_tbl <- tibble(
  text = NA_character_,
  experiment = "Wulff2022_StructuralDifferences/Study1_Fluency",
  participant_id = unique(exp1$participant_id),
  rt = NA
)

for (p in exp1 |> pull(participant_id) |> unique()) {
  
  this_p <- exp1 |> filter(participant_id == p)
  
  instructions <- "Ich werde Ihnen zweimal eine Kategorie nennen und möchte, dass Sie so schnell Sie können alle Dinge aufzählen, die in diese Kategorie gehören. Wenn ich zum Beispiel 'Kleidungsstücke' sage, können Sie 'Hemd', 'Krawatte' oder 'Hut', usw. aufzählen. Sie haben dafür jeweils 10 Minuten Zeit."

  prompts_stimuli = c()
  rt_stimuli = list()
  
  for (s in this_p |> pull(stimulus) |> unique()) {
    
    this_s <- this_p |> filter(stimulus == s)
    
    position <- this_s$trial_order[1] + 1
    position_ger <- case_when(position == 1 ~ "erste", position == 2 ~ "zweite")
    stimulus_ger <- case_when(s == "country" ~ "Länder", s == "animal" ~ "Tiere")

    responses <- paste(
      sprintf(
        "  Response %d: <<%s>>",
        seq_along(this_s$response_corrected),
        this_s$response_corrected
      ),
      collapse = "\n"
    )
    
    prompt_s <- paste(
      c(
        sprintf(
          "Trial %d: Sind Sie bereit? Die %s Kategorie ist: %s.",
          position,
          position_ger,
          stimulus_ger
        ),
        responses,
        "Gut, danke, die Zeit ist abgelaufen."
      ),
      collapse = "\n\n"
    )

    prompts_stimuli <- c(prompts_stimuli, prompt_s)
    rt_stimuli <- append(rt_stimuli, list(this_s$rt))
    
  }
  
  prompt_participant <- paste(c(instructions, prompts_stimuli), collapse = "\n\n")
  
  exp1_tbl$text[exp1_tbl$participant_id == p] <- prompt_participant
  exp1_tbl$rt[exp1_tbl$participant_id == p] <- list(rt_stimuli)
  
}

ppt_vars <- exp1 |> 
  select(participant_id, age, participant_age_group, gender) |> 
  distinct()

exp1_tbl <- exp1_tbl |> 
  left_join(ppt_vars, by = "participant_id")

# Create prompts Experiment 2 --------------------------------------------------

exp2_tbl <- tibble(
  text = NA_character_,
  experiment = "Wulff2022_StructuralDifferences/Study2_Fluency",
  participant_id = unique(exp2$participant_id),
  rt = NA
)

for (p in exp2 |> pull(participant_id) |> unique()) {
  
  this_p <- exp2 |> filter(participant_id == p)
  
  instructions <- "Ich werde Ihnen eine Kategorie nennen und möchte, dass Sie so schnell Sie können alle Dinge aufzählen, die in diese Kategorie gehören. Wenn ich zum Beispiel 'Kleidungsstücke' sage, können Sie 'Hemd', 'Krawatte' oder 'Hut', usw. aufzählen. Sie haben dafür 10 Minuten Zeit.\n\nSind Sie bereit? Die Kategorie ist: Tiere."
  
  responses <- paste(
    sprintf(
      "Response %d: <<%s>>",
      seq_along(this_p$response_corrected),
      this_p$response_corrected
    ),
    collapse = "\n"
  )
  
  prompt_participant <- paste(
    c(instructions, responses, "Gut, danke, die Zeit ist abgelaufen."),
    collapse = "\n\n"
  )
  
  exp2_tbl$text[exp2_tbl$participant_id == p] <- prompt_participant
  exp2_tbl$rt[exp2_tbl$participant_id == p] <- list(this_p$rt)
  
}

ppt_vars <- exp2 |> 
  select(participant_id, age, participant_age_group, gender) |> 
  distinct()

exp2_tbl <- exp2_tbl |> 
  left_join(ppt_vars, by = "participant_id")

# Create prompts Experiment 3 --------------------------------------------------

exp3_tbl <- tibble(
  text = NA_character_,
  experiment = "Wulff2022_StructuralDifferences/Study2_SimilarityJudgements",
  participant_id = unique(exp3$participant_id),
  rt = NA
)

for (p in exp3 |> pull(participant_id) |> unique()) {
  
  this_p <- exp3 |> filter(participant_id == p)
  
  instructions <- "In dieser Aufgabe werden Sie die Ähnlichkeit von Tierpaaren bewerten. Antworten Sie jeweils auf einer Skala von 1 (extrem unähnlich) bis 20 (extrem ähnlich)!"
  
  responses <- paste(
    sprintf(
      "Trial %d: Wie ähnlich sind '%s' und '%s'? <<%d>>",
      seq_along(this_p$response),
      this_p$stimulus_left,
      this_p$stimulus_right,
      this_p$response
    ),
    collapse = "\n"
  )
  
  prompt_participant <- paste(
    c(instructions, responses, "Gut, danke, die Zeit ist abgelaufen."),
    collapse = "\n\n"
  )

  exp3_tbl$text[exp3_tbl$participant_id == p] <- prompt_participant
  exp3_tbl$rt[exp3_tbl$participant_id == p] <- list(this_p$rt)
  
}

ppt_vars <- exp3 |> 
  select(participant_id, age, participant_age_group, gender) |> 
  distinct()

exp3_tbl <- exp3_tbl |> 
  left_join(ppt_vars, by = "participant_id")

# Combine, export as .jsonl file, and zip --------------------------------------

exp <- bind_rows(exp1_tbl, exp2_tbl, exp3_tbl)

stream_out(exp, file("prompts.jsonl"))
zip("prompts.jsonl.zip", "prompts.jsonl")
file.remove("prompts.jsonl")
