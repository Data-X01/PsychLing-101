#
# Created by Courtney Hilton April 30 following format on https://github.com/Data-X01/PsychLing-101/blob/main/README.md
#

# libraries ---------------------------------------------------------------

library(tidyverse)
library(here)
library(jsonlite)

# load data ---------------------------------------------------------------

exp1 <- read_csv(here("processed_data", "exp1.csv")) |> 
  # construct trial prompt
  rowwise() |> 
  mutate(
    prompt = paste0(
      "Trial ",
      trial_id,
      ": The sentence stimuli is ",
      stimulus,
      ". The comprehension probe is '",
      comprehension_probe,
      "'. You press <<",
      response,
      ">> after <<",
      round(rt * 1000),
      ">> ms. ",
      if_else(accuracy == 1, "Correct.", "Incorrect.")
    )
  )

# instructions ------------------------------------------------------------

instructions1 <- paste(
    "Welcome to the experiment. Thank you for participating!",
    "In each trial, you will read a sentence one word at a time, presented on the screen at a steady rhythm.",
    "When words appear in all capital letters, imagine reading this word with extra rhythmic emphasis. These will occur at a regular pattern like a rhythm.",
    "After reading the sentence, the experiment then tests your understanding of this sentence by asking you a question.",
    "You respond to this question with either 'yes' or 'no', indicating your response with the 'y' and 'n' keys respectively.",
    "If you have no idea of the answer, either because you found the sentence hard, or your concentration lapsed. Don't worry. Press 'd' for \"don't know\".",
    "This is totally fine, it is natural for your concentration to go up and down during an experiment like this and it's important you don't just randomly guess an answer.",
    "For example, if the sentence was \"The boy that the girl liked is wearing a hat\" and the question was \"the girl is wearing a hat\", the correct response would be 'n'.",
    "When the question appears on the screen, you are to respond as quickly as you can.",
    "If you take longer than 5 seconds, you will be reminded to speed up on the next trial. Accuracy is still important, however, so do not go too quickly.",
    "And unlike reading this sentence, during the trial, the sentence will flash up on the screen one or two words at a time, synchronised to an auditory tone.",
    "You control when each trial starts, so feel free to take short breaks to keep your concentration high. And you are always welcome to ask the experimenter questions during these breaks if anything is unclear.",
    "It is very important that you feel confident in your understanding of the task and are giving it your full attention. Making mistakes is part of the experiment, though, so do not worry when this happens.",
    "Good science is made possible by good participants, so thank you in advance for your cooperation—we really appreciate it!",
    "During the trials, keep your index fingers resting on the 'y' and 'n' key ready to press the button.",
    "Press space to start the main experiment.",
    sep = " "
  )

# assemble output format --------------------------------------------------

participant_ids <- unique(exp1$participant_id)

prompts <- map(participant_ids, \(.participant_id) {
  data_filtered <- exp1 |> 
    filter(participant_id == .participant_id) |> 
    arrange(trial_id)
  
  trial_prompts <- data_filtered |> 
    pull(prompt)
  
  prompt <- paste(c(instructions1, trial_prompts), collapse = "\n")
  
  data.frame(
    text = prompt,
    experiment = "hilton2021_comprehension_exp1",
    participant_id = .participant_id,
    age = unique(data_filtered$age),
    gender = unique(data_filtered$gender),
    first_language = unique(data_filtered$first_language),
    other_languages = unique(data_filtered$other_languages),
    handedness = unique(data_filtered$handedness),
    country_of_residence = unique(data_filtered$country_of_residence)
  )
}) |> 
  list_rbind()


# write to JSON lines -----------------------------------------------------

jsonlite::stream_out(
  prompts,
  file("prompts.jsonl.zip"),
  verbose = FALSE
)

# -------------------------------------------------------------------------