# Preprocess MECO L1 (Siegelman et al., 2022; 2025) for PsychLing-101.
#
# Reads the word-level eye-tracking reports of release 2.0, version 2.1, and
# writes one tidy CSV per wave:
#
#     processed_data/exp1.csv   Wave 1, 13 samples
#     processed_data/exp2.csv   Wave 2, 16 samples
#
# One row = one word (interest area, IA) of one text read by one participant.
# Words that were never fixated are kept as rows.
#
# Source-data issues handled here (details in README.md)
# -------------------------------------------------------
# * Text identity. The source column trialid is documented as the text number,
#   but for six participants it runs one behind the text actually shown on a
#   stretch of trials. text_id is therefore established from the words
#   themselves: every trial is matched to the text of the reading materials it
#   was read from. The match is cross-checked against itemid, which carries the
#   text number up to a constant offset per sample, and the script stops if the
#   two disagree anywhere.
# * Presentation order. Wave 2 records the experiment's trial counter
#   (trialnum), which is kept as trial_order. It shows that 14 Danish
#   participants read text 12 first. Wave 1 has no such counter, so exp1 has
#   no trial_order column.
# * Duplicate rows. In Wave 2 every row of participant da_16 appears twice.
#   Exact duplicate rows are dropped.
# * Unfixated words. The source leaves all measures empty when a word was never
#   fixated. As in luke2018_provo and berzak2025_onestop, rt (total reading
#   time), fixation_count and run_count are set to 0 for these words and the
#   duration measures stay empty.
# * Go-past time. popEye stores 0 for words skipped during first-pass reading
#   and fixated only later, where go-past time is undefined. These 0s are set
#   to empty.
#
# Run from this folder: Rscript preprocess_data.R

suppressPackageStartupMessages({
  library(data.table)
  library(readxl)
  library(stringi)
})

ORIGINAL_DIR <- "original_data"
PROCESSED_DIR <- "processed_data"

# Sample code (source column lang) -> first language, per the MECO papers.
FIRST_LANGUAGE <- c(
  # Wave 1
  du = "Dutch", ee = "Estonian", en = "English", fi = "Finnish", ge = "German",
  gr = "Greek", he = "Hebrew", it = "Italian", ko = "Korean", no = "Norwegian",
  ru = "Russian", sp = "Spanish", tr = "Turkish",
  # Wave 2 (sample codes name the site where a language has several samples)
  ba = "Basque", bp = "Portuguese", ch_s = "Chinese", ch_t = "Chinese",
  da = "Danish", en_uk = "English", ge_po = "German", ge_zu = "German",
  hi_iiith = "Hindi", hi_iitk = "Hindi", ic = "Icelandic", ru_mo = "Russian",
  se = "Serbian", sp_ch = "Spanish"
)

WAVES <- list(
  list(
    name = "Wave 1", output = "exp1.csv",
    data = file.path(ORIGINAL_DIR, "wave1", "joint_l1_data_trimmed_version2.1.rda"),
    materials = function() {
      texts <- read.csv(file.path(ORIGINAL_DIR, "wave1", "supp_texts.csv"),
                        check.names = FALSE, encoding = "UTF-8")
      texts <- texts[!is.na(texts[[1]]) & texts[[1]] != "", ]
      rownames(texts) <- texts[[1]]
      texts[, 2:13]
    },
    # Sample code -> row of the materials table.
    rows = c(du = "Dutch", ee = "Estonian", en = "English", fi = "Finnish",
             ge = "German", gr = "Greek", he = "Hebrew", it = "Italian",
             ko = "Korean", no = "Norwegian", ru = "Russian", sp = "Spanish",
             tr = "Turkish")
  ),
  list(
    name = "Wave 2", output = "exp2.csv",
    data = file.path(ORIGINAL_DIR, "wave2", "joint_data_trimmed_wave2_version2.1.rda"),
    materials = function() {
      texts <- as.data.frame(read_excel(
        file.path(ORIGINAL_DIR, "wave2", "supp_texts_wave2.xlsx"), sheet = "Sheet1",
        .name_repair = "unique_quiet"))
      texts <- texts[!is.na(texts[[1]]), ]
      rownames(texts) <- texts[[1]]
      texts[, 2:13]
    },
    rows = c(ba = "Basque", bp = "Portuguese(Brazil)", ch_s = "Chinese(simplified)",
             ch_t = "Chinese(traditional)", da = "Danish", en_uk = "English (uk)",
             ge_po = "German Wave 2", ge_zu = "German Wave 2 Zurich",
             hi_iiith = "Hindi iiith", hi_iitk = "Hindi iitk", ic = "Icelandic",
             no = "Norwegian Wave 2", ru_mo = "Russian Wave 2", se = "Serbian",
             sp_ch = "Spanish(Chile)", tr = "Turkish Wave 2")
  )
)

