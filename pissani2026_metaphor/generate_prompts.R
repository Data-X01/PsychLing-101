library(jsonlite)

processed_folder <- "processed_data"
prompt_file <- "prompts.jsonl"
zip_file <- "prompts.jsonl.zip"

instruction_for <- function(experiment) {
  switch(
    experiment,
    exp1_aptness = paste(
      "Your task is to rate how apt you find the given metaphorical expression in UPPERCASE in the end.",
      "Try to use the full scale, with not so apt expressions rated more towards the middle (2, 3, 4, 5, 6), reserving 1 for truly not apt expressions and 7 for very apt ones.",
      "",
      "The expressions you will see are composed of two words, such as \"SILKY HAIR\". These expressions can be considered as containing two parts: the topic and the vehicle, where the topic is the subject of the metaphor and the vehicle is the word that modifies or describes this topic.",
      "",
      "For instance, in 'SILKY HAIR', 'SILKY' is the vehicle, and it describes 'HAIR', the topic. Note that vehicles can also be used to describe other topics, such as 'SILKY SUNSET' or 'SILKY LAKE'.",
      "",
      "In summary,",
      "Expression: SILKY HAIR",
      "Topic: HAIR",
      "Vehicle: SILKY",
      "",
      "For example, hair can be shiny and smooth. Consequently, 'SILKY HAIR' can be considered an apt expression, because 'SILKY' captures important features of the 'HAIR' (namely, shine and smoothness). A less apt statement would be 'SILKY SUNSET' since it may be less common for a sunset to be both shiny and smooth. Hence 'SILKY HAIR' would receive a higher aptness rating (perhaps 6 or 7), whereas 'SILKY SUNSET' would receive a lower aptness rating (perhaps 3 or 4).",
      "",
      "In another example, 'BRIDAL SHOWER', 'SHOWER' is the vehicle, and it is modified by 'BRIDAL'. Remember that vehicles can also be used with other topics, such as 'WEDDING SHOWER' or 'DIAPER SHOWER'.",
      "",
      "In summary,",
      "Expression: BRIDAL SHOWER",
      "Topic: BRIDAL PARTY",
      "Vehicle: SHOWER",
      "",
      "For example, at a bridal party, the bride is 'showered' with gifts. Consequently, 'BRIDAL SHOWER' can be considered an apt expression because 'shower' captures important features of a bridal party (namely, receiving many gifts resembling a rain shower). A less apt statement would be 'ANNIVERSARY SHOWER' since it may be less common to celebrate an anniversary by receiving numerous gifts. Hence 'BRIDAL SHOWER' would receive a higher aptness rating (perhaps 6 or 7), whereas 'ANNIVERSARY SHOWER' would receive a lower aptness rating (perhaps 3 or 4).",
      "",
      "In another example, 'ROUGH DIAMOND', both words together refer to someone with potential, but who lacks certain skills, such as education or social skills.",
      "In summary,",
      "Expression: ROUGH DIAMOND",
      "Implicit topic: someone with potential",
      "Vehicle: ROUGH DIAMOND",
      "",
      "For example, a diamond in the rough is the unpolished state of the diamond. Consequently, 'ROUGH DIAMOND' can be considered an apt expression, because it captures important features of someone with potential (namely, being uneducated or 'unpolished'). A less apt statement would be 'CHIN MUSIC', which refers to idle chatter, because there are no apparent features being transferred. Hence 'ROUGH DIAMOND' would receive a higher aptness rating (perhaps 6 or 7), whereas 'CHIN MUSIC' would receive a lower aptness rating (perhaps 1 or 2).",
      "Rate how apt the expression itself is as a metaphor or figurative phrase. Do NOT imagine additional context; base your judgment only on the expression as written.",
      "",
      "Scale Numerical: integer 1-7 (1=not apt at all, 7=very apt).",
      sep = "\n"
    ),
    exp2_concreteness = paste(
      "You will be shown a metaphorical expression. Rate how concrete the UPPERCASE expression is: how directly it can be perceived via the senses or simple actions (e.g., pointing, showing a picture). Rate the expression itself. Use the full scale.",
      "",
      "Examples and indicative ratings per scale:",
      "",
      "ZEBRA crossing - perceptible stripes -> concrete.",
      "- Numerical rating: 6 or 7",
      "",
      "SMALL talk - 'unimportant/uncontroversial' -> abstract.",
      "- Numerical rating: 2 or 3",
      "",
      "Truth BOMB - 'blunt or unexpected' -> abstract.",
      "- Numerical rating: 2 or 3",
      "",
      "WHITE ELEPHANT - 'of little or no value' -> abstract.",
      "- Numerical rating: 2 or 3",
      "",
      "Scale Numerical: 1 (abstract) ... 7 (very concrete).",
      sep = "\n"
    ),
    exp3_constituency = paste(
      "You will be presented with a two-word metaphorical expression. Decide which word carries more metaphorical content and how strongly. Base your judgment on typical English usage.",
      "",
      "Examples (two-word expressions) and how to rate them on this scale:",
      "",
      "SNAIL MAIL",
      "- Interpretation: SNAIL is metaphorical (slowness), MAIL is literal.",
      "- Rating: -3",
      "",
      "TIME BOMB",
      "- Interpretation: both TIME and BOMB contribute metaphorically; balanced.",
      "- Rating: 0",
      "",
      "MIND PRISON",
      "- Interpretation: PRISON is metaphorical (mental confinement), MIND is literal.",
      "- Rating: +3",
      "",
      "Scale: Numerical (-3 to +3 integer encoding direction and strength):",
      "-3 = Definitely the first word",
      "-2 = Mostly the first word",
      "-1 = Slightly more the first word",
      "0 = Both words equally metaphorical",
      "+1 = Slightly more the second word",
      "+2 = Mostly the second word",
      "+3 = Definitely the second word",
      sep = "\n"
    ),
    exp4_familiarity = paste(
      "You will be shown just the metaphorical expression in isolation, without any sentence context. Rate how familiar this metaphorical expression is: how often a typical native English speaker would have seen, heard, or read it before. Do NOT imagine extra context.",
      "",
      "Scale Numerical: 1 (not familiar at all) ... 7 (very familiar).",
      sep = "\n"
    ),
    exp5_metaphoricity = paste(
      "You will be shown a two-word expression. Rate how metaphorical that expression is: the extent to which you consider the expression to be literally or metaphorically true. Use the full scale.",
      "",
      "Examples and indicative ratings per scale:",
      "",
      "ROCKY TRAIL - straightforward terrain description -> very literal.",
      "- Numerical rating: 1 or 2",
      "",
      "SOFT WARNING - warnings are not literally soft/hard -> slightly metaphorical.",
      "- Numerical rating: 2 or 3",
      "",
      "SMOKE SCREENS - not literal smoke/screens -> highly metaphorical.",
      "- Numerical rating: 6 or 7",
      "",
      "Scale Numerical: 1 (very literal) ... 7 (very metaphorical).",
      sep = "\n"
    ),
    "In this study, you will be presented with linguistic stimuli and asked to provide ratings."
  )
}

