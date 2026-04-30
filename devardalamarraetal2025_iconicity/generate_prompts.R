### convert psycholinguistic iconicity rating data into a zipped JSONL file suitable for fine-tuning and evaluating large language models ###

# input:   exp1.csv         
# output:  prompts.jsonl.zip 

# each JSON object contains:
#   - "text":           Full prompt (instructions + trial-by-trial stimuli with human ratings marked as <<rating>>)
#   - "experiment":     Experiment identifier ("exp1")
#   - "participant_id": Participant ID
#   - "group":          Participant's group (1=L1 Ita, 2=L2 Ita)
#   - first_language:   Participant's first language
#   - second_language:  Participant's second language
#   - lexita_self_cefr: Participant's score in LexIta according to CEFR levels
#   - lexita_score:     Participant's score in LexIta


library(dplyr)
library(jsonlite)

## import data
data <- read.csv("processed_data/exp1.csv", stringsAsFactors = FALSE)
data$response <- round(data$response) #to shorten answers with decimals

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


## create sorted list of unique participant IDs

participant_ids <- sort(unique(data$participant_id))
cat("Number of participants:", length(participant_ids), "\n\n")


## define output paths

output_file <- "prompts.jsonl"      # temporary unzipped file 
zip_file    <- "prompts.jsonl.zip"  # final output


## format trial  

format_trial <- function(trial_idx, stimulus, response) {
  paste0(
    "Trial ", trial_idx, ". ",
    "La parola italiana è: '", stimulus, "'. ",
    "Quanto è iconica questa parola? ",
    "1 (Per niente iconica) 2 3 4 5 6 7 (Moltissimo iconica). ",
    "Hai valutato: <<", response, ">>"
  )
}

# function to print examples 

print_example_prompts <- function(df, n_participants = 2, n_trials = 5) {
  cat("\n", strrep("=", 70), "\n", sep = "")
  cat("EXAMPLE PROMPTS\n")
  cat(strrep("=", 70), "\n", sep = "")
  
  # select the first n_participants 
  sample_ids <- sort(unique(df$participant_id))[
    seq_len(min(n_participants, length(unique(df$participant_id))))
  ]
  
  # print participant header
  for (pid in sample_ids) {
    cat("\n", strrep("-", 70), "\n", sep = "")
    cat("PARTICIPANT:", pid, "\n")
    cat(strrep("-", 70), "\n\n")
    
    # print the prompt
    cat(instructions, "\n\n")

    # subset this participant's trials applying the same randomization used for prompt generation
    sub_df <- df %>% filter(participant_id == pid)
    set.seed(as.integer(sub("rater_", "", pid)))
    sub_df <- sub_df[sample(nrow(sub_df)), ]

    # print the fist _trials
    for (i in seq_len(min(n_trials, nrow(sub_df)))) {
      row <- sub_df[i, ]
      cat(format_trial(i, row$stimulus, row$response), "\n")
    }
    
    # total n of completed trials per participant
    cat("... (", nrow(sub_df), "trials total)\n")
  }
  cat("\n")
}


## build and write one JSON object per participant

con <- file(output_file, open = "w", encoding = "UTF-8")
n_truncated <- 0

for (pid in participant_ids) {

  # subset and randomize trial order 
  participant_data <- data %>% filter(participant_id == pid)

  seed_value <- as.integer(sub("rater_", "", pid))
  set.seed(seed_value)

  participant_data <- participant_data[sample(nrow(participant_data)), ]

  # build trial's rows
  trial_lines <- mapply(
    format_trial,
    trial_idx = seq_len(nrow(participant_data)),
    stimulus  = participant_data$stimulus,
    response  = participant_data$response,
    SIMPLIFY  = TRUE
  )

  trials_text <- paste(trial_lines, collapse = "\n")

  # assemble full prompt
  full_text <- paste0(instructions, "\n\n---\n\n", trials_text)

  # check token limit; if reached, trials are dropped from the end until the prompt fits
  if (count_tokens_approx(full_text) > TOKEN_LIMIT) {

    n_truncated <- n_truncated + 1
    cat("WARNING: Participant", pid, "exceeds 32K token limit. Truncating trials.\n")

    instructions_tokens <- count_tokens_approx(instructions) + 10  
    remaining_budget    <- TOKEN_LIMIT - instructions_tokens

    kept_trials <- c()
    for (trial in trial_lines) {
      trial_tokens <- count_tokens_approx(trial) + 1  # +1 for newline
      if (remaining_budget - trial_tokens < 0) break # stop if next trial won't fit
      kept_trials      <- c(kept_trials, trial)
      remaining_budget <- remaining_budget - trial_tokens
    }
    
    # rebuild the prompt with only the trials that fit
    trials_text <- paste(kept_trials, collapse = "\n")
    full_text   <- paste0(instructions, "\n\n---\n\n", trials_text)
  }
  
  # additional limit: truncate at 100,000 characters if needed (GitHub file line limit)
  if (nchar(full_text) > 100000) {
    
    cat("WARNING: Participant", pid, "exceeds 100,000 character limit. Truncating.\n")
    
    # Rebuild trial by trial, stopping before the character limit
    char_budget <- 100000 - nchar(instructions) - nchar("\n\n---\n\n") - 10  
    
    kept_trials <- c()
    for (trial in trial_lines) {
      trial_chars <- nchar(trial) + 1  # +1 for newline
      if (char_budget - trial_chars < 0) break
      kept_trials  <- c(kept_trials, trial)
      char_budget  <- char_budget - trial_chars
    }
    
    trials_text <- paste(kept_trials, collapse = "\n")
    full_text   <- paste0(instructions, "\n\n---\n\n", trials_text)
  }

  # convert the prompt to a JSON object with three fields: text, experiment, participant_id.
  json_obj <- toJSON(
    list(
      text             = full_text,
      experiment       = "exp1",
      participant_id   = as.character(pid),
      group            = as.integer(participant_data$group[1]),
      first_language   = as.character(participant_data$first_language[1]),
      second_language  = as.character(participant_data$second_language[1]),
      lexita_self_cefr = as.character(participant_data$lexita_self_cefr[1]),
      lexita_score     = as.numeric(participant_data$lexita_score[1])
    ),
    auto_unbox   = TRUE,
    ensure_ascii = FALSE
  )

  writeLines(json_obj, con = con)
}

close(con)


## zip the JSONL file

zip::zip(zip_file, files = output_file)
cat("Created zip archive:", zip_file, "\n")

## summary report

cat("\n=== Done ===\n")
cat("Output:                      ", zip_file, "\n")
cat("Participants written:         ", length(participant_ids), "\n")
cat("Participants truncated for token limit:       ", n_truncated, "\n")

## approximate token count for the first participant as a sanity check
sample_pid  <- participant_ids[1]
sample_data <- data %>% filter(participant_id == sample_pid)
approx_tok  <- count_tokens_approx(instructions) +
  sum(nchar(sample_data$stimulus)) / 4 * 2
cat("Approx. tokens (sample participant):", round(approx_tok), "\n")


## print example prompts for visual verification
print_example_prompts(data, n_participants = 2, n_trials = 5)

