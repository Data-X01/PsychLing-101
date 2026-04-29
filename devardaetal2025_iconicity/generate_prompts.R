### convert psycholinguistic iconicity rating data into a zipped JSONL file suitable for fine-tuning and evaluating large language models ###

# input:   exp1.csv         
# output:  prompts.jsonl.zip 

# each JSON object contains:
#   - "text":           Full prompt (instructions + trial-by-trial stimuli with human ratings marked as <<rating>>)
#   - "experiment":     Experiment identifier ("exp1")
#   - "participant_id": Participant ID


library(dplyr)
library(jsonlite)

## import data
data <- read.csv("processed_data/exp1.csv", stringsAsFactors = FALSE)

# quick check: print column names and number of rows to verify correct loading
cat("Columns:", paste(colnames(data), collapse = ", "), "\n")
cat("Rows:", nrow(data), "\n\n")


## define the instructions text: the fixed preamble shown at the start of every participant's prompt
# as in the original study, instructions are given in Italian and then English

instructions <- "Nel seguente questionario ti verr\u00e0 chiesto di valutare circa 250 parole della lingua italiana in base alla loro ICONICIT\u00c0. Prima di iniziare, leggi attentamente le seguenti istruzioni. Alla pagina successiva troverai le stesse istruzioni in lingua inglese, nel caso l'italiano non sia la tua prima lingua. Alcune parole della lingua italiana ricordano il loro significato (ad esempio, per come 'suonano'). Queste parole sono definite 'iconiche'. Una persona potrebbe essere in grado di indovinare il significato delle parole iconiche anche se non conosce l'italiano. In questo studio, ti chiediamo di valutare quanto sono iconiche alcune parole su una scala da 1 a 7. Seleziona il punteggio 1 se la parola non \u00e8 affatto iconica, ovvero se non percepisci un legame tra il suono della parola e il suo significato. Seleziona il punteggio 7 se la parola \u00e8 molto iconica, ovvero se percepisci un legame molto forte tra il suono della parola e il suo significato. Tra le parole ad iconicit\u00e0 molto alta, che potrebbero ricevere il punteggio 7, troviamo 'boom', 'crash', 'bang' eccetera. Tra le parole a bassa iconicit\u00e0, che potrebbero ricevere un punteggio molto basso, troviamo 'ragione', 'manico', 'pensione'. Per fare un altro esempio, una parola come 'piccino' dovrebbe avere un valore di iconicit\u00e0 pi\u00f9 alto di 'azzurro'. Prima di valutare la parola, \u00e8 importante che la parola venga pronunciata ad alta voce, anche pi\u00f9 volte, e che ci si concentri sul suo significato. Cerca di concentrarti sul significato dell'intera parola, piuttosto che scomporla in pi\u00f9 parti. Per esempio, per valutare una parola come 'FONDAMENTA' pensa alle strutture interrate di sostegno di un edificio, piuttosto che alle parole 'FONDA' e 'MENTA', e concentrati su quanto il significato dell'intera parola sia simile alla pronuncia della parola 'FONDAMENTA'. Se non conosci il significato o la pronuncia di una parola, puoi selezionare la casella apposita. Ricorda di pronunciare la parola e di pensare attentamente al significato di ogni parola che valuterai. Nell'esprimere il tuo giudizio ricordati di utilizzare tutti i valori della scala e di non preoccuparti quanto spesso usi un certo valore. Per ogni parola dovrai scegliere il numero che meglio indica il tuo giudizio. Incominciamo? In this task you will be rating about 250 Italian words on their ICONICITY. Please read the following instructions very carefully as they are important for doing this task. Some Italian words sound like what they mean. These words are iconic. You might be able to guess the meaning of such a word even if you did not know Italian. Some words that might be rated high in iconicity are 'boom', 'crash', 'bang' because they sound very much like what they mean. Some words that might be rated low in iconicity are 'pensione', 'manico', 'ragione'. As another example, a word like 'piccino' should receive a higher iconicity value than 'azzurro'. In this task, you are going to rate words for how iconic they are. You will rate each word on a scale from 1 to 7. A rating of 1 indicates that the word is not at all iconic and does not at all sound like what it means. 7 indicates that the word is high in iconicity and sounds very much like what it means. It is important that you say the word out loud to yourself, and that you think about its meaning. If you are unsure of the meaning or the pronunciation of a word, you have the option of skipping it. Try to focus on the word meaning of the whole word, rather than decomposing it into parts. For example, when rating 'FONDAMENTA' think of the foundation of the house rather than 'FONDA' and 'MENTA' and rate how well the whole meaning relates to the sound of the whole word 'FONDAMENTA'. Please remember to say the word to yourself and to think about the meaning of each word. Ready to start?"