# trial_order is written only where the source records it (Wave 2).
OUTPUT_COLUMNS <- c(
  "participant_id", "lab", "first_language", "text_id", "trial_order", "word_position",
  "sentence_number", "stimulus", "rt", "first_fixation_duration",
  "gaze_duration", "go_past_time", "fixation_count", "run_count", "is_fixated",
  "is_first_pass_skipped", "is_regressed_into", "is_regressed_out_of"
)

NGRAM <- 6
MIN_MATCH <- 0.9      # share of a trial's n-grams found in its text
MAX_RUNNER_UP <- 0.5  # share found in the best of the other eleven texts


# Text normalised for matching: whitespace, line-break markers, the '*' word
# separators of the simplified Chinese materials, quotation marks and
# zero-width characters removed; NFKC folds full-width digits.
normalise <- function(x) {
  x <- stri_trans_nfkc(x)
  x <- gsub("\\\\+n", "", x)
  x <- stri_replace_all_regex(x, "[\\s*\"'`´‘’‚“”„«»​‌‍﻿]", "")
  x
}

ngrams <- function(s, n = NGRAM) {
  k <- nchar(s)
  if (k < n) return(s)
  unique(substring(s, 1:(k - n + 1), n:k))
}


# Establish text_id for every participant x trial from its words.
identify_texts <- function(d, materials, rows) {
  text_grams <- lapply(names(rows), function(lab) {
    lapply(1:12, function(i) ngrams(normalise(as.character(materials[rows[[lab]], i]))))
  })
  names(text_grams) <- names(rows)

  trials <- d[order(wordnum), .(read = normalise(paste(word, collapse = ""))),
              by = .(uniform_id, lang, trialid, itemid)]
  scores <- t(mapply(function(lab, read) {
    g <- ngrams(read)
    vapply(text_grams[[lab]], function(tg) mean(g %in% tg), numeric(1))
  }, trials$lang, trials$read))
  best <- apply(scores, 1, which.max)
  best_score <- scores[cbind(seq_along(best), best)]
  runner_up <- apply(scores, 1, function(s) sort(s, decreasing = TRUE)[2])
  trials[, `:=`(text_id = best, score = best_score, runner_up = runner_up)]

  if (any(trials$score < MIN_MATCH) || any(trials$runner_up > MAX_RUNNER_UP)) {
    print(trials[score < MIN_MATCH | runner_up > MAX_RUNNER_UP])
    stop("Some trials do not match a single text of the reading materials.")
  }

  # Cross-check: itemid is the text number up to a constant offset per sample.
  trials[, offset := as.numeric(itemid) - text_id]
  offsets <- trials[, .(n_offsets = uniqueN(offset), offset = offset[1]), by = lang]
  if (any(offsets$n_offsets != 1)) {
    print(trials[lang %in% offsets[n_offsets != 1, lang]])
    stop("The matched texts disagree with itemid.")
  }
  if (anyDuplicated(trials[, .(uniform_id, text_id)])) {
    stop("A participant is assigned the same text twice.")
  }

  cat(sprintf("  text matching: %d trials, lowest match %.3f, highest runner-up %.3f\n",
              nrow(trials), min(trials$score), max(trials$runner_up)))
  moved <- trials[trialid != text_id]
  if (nrow(moved)) {
    cat(sprintf("  trialid corrected on %d trials of %d participants:\n",
                nrow(moved), uniqueN(moved$uniform_id)))
    for (p in unique(moved$uniform_id)) {
      m <- moved[uniform_id == p][order(trialid)]
      cat(sprintf("    %s: %s\n", p, paste(sprintf("%d->%d", m$trialid, m$text_id), collapse = ", ")))
    }
  }
  trials[, .(uniform_id, trialid, text_id)]
}


