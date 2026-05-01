input_folder <- "original_data"
output_folder <- "processed_data"

dir.create(output_folder, showWarnings = FALSE)

old_processed <- list.files(output_folder, pattern = "[.]csv$", full.names = TRUE)
if (length(old_processed) > 0) {
  unlink(old_processed)
}

read_raw <- function(filename) {
  read.csv(file.path(input_folder, filename), check.names = FALSE, stringsAsFactors = FALSE)
}

standardize_gender <- function(x) {
  value <- trimws(tolower(x))
  standardized <- ifelse(
    value %in% c("f", "female", "woman", "women"),
    "Female",
    ifelse(
      value %in% c("m", "male", "man", "men"),
      "Male",
      ifelse(value %in% c("nonbinary", "non-binary", "non binary"), "Nonbinary", x)
    )
  )
  standardized
}

standardize_rating_file <- function(filename, experiment, task, scale_label) {
  df <- read_raw(filename)

  if ("workerid" %in% names(df)) {
    df$participant_id <- df$workerid
  } else if ("participant" %in% names(df)) {
    df$participant_id <- df$participant
  }

  df$trial_id <- seq_len(nrow(df))
  df$trial_order <- ave(df$trial_id, df$participant_id, FUN = seq_along) - 1
  df$gender <- standardize_gender(df$gender)
  df$stimulus <- df$item
  df$response <- df$rating
  df$experiment <- experiment
  df$task <- task
  df$rating_scale <- scale_label

  if (!"context" %in% names(df)) {
    df$context <- NA
  }
  if (!"sentence" %in% names(df)) {
    df$sentence <- NA
  }

  keep <- c(
    "experiment", "task", "participant_id", "age", "gender", "trial_id", "trial_order",
    "stimulus", "sentence", "context", "response", "rating_scale"
  )

  df[keep]
}

experiments <- list(
  exp1 = standardize_rating_file(
    "df_apt.csv",
    "exp1_aptness",
    "aptness rating",
    "1 = not apt; 7 = very apt"
  ),
  exp2 = standardize_rating_file(
    "df_con.csv",
    "exp2_concreteness",
    "concreteness rating",
    "1 = very abstract; 7 = very concrete"
  ),
  exp3 = standardize_rating_file(
    "df_cons.csv",
    "exp3_constituency",
    "constituency rating",
    "-3 = definitely the first word; 0 = both words equally metaphorical; +3 = definitely the second word"
  ),
  exp4 = standardize_rating_file(
    "df_fam.csv",
    "exp4_familiarity",
    "familiarity rating",
    "1 = not familiar; 7 = very familiar"
  ),
  exp5 = standardize_rating_file(
    "df_met.csv",
    "exp5_metaphoricity",
    "metaphoricity rating",
    "1 = very literal; 7 = very metaphorical"
  )
)

for (name in names(experiments)) {
  write.csv(
    experiments[[name]],
    file.path(output_folder, paste0(name, ".csv")),
    row.names = FALSE,
    na = ""
  )
}
