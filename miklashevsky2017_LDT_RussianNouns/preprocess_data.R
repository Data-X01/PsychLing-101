library(dplyr)

## read data
data = read.csv("merged_data_DB_LDT_raw.csv", stringsAsFactors = FALSE)

## keep only critical variables
data =
  data[, c(
    "ExperimentName",
    "Subject",
    "Age",
    "NativeLanguage",
    "Sex",
    "Speciality",
    "word.Session.",
    "BlockList",
    "Procedure",
    "Stimulus.ACC",
    "Stimulus.CRESP",
    "Stimulus.RESP",
    "Stimulus.RT",
    "Type",
    "word.Block."
  )]

## remove practice
data = data[data$Procedure == "exp", ]
data$Procedure = NULL

## remove non-native speakers and testers
data = data[data$NativeLanguage == "Russian", ]

## check accuracy (save ids of participants with accuracy < 85%)
low_accuracy_ppts =
  data %>%
  group_by(Subject) %>%
  summarise(
    mean_accuracy = mean(Stimulus.ACC, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  filter(mean_accuracy < 0.85)

## remove participants with accuracy < 85%
bad_ids = low_accuracy_ppts$Subject
data = data[!data$Subject %in% bad_ids, ]

## correct trial_order to start with 0
data$BlockList = data$BlockList - 1

## rename variables
data =
  data %>%
  rename(
    response_mapping  = ExperimentName, ## add to CODEBOOK
    participant_id    = Subject,
    age               = Age,
    first_language    = NativeLanguage,
    gender            = Sex,
    education_subject = Speciality, ## add to CODEBOOK
    list              = word.Session.,
    trial_order       = BlockList,
    accuracy          = Stimulus.ACC,
    correct_response  = Stimulus.CRESP, ## add to CODEBOOK
    response          = Stimulus.RESP,
    rt                = Stimulus.RT,
    condition         = Type,
    target_word       = word.Block.
  )

## save preprocessed data
write.csv(data, "exp1.csv", row.names = FALSE)