process_wave <- function(wave) {
  cat(sprintf("%s\n", wave$name))
  env <- new.env()
  load(wave$data, envir = env)
  d <- as.data.table(get("joint.data", envir = env))
  n_source <- nrow(d)

  duplicated_rows <- duplicated(d)
  if (any(duplicated_rows)) {
    cat(sprintf("  dropped %d exact duplicate rows (participants: %s)\n",
                sum(duplicated_rows),
                paste(unique(d$uniform_id[duplicated_rows]), collapse = ", ")))
    d <- d[!duplicated_rows]
  }
  if (anyDuplicated(d[, .(uniform_id, trialid, wordnum)])) {
    stop("Rows are not unique by participant, trial and word.")
  }
  stopifnot(all(d$lang %in% names(wave$rows)))

  texts <- identify_texts(d, wave$materials(), wave$rows)
  d <- merge(d, texts, by = c("uniform_id", "trialid"))

  fixated <- d$skip == 0
  stopifnot(identical(fixated, !is.na(d$dur)))
  # popEye's 0 placeholder for go-past time: exactly the first-pass skips.
  stopifnot(all((d$firstrun.gopast == 0) == (d$firstrun.skip == 1), na.rm = TRUE))

  out <- data.table(
    participant_id = d$uniform_id,
    lab = d$lang,
    first_language = unname(FIRST_LANGUAGE[d$lang]),
    text_id = d$text_id,
    word_position = d$wordnum,
    sentence_number = d$sentnum,
    stimulus = d$word,
    rt = ifelse(fixated, d$dur, 0),
    first_fixation_duration = d$firstfix.dur,
    gaze_duration = d$firstrun.dur,
    go_past_time = ifelse(d$firstrun.skip == 1, NA, d$firstrun.gopast),
    fixation_count = ifelse(fixated, d$nfix, 0),
    run_count = ifelse(fixated, d$nrun, 0),
    is_fixated = as.integer(fixated),
    is_first_pass_skipped = d$firstrun.skip,
    is_regressed_into = d$reg.in,
    is_regressed_out_of = d$reg.out
  )
  if ("trialnum" %in% names(d)) {
    out[, trial_order := d$trialnum]
    trials <- unique(out[, .(participant_id, text_id, trial_order)])
    if (anyDuplicated(trials[, .(participant_id, text_id)]) ||
        anyDuplicated(trials[, .(participant_id, trial_order)])) {
      stop("trialnum does not give one position per text and participant.")
    }
  }

  # Participants in sample order, then by the number in their identifier.
  participant_number <- as.integer(sub(".*_", "", out$participant_id))
  setorderv(out[, number := participant_number],
            c("lab", "number", "text_id", "word_position"))
  out[, number := NULL]
  setcolorder(out, intersect(OUTPUT_COLUMNS, names(out)))

  path <- file.path(PROCESSED_DIR, wave$output)
  fwrite(out, path, na = "")
  cat(sprintf("  wrote %s: %d rows (%d in source), %d participants, %d samples, %.1f%% of words fixated\n",
              path, nrow(out), n_source, uniqueN(out$participant_id),
              uniqueN(out$lab), 100 * mean(out$is_fixated)))
}


dir.create(PROCESSED_DIR, showWarnings = FALSE)
for (wave in WAVES) process_wave(wave)