format_trial <- function(row, trial_number) {
  response <- paste0("<<", row[["response"]], ">>")

  if (!is.na(row[["sentence"]]) && nzchar(row[["sentence"]])) {
    paste0(
      "Trial ", trial_number, ": The sentence is '", row[["sentence"]], "'. ",
      "The target expression is '", row[["stimulus"]], "'. ",
      "You rate ", response, "."
    )
  } else {
    paste0(
      "Trial ", trial_number, ": The expression is '", row[["stimulus"]], "'. ",
      "You rate ", response, "."
    )
  }
}

make_prompt <- function(df, participant_id) {
  participant_df <- df[df$participant_id == participant_id, , drop = FALSE]
  if ("trial_order" %in% names(participant_df)) {
    participant_df <- participant_df[order(participant_df$trial_order), , drop = FALSE]
  } else {
    participant_df <- participant_df[order(participant_df$trial_id), , drop = FALSE]
  }
  experiment <- participant_df$experiment[1]

  trials <- vapply(
    seq_len(nrow(participant_df)),
    function(i) format_trial(participant_df[i, , drop = FALSE], i),
    character(1)
  )

  item <- list(
    text = paste(c(instruction_for(experiment), trials), collapse = "\n\n"),
    experiment = experiment,
    participant_id = participant_id
  )

  if ("age" %in% names(participant_df) && !is.na(participant_df$age[1]) && nzchar(as.character(participant_df$age[1]))) {
    item$age <- participant_df$age[1]
  }
  if ("gender" %in% names(participant_df) && !is.na(participant_df$gender[1]) && nzchar(participant_df$gender[1])) {
    item$gender <- participant_df$gender[1]
  }

  item
}

csv_files <- list.files(processed_folder, pattern = "^exp[0-9]+[.]csv$", full.names = TRUE)
if (length(csv_files) == 0) {
  stop("No standardized exp*.csv files found in processed_data/. Run preprocess_data.R first.")
}

prompts <- list()
for (file in csv_files) {
  df <- read.csv(file, check.names = FALSE, stringsAsFactors = FALSE)
  required <- c("experiment", "participant_id", "trial_id", "stimulus", "response")
  missing <- setdiff(required, names(df))
  if (length(missing) > 0) {
    stop(paste("Missing required columns in", file, ":", paste(missing, collapse = ", ")))
  }

  participant_ids <- unique(df$participant_id)
  for (participant_id in participant_ids) {
    prompts[[length(prompts) + 1]] <- make_prompt(df, participant_id)
  }
}

json_lines <- vapply(prompts, toJSON, character(1), auto_unbox = TRUE, na = "null")
writeLines(json_lines, prompt_file, useBytes = TRUE)

too_long <- vapply(prompts, function(x) nchar(x$text, type = "chars") > 128000, logical(1))
if (any(too_long)) {
  stop("At least one prompt may exceed the 32K token limit.")
}

if (file.exists(zip_file)) {
  unlink(zip_file)
}
utils::zip(zipfile = zip_file, files = prompt_file, flags = "-q")