## approximate token count (to stay within the 32K token limit per participant)
# rough estimate: 1 token is about 4 characters (standard heuristic for European languages)

count_tokens_approx <- function(text) {
  nchar(text) / 4
}

TOKEN_LIMIT <- 32000  # maximum tokens allowed per participant prompt

# -----------------------------------------------------------------------------
# 4. Get sorted list of unique participant IDs
# -----------------------------------------------------------------------------

participant_ids <- sort(unique(data$participant_id))
cat("Number of participants:", length(participant_ids), "\n\n")

# -----------------------------------------------------------------------------
# 5. Define output paths
# -----------------------------------------------------------------------------

output_file <- "prompts.jsonl"      # temporary unzipped file (deleted after zipping)
zip_file    <- "prompts.jsonl.zip"  # final output

# -----------------------------------------------------------------------------
# 6. Trial formatting helper
#
# Formats a single trial as a natural-language sentence following the pattern
# used in PsychLing-101 datasets (cf. de Varda et al., 2024).
# The human iconicity rating is enclosed in << >> as required.
# trial_idx is 1-based for human readability.
# -----------------------------------------------------------------------------

format_trial <- function(trial_idx, stimulus, eng_translation, response) {
  paste0(
    "Trial ", trial_idx, ". ",
    "La parola italiana è: '", stimulus, "' (", eng_translation, "). ",
    "Quanto è iconica questa parola? ",
    "1 (Per niente iconica) 2 3 4 5 6 7 (Moltissimo iconica). ",
    "Hai valutato: <<", response, ">>"
  )
}

# -----------------------------------------------------------------------------
# 7. print_example_prompts: console preview for quick visual verification
#
# Prints the first n_trials trials for the first n_participants participants,
# using the same randomization seed as the main loop so output is consistent.
# -----------------------------------------------------------------------------

print_example_prompts <- function(df, n_participants = 2, n_trials = 5) {
  cat("\n", strrep("=", 70), "\n", sep = "")
  cat("EXAMPLE PROMPTS\n")
  cat(strrep("=", 70), "\n", sep = "")

  sample_ids <- sort(unique(df$participant_id))[
    seq_len(min(n_participants, length(unique(df$participant_id))))
  ]

  for (pid in sample_ids) {
    cat("\n", strrep("-", 70), "\n", sep = "")
    cat("PARTICIPANT:", pid, "\n")
    cat(strrep("-", 70), "\n\n")
    cat(instructions, "\n\n")

    # Reproduce the same randomization used during prompt generation
    sub_df <- df %>% filter(participant_id == pid)
    set.seed(as.integer(sub("rater_", "", pid)))
    sub_df <- sub_df[sample(nrow(sub_df)), ]

    for (i in seq_len(min(n_trials, nrow(sub_df)))) {
      row <- sub_df[i, ]
      cat(format_trial(i, row$stimulus, row$eng_translation, row$response), "\n")
    }
    cat("... (", nrow(sub_df), "trials total)\n")
  }
  cat("\n")
}

# -----------------------------------------------------------------------------
# 8. Main loop: build and write one JSON object per participant
# -----------------------------------------------------------------------------

con         <- file(output_file, open = "w", encoding = "UTF-8")
n_truncated <- 0

