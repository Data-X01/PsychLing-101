library(readr)
library(dplyr)

# ── Input paths ──────────────────────────────────────────────────────────────
data_dir <- "original_data"

rawdata     <- read_tsv(file.path(data_dir, "ICP_raw_data.csv"))
sessiondata <- read_tsv(file.path(data_dir, "sessions.csv"))
subjdata    <- read_tsv(file.path(data_dir, "profiles.csv"))

dim(rawdata)
dim(sessiondata)
dim(subjdata)

# ── Filter participants ───────────────────────────────────────────────────────
# Keep Italian native speakers only
subjdata <- subjdata[subjdata$native_language == "Italiano", ]
subjdata <- subjdata[!is.na(subjdata$profile_id), ]

dim(subjdata)

# Keep only the first session they completed
sessiondata <- sessiondata[sessiondata$profile_id_session == 1, ]

dim(sessiondata)

# ── Merge ─────────────────────────────────────────────────────────────────────
alldata <- merge(rawdata,  sessiondata, by = "exp_id")
alldata <- merge(alldata,  subjdata,    by = "profile_id")

dim(alldata)
head(alldata)

# ── Drop unneeded columns ─────────────────────────────────────────────────────
drop_cols <- c(
  "exp_id", "rt_adjbox", "rt_zscore", "ua_id.x", "ua_id.y",
  "browser_id", "nw_acc", "w_acc", "score", "profile_id_session",
  "touch", "time_start", "time_end", "level_italian", "country","best_foreign", "handedness"
)
alldata <- alldata[, !colnames(alldata) %in% drop_cols]

head(alldata)

# ── Rename columns ────────────────────────────────────────────────────────────
alldata <- alldata %>% rename(
  participant_id       = profile_id,
  stimulus             = spelling,
  first_language       = native_language
)

head(alldata)
dim(alldata)

# ── Recode categorical values to English labels ───────────────────────────────
  
 alldata <- alldata %>%
  mutate(
    education = recode(
      education,
      "Dottorato" = "PhD",
      "Laurea magistrale" = "Master",
      "Laurea triennale" = "Bachelor",
      "Diploma" = "High_school",
      "Licenza media" = "Middle_school",
      "Licenza elementare" = "Primary_school"
    )
  )
 unique(alldata$education)
 
 alldata <- alldata %>%
  mutate(
    gender = recode(
      gender,
      "Femmina" = "Female",
      "Maschio" = "Male"
    )
  )
 unique(alldata$gender)
 
 alldata <- alldata %>%
  mutate(
    first_language = recode(
      first_language,
      "Italiano" = "Italian"
    )
  )
 unique(alldata$first_language)

# ── Codebook ──────────────────────────────────────────────────────────────────
codebook_master <- read_csv("original_data/CODEBOOKmaster.csv") # Call the original CODEBOOK

codebook <- codebook_master %>%
  filter(`Recommended Column Name` %in% colnames(alldata)) # Keep only needed columns

icp_specific <- data.frame(
  `Recommended Column Name` = c(
    "lexicality", "no_foreign_lang"
  ),
  Description = c(
    "Whether the linguistic stimulus is a real word (W) or a nonword (N).",
    "Number of foreign languages the participant reported speaking."
  ),
  check.names = FALSE
)

codebook <- bind_rows(codebook, icp_specific) # Merge new columns
codebook <- codebook[match(colnames(alldata), codebook$`Recommended Column Name`), ]

# ── Save ──────────────────────────────────────────────────────────────────────
out_dir <- "processed_data"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

write_csv(alldata,  file.path(out_dir, "ICP_L1.csv"))
write_csv(codebook, "CODEBOOK.csv")

cat("ICP_L1.csv:     ", nrow(alldata),  "rows,", ncol(alldata),  "columns\n")
cat("Saved CODEBOOK.csv: ", nrow(codebook), "rows\n")
