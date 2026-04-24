library(dplyr)
library(readr)
library(stringr)

# -----------------------------
# Paths
# -----------------------------
input_file <- "original_data/mousetracking.csv"
output_dir <- "processed_data"
output_file <- file.path(output_dir, "exp1.csv")

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# -----------------------------
# Read raw data
# -----------------------------
df <- read_csv(input_file, show_col_types = FALSE)

# -----------------------------
# Preprocess
# -----------------------------
df_clean <- df %>%
  # remove accidental repeated header rows inside the csv
  filter(
    VP != "VP",
    trial_type != "trial_type",
    trial_number != "trial_number",
    word != "word",
    resp_loc != "resp_loc",
    correctness != "correctness",
    part != "part",
    block != "block",
    block_number != "block_number",
    version != "version"
  ) %>%
  # keep only real experimental drag-response trials
  filter(trial_type == "mouse-drag-response") %>%
  # keep rows with a real stimulus
  filter(!is.na(word), word != "") %>%
  select(
    VP,
    trial_number,
    version,
    part,
    block,
    block_number,
    word,
    word_loc,
    resp_loc,
    start_rt,
    end_rt,
    end_loc,
    correctness,
    concreteness,
    age,
    gender,
    handedness,
    device,
    item
  ) %>%
  rename(
    participant_id = VP,
    trial_id = trial_number,
    phase_id = part,
    stimulus = word,
    stimulus_location = word_loc,
    response = end_loc,
    condition = resp_loc,
    accuracy = correctness,
    device_type = device
  ) %>%
  mutate(
    participant_id = as.character(participant_id),
    trial_id = suppressWarnings(as.integer(trial_id)),
    trial_order = suppressWarnings(as.integer(trial_order)),
    version = suppressWarnings(as.integer(version)),
    phase_id = as.character(phase_id),
    block = suppressWarnings(as.integer(block)),
    block_number = suppressWarnings(as.integer(block_number)),
    stimulus = as.character(stimulus),
    stimulus_location = str_to_lower(as.character(stimulus_location)),
    condition = str_to_lower(as.character(condition)),
    response = str_to_lower(as.character(response)),
    start_rt = suppressWarnings(as.numeric(start_rt)),
    end_rt = suppressWarnings(as.numeric(end_rt)),
    accuracy = suppressWarnings(as.integer(accuracy)),
    concreteness = str_to_lower(as.character(concreteness)),
    age = suppressWarnings(as.numeric(age)),
    gender = str_to_lower(as.character(gender)),
    handedness = str_to_lower(as.character(handedness)),
    device_type = str_to_lower(as.character(device_type)),
    item = suppressWarnings(as.integer(item))
  ) %>%
  # define which response rule was active on that trial
  mutate(
    instruction_mapping = case_when(
      version == 1 & block_number %in% c(0, 1, 2) ~ "abstract_top_concrete_bottom",
      version == 1 & block_number %in% c(3, 4, 5) ~ "abstract_bottom_concrete_top",
      version == 2 & block_number %in% c(0, 1, 2) ~ "abstract_bottom_concrete_top",
      version == 2 & block_number %in% c(3, 4, 5) ~ "abstract_top_concrete_bottom",
      TRUE ~ NA_character_
    )
  ) %>%
  # reconstruct semantic response from motor response + current instruction
  mutate(
    response_category = case_when(
      instruction_mapping == "abstract_top_concrete_bottom" & response == "top" ~ "abstract",
      instruction_mapping == "abstract_top_concrete_bottom" & response == "bottom" ~ "concrete",
      instruction_mapping == "abstract_bottom_concrete_top" & response == "top" ~ "concrete",
      instruction_mapping == "abstract_bottom_concrete_top" & response == "bottom" ~ "abstract",
      TRUE ~ NA_character_
    )
  ) %>%
  arrange(participant_id, trial_order, trial_id)

# -----------------------------
# Save processed file
# -----------------------------
write_csv(df_clean, output_file, na = "")

# -----------------------------
# Checks
# -----------------------------

cat("Saved file:", output_file, "\n")
cat("Rows:", nrow(df_clean), "\n")
cat("Participants:", n_distinct(df_clean$participant_id), "\n")
cat("Versions:", paste(sort(unique(df_clean$version)), collapse = ", "), "\n")
cat("Phase IDs:", paste(sort(unique(df_clean$phase_id)), collapse = ", "), "\n")
cat("Block numbers:", paste(sort(unique(df_clean$block_number)), collapse = ", "), "\n")
cat("Instruction mappings:", paste(sort(unique(df_clean$instruction_mapping)), collapse = ", "), "\n")
cat("Responses:", paste(sort(unique(df_clean$response)), collapse = ", "), "\n")
cat("Response categories:", paste(sort(unique(df_clean$response_category)), collapse = ", "), "\n")
cat("Devices:", paste(sort(unique(df_clean$device_type)), collapse = ", "), "\n")