for (pid in participant_ids) {

  # --- 8a. Subset and randomize trial order ----------------------------------
  #
  # Randomizing stimulus order per participant prevents the LLM from learning
  # a fixed presentation order. A reproducible seed derived from the numeric
  # suffix of the participant ID (e.g., "rater_12" -> seed 12) ensures the
  # same randomization is reproduced on every run of the script.

  participant_data <- data %>% filter(participant_id == pid)

  seed_value <- as.integer(sub("rater_", "", pid))
  set.seed(seed_value)

  participant_data <- participant_data[sample(nrow(participant_data)), ]

  # --- 8b. Build trial lines -------------------------------------------------

  trial_lines <- mapply(
    format_trial,
    trial_idx       = seq_len(nrow(participant_data)),
    stimulus        = participant_data$stimulus,
    eng_translation = participant_data$eng_translation,
    response        = participant_data$response,
    SIMPLIFY        = TRUE
  )

  trials_text <- paste(trial_lines, collapse = "\n")

  # --- 8c. Assemble full prompt ----------------------------------------------
  #
  # Structure:
  #   [Instructions]
  #   ---
  #   Trial 1. ...
  #   Trial 2. ...
  #   ...

  full_text <- paste0(instructions, "\n\n---\n\n", trials_text)

  # --- 8d. Check token limit -------------------------------------------------
  #
  # If the assembled prompt exceeds ~32K tokens, trials are dropped from the
  # end until the prompt fits. A warning is printed for each affected participant.

  if (count_tokens_approx(full_text) > TOKEN_LIMIT) {

    n_truncated <- n_truncated + 1
    cat("WARNING: Participant", pid, "exceeds 32K token limit. Truncating trials.\n")

    instructions_tokens <- count_tokens_approx(instructions) + 10  # small buffer
    remaining_budget    <- TOKEN_LIMIT - instructions_tokens

    kept_trials <- c()
    for (trial in trial_lines) {
      trial_tokens <- count_tokens_approx(trial) + 1  # +1 for newline
      if (remaining_budget - trial_tokens < 0) break
      kept_trials      <- c(kept_trials, trial)
      remaining_budget <- remaining_budget - trial_tokens
    }

    trials_text <- paste(kept_trials, collapse = "\n")
    full_text   <- paste0(instructions, "\n\n---\n\n", trials_text)
  }

  # --- 8e. Serialize to JSON and write one line ------------------------------
  #
  # auto_unbox = TRUE: scalar strings are written as "value", not ["value"]
  # ensure_ascii = FALSE: preserves Italian characters (è, à, ù, etc.)

  json_obj <- toJSON(
    list(
      text           = full_text,
      experiment     = "exp1",
      participant_id = as.character(pid)
    ),
    auto_unbox   = TRUE,
    ensure_ascii = FALSE
  )

  writeLines(json_obj, con = con)
}

close(con)

# -----------------------------------------------------------------------------
# 9. Zip the JSONL file and remove the unzipped version
#    zip() creates a standard .zip archive; the JSONL is stored inside as
#    "prompts.jsonl" so it can be extracted with any standard unzip tool.
# -----------------------------------------------------------------------------

zip(zip_file, files = output_file)  # create zip archive containing the JSONL
file.remove(output_file)            # remove the temporary unzipped file
cat("Created zip archive:", zip_file, "\n")

# -----------------------------------------------------------------------------
# 10. Summary report
# -----------------------------------------------------------------------------

cat("\n=== Done ===\n")
cat("Output:                      ", zip_file, "\n")
cat("Participants written:         ", length(participant_ids), "\n")
cat("Participants truncated:       ", n_truncated, "\n")

# Approximate token count for the first participant as a sanity check
sample_pid  <- participant_ids[1]
sample_data <- data %>% filter(participant_id == sample_pid)
approx_tok  <- count_tokens_approx(instructions) +
               sum(nchar(sample_data$stimulus) + nchar(sample_data$eng_translation)) / 4 * 2
cat("Approx. tokens (sample participant):", round(approx_tok), "\n")

# -----------------------------------------------------------------------------
# 11. Print example prompts for visual verification
# -----------------------------------------------------------------------------

print_example_prompts(data, n_participants = 2, n_trials = 5)
