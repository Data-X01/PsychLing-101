# preprocess data from EPLeP for PsychLing-101

library(dplyr)

raw_filenames <- list.files(path = "original_data/",
                                  recursive = TRUE)

eplep_exp1 <- read.table(paste('original_data/',raw_filenames[1],sep=''),
                         header = TRUE, sep = ",", dec = ".")
eplep_exp2 <- read.table(paste('original_data/',raw_filenames[2],sep=''),
                         header = TRUE, sep = ",", dec = ".")
eplep_exp3 <- read.table(paste('original_data/',raw_filenames[3],sep=''),
                         header = TRUE, sep = ",", dec = ".")
eplep_exp4 <- read.table(paste('original_data/',raw_filenames[4],sep=''),
                         header = TRUE, sep = ",", dec = ".")

new_labels <- c('participant_id','phase_id','trial_order','list','stimulus','condition','catch','response','accuracy','rt','age')

colnames(eplep_exp1) <- new_labels
colnames(eplep_exp2) <- new_labels
colnames(eplep_exp3) <- new_labels
colnames(eplep_exp4) <- new_labels

eplep_exp1 <-
  eplep_exp1 %>%
  mutate(accuracy = case_when(
    accuracy == 1 ~ 1,
    accuracy == 2 ~ 0,
    accuracy == 3 ~ 0))

eplep_exp2 <-
  eplep_exp2 %>%
  mutate(accuracy = case_when(
    accuracy == 1 ~ 1,
    accuracy == 2 ~ 0,
    accuracy == 3 ~ 0))

eplep_exp3 <-
  eplep_exp3 %>%
  mutate(accuracy = case_when(
    accuracy == 1 ~ 1,
    accuracy == 2 ~ 0,
    accuracy == 3 ~ 0))

eplep_exp4 <-
  eplep_exp4 %>%
  mutate(accuracy = case_when(
    accuracy == 1 ~ 1,
    accuracy == 2 ~ 0,
    accuracy == 3 ~ 0))

# export processed data as csv
write.csv(eplep_exp1, "processed_data/exp1.csv")
write.csv(eplep_exp2, "processed_data/exp2.csv")
write.csv(eplep_exp3, "processed_data/exp3.csv")
write.csv(eplep_exp4, "processed_data/exp4.csv")
