library(readr)
library(dplyr)
library(jsonlite)

# ── Load processed data ───────────────────────────────────────────────────────
df <- read_csv(
  "processed_data/exp1.csv",
  na = "", show_col_types = FALSE
)

cat("Rows:", nrow(df), "\n")
cat("Participants:", n_distinct(df$participant_id), "\n")
head(df)

# ── Build prompts ─────────────────────────────────────────────────────────────
  
parts <- df %>%
  arrange(participant_id, trial_order) %>%
  group_by(participant_id) %>%
  group_split()

all_prompts <- vector("list", length(parts))

for (idx in seq_along(parts)) {

  df_part <- parts[[idx]] %>%
    arrange(trial_order)

  pid <- df_part$participant_id[1L]
  
  df_part$response_key <- ifelse(df_part$response == "W", "J", "F")

  instructions <- paste(
    "In questo test ti verranno presentate 100 sequenze di lettere; alcune di queste sono parole usate in italiano mentre altre sono non-parole inventate.",
    "Per ogni sequenza di lettere, dovrai indicare se si tratta di una parola oppure no premendo i tasti J o F.",
    "J: SI', conosco questa parola; F: NO, non conosco questa parola.",
    "Consiglio! Non rispondere SI' a parole che non conosci, perché le risposte positive a non-parole sono penalizzate fortemente!",
    "Consiglio! Le parole incluse nel test appaiono sia nella loro forma base, sia nella loro forma flessa.",
    "Ad esempio sono inclusi verbi coniugati e forme maschili/femminili e singolari/plurali di nomi e aggettivi.",
    "Sono inclusi anche clitici e prestiti linguistici comunemente usati in italiano."
  )

  trial_lines <- paste0(
    "Trial ", df_part$trial_order,
    ": '", df_part$stimulus, "'. ",
    "Response <<", df_part$response_key, ">>. ",
    "RT = <<", df_part$rt, ">> ms. ",
    ifelse(df_part$accuracy == 1, "Correct.", "Incorrect.")
  )

  prompt_text <- paste(
    instructions,
    "",
    paste(trial_lines, collapse = "\n"),
    sep = "\n"
  )

  all_prompts[[idx]] <- list(
  text = prompt_text,
  experiment = "ICP_L1",
  participant_id = as.integer(pid),
  rt = df_part$rt,
  accuracy = df_part$accuracy
  )
}

cat("Generated", length(all_prompts), "prompts\n")
n_distinct(df$participant_id)
cat("Participants:", n_distinct(df$participant_id), "\n")
cat(all_prompts[[1]]$text)

# ── Save ──────────────────────────────────────────────────────────────────────
out_dir    <- "."
jsonl_path <- file.path(out_dir, "prompts.jsonl")
zip_path   <- file.path(out_dir, "prompts.jsonl.zip")

con <- file(jsonl_path, open = "w", encoding = "UTF-8")
for (p in all_prompts) {
  writeLines(toJSON(p, auto_unbox = TRUE, na = "null"), con)
}
close(con)

# system(paste0(
  # '"C:/Program Files/7-Zip/7z.exe" a "',
  # zip_path,
  # '" "',
  # jsonl_path,
  # '"'
# ))

system(paste(
  "7z a",
  shQuote(zip_path),
  shQuote(jsonl_path)
))

cat("Saved", jsonl_path, "\n")
cat("Saved", zip_path, "\n")
file.info(jsonl_path)$size / 1024^2
#[1] 1198.713
file.info(zip_path)$size / 1024^2
#[1] 194.328

