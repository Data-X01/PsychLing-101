script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
if (length(script_arg) != 1) {
  stop("Run this script with Rscript.")
}

script_path <- sub("^--file=", "", script_arg)
dataset_dir <- dirname(normalizePath(script_path))
input_path <- file.path(dataset_dir, "original_data", "pseudo_discreteR1_def.RData")
output_dir <- file.path(dataset_dir, "processed_data")

if (!file.exists(input_path)) {
  stop(paste("Missing source file:", input_path))
}
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

source_objects <- new.env(parent = emptyenv())
load(input_path, envir = source_objects)

required_objects <- c("dat_TP3", "dat_b3", "dat_a")
missing_objects <- required_objects[!vapply(required_objects, exists, logical(1), envir = source_objects)]
if (length(missing_objects) > 0) {
  stop(paste("Missing RData objects:", paste(missing_objects, collapse = ", ")))
}

normalize_gender <- function(values) {
  keys <- tolower(trimws(iconv(as.character(values), to = "ASCII//TRANSLIT")))
  keys <- gsub("\\s+", " ", keys)
  female <- c("mujer", "femenino")
  male <- c("hombre", "varon", "masculino")
  result <- rep("unspecified", length(keys))
  result[keys %in% female] <- "female"
  result[keys %in% male] <- "male"
  result
}

participant_ids <- function(source_ids, prefix) {
  paste0(prefix, "_", match(source_ids, unique(source_ids)))
}

trial_orders <- function(ids) {
  as.integer(ave(seq_along(ids), ids, FUN = seq_along) - 1)
}

write_processed <- function(data, filename) {
  path <- file.path(output_dir, filename)
  write.csv(data, path, row.names = FALSE, na = "", fileEncoding = "UTF-8")
  cat("Wrote:", path, "\n")
  cat("Rows:", nrow(data), "Participants:", length(unique(data$participant_id)), "\n")
}

# Experiment 1: dat_TP3 duplicates behavioral trials for target/control
# semantic comparisons. Retain the target comparison row once per trial.
raw_exp1 <- source_objects$dat_TP3[source_objects$dat_TP3$type == "target", , drop = FALSE]
pid1 <- participant_ids(raw_exp1$ID, "exp1")
order1 <- trial_orders(pid1)

exp1 <- data.frame(
  experiment = "martineztomas2026_discrete_emotionality_exp1",
  participant_id = pid1,
  trial_id = paste0("exp1_t", order1),
  trial_order = order1,
  phase_id = "production",
  stimulus = raw_exp1$Palabra,
  response = raw_exp1$response.text,
  emotion = raw_exp1$emotion,
  rt = round((raw_exp1$generation.stopped - raw_exp1$generation.started) * 1000, 3),
  age = as.integer(raw_exp1$edad),
  gender = normalize_gender(raw_exp1$género),
  stringsAsFactors = FALSE,
  check.names = FALSE
)

if (anyDuplicated(exp1[c("participant_id", "trial_id")])) {
  stop("Duplicate Experiment 1 participant/trial identifiers.")
}

# Experiment 2: novel-string to original-word decoding.
raw_exp2 <- source_objects$dat_b3
pid2 <- participant_ids(raw_exp2$ID, "exp2")
order2 <- trial_orders(pid2)

exp2 <- data.frame(
  experiment = "martineztomas2026_discrete_emotionality_exp2",
  participant_id = pid2,
  trial_id = paste0("exp2_t", order2),
  trial_order = order2,
  phase_id = "word_decoding",
  stimulus = raw_exp2$Palabra,
  target_word = raw_exp2$target_word,
  response = raw_exp2$response.text,
  emotion = raw_exp2$emotion,
  rt = round((raw_exp2$generation.stopped - raw_exp2$generation.started) * 1000, 3),
  age = as.integer(raw_exp2$edad),
  gender = normalize_gender(raw_exp2$género),
  stringsAsFactors = FALSE,
  check.names = FALSE
)

if (anyDuplicated(exp2[c("participant_id", "trial_id")])) {
  stop("Duplicate Experiment 2 participant/trial identifiers.")
}

# Experiment 3: novel-string to discrete-emotion decoding.
raw_exp3 <- source_objects$dat_a
pid3 <- participant_ids(raw_exp3$ID, "exp3")
order3 <- trial_orders(pid3)

exp3 <- data.frame(
  experiment = "martineztomas2026_discrete_emotionality_exp3",
  participant_id = pid3,
  trial_id = paste0("exp3_t", order3),
  trial_order = order3,
  phase_id = "emotion_decoding",
  stimulus = raw_exp3$Palabra,
  target_word = raw_exp3$target_word,
  response = raw_exp3$emotion_selected,
  response_correct = raw_exp3$emotion,
  accuracy = as.integer(raw_exp3$accuracy),
  emotion = raw_exp3$emotion,
  rt = round(raw_exp3$RTs * 1000, 3),
  age = as.integer(raw_exp3$edad),
  gender = normalize_gender(raw_exp3$género),
  stringsAsFactors = FALSE,
  check.names = FALSE
)

if (anyDuplicated(exp3[c("participant_id", "trial_id")])) {
  stop("Duplicate Experiment 3 participant/trial identifiers.")
}

for (data in list(exp1, exp2, exp3)) {
  if (any(is.na(data$rt)) || any(data$rt <= 0)) {
    stop("Missing or nonpositive reaction times detected.")
  }
  if (any(is.na(data$response)) || any(trimws(data$response) == "")) {
    stop("Missing or blank participant responses detected.")
  }
}

write_processed(exp1, "exp1.csv")
write_processed(exp2, "exp2.csv")
write_processed(exp3, "exp3.csv")
