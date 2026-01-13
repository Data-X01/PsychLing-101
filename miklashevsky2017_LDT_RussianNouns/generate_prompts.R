library(dplyr)
library(readr)
library(jsonlite)

## read data
data = read_csv("processed_data/exp1.csv", show_col_types = FALSE)

all_prompts = list()

participants_list = unique(data$participant_id)
trials_exp1 = 0:max(data$trial_order, na.rm = TRUE)

instruction_practice_mapping1 =
  paste0(
    'Здравствуйте!\n',
    'Спасибо, что согласились принять участие в эксперименте.\n',
    'Сейчас перед Вами будут появляться стимулы - слова и псевдослова (последовательности букв, поxожие на слова). Ваша задача - нажать на нужную клавишу:\n',
    '1 - если перед Вами настоящее слово\n',
    '2 - если перед Вами не настоящее слово (псевдослово).\n',
    'Сначала будет небольшая тренировка, чтобы Вы могли лучше понять задание.\n',
    'Нажмите пробел, чтобы продолжить.\n'
  )

instruction_main_experiment_mapping1 =
  paste0(
    'Поxоже, что Вы уже освоились. Сейчас начнется настоящий эксперимент.\n',
    'Помните, Ваша задача - нажать на нужную клавишу:\n',
    '1 - если перед Вами настоящее слово\n',
    '2 - если перед Вами не настоящее слово (псевдослово).\n',
    'Готовы?\n',
    'Нажмите пробел, чтобы продолжить.\n'
  )

instruction_practice_mapping2 =
  paste0(
    'Здравствуйте!\n',
    'Спасибо, что согласились принять участие в эксперименте.\n',
    'Сейчас перед Вами будут появляться стимулы - слова и псевдослова (последовательности букв, поxожие на слова). Ваша задача - нажать на нужную клавишу:\n',
    '2 - если перед Вами настоящее слово\n',
    '1 - если перед Вами не настоящее слово (псевдослово).\n',
    'Сначала будет небольшая тренировка, чтобы Вы могли лучше понять задание.\n',
    'Нажмите пробел, чтобы продолжить.\n'
  )

instruction_main_experiment_mapping2 =
  paste0(
    'Поxоже, что Вы уже освоились. Сейчас начнется настоящий эксперимент.\n',
    'Помните, Ваша задача - нажать на нужную клавишу:\n',
    '2 - если перед Вами настоящее слово\n',
    '1 - если перед Вами не настоящее слово (псевдослово).\n',
    'Готовы?\n',
    'Нажмите пробел, чтобы продолжить.\n'
  )

# participant-level info (all columns that are constant within participant)
participant_info =
  data %>%
  group_by(participant_id) %>%
  summarise(
    response_mapping   = first(response_mapping),
    age                = first(age),
    first_language     = first(first_language),
    gender             = first(gender),
    education_subject  = first(education_subject),
    list               = first(list),
    .groups = "drop"
  )

for (ppt in participants_list) {
  
  exp_participant = data %>% filter(participant_id == ppt)
  info = participant_info %>% filter(participant_id == ppt)
  
  mapping = info$response_mapping[1]
  
  if (mapping == "DB_LD_1") {
    instruction_practice = instruction_practice_mapping1
    instruction_main = instruction_main_experiment_mapping1
  } else {
    instruction_practice = instruction_practice_mapping2
    instruction_main = instruction_main_experiment_mapping2
  }
  
  individual_prompt = paste0(instruction_practice, "\n", instruction_main, "\n")
  
  for (trial in trials_exp1) {
    exp_trial = exp_participant %>% filter(trial_order == trial)
    if (nrow(exp_trial) > 0) {
      
      stimulus  = exp_trial$target_word[1]
      response  = exp_trial$response[1]
      correct   = exp_trial$correct_response[1]
      rt        = exp_trial$rt[1]
      condition = exp_trial$condition[1]
      acc       = exp_trial$accuracy[1]
      block     = exp_trial$BlockList[1]
      
      datapoint =
        paste0(
          "trial ", trial, ": ",
          stimulus, " (", condition, "). ",
          "Correct response: ", correct,
          ". You press <<", response, ">>",
          ". ACC=", acc,
          ". RT=", rt, "ms.\n"
        )
      
      individual_prompt = paste0(individual_prompt, datapoint)
    }
  }
  
  all_prompts[[length(all_prompts) + 1]] = list(
    text = individual_prompt,
    experiment = "myexperiment2017_LDT",
    participant = ppt,
    participant_info = as.list(info)
  )
}

# Save all prompts to JSONL file
con = file("prompts.jsonl", open = "w", encoding = "UTF-8")
for (i in seq_along(all_prompts)) {
  writeLines(toJSON(all_prompts[[i]], auto_unbox = TRUE, null = "null"), con)
}
close(con)