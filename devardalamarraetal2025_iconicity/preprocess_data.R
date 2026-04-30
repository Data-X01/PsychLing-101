### import and prepare original data ###

library(readr)
original_data <- read_csv("original_data/all_data.csv")
names(original_data)

# columns c(1:8) and 38 are the ones collected in this study, the others are other psycholinguistic variables which were used to run correlational analysis 
# in the original study, but were collected in other studies (see the original study for reference: https://doi.org/10.1371/journal.pone.0337947).

# in this script, we focus on the columns collected for this study

## rename columns according to codebook
codebook <- read_csv("CODEBOOK.csv")
print(codebook$`Recommended Column Name`)

## required variables added previously to codebook
library(dplyr)
# codebook_new <- codebook %>%
#   add_row(
#     `Recommended Column Name` = c(
#       "group", "eng_translation", "word_class", "word_length", "first_language",
#       "second_language", "lexita_self_cefr", "lexita_score",
#       "Auditory", "Gustatory", "Haptic", "Ita_Word_y", "M_AoA",
#       "M_Aro", "M_Con", "M_Dom", "M_Fam", "M_Ima", "M_Val", "Olfactory", "SD_AoA",
#       "Specificity_scaled", "Visual", "WF_Subtlex", "density_fastText",
#       "ldt_acc", "ldt_rt", "ldt_rt_z", "letter_freq", "mag_percept",
#       "max_percept", "mean_percept", "min_percept", "mink_percept",
#       "mod_e", "mod_exc", "nt_acc", "nt_rt", "nt_rt_z"
#     ),
#     Description = c(
#       "The participant's group (1 for L1 Italian speaker, 2 for L2 Italian speaker)",
#       "English translation of the Italian target word",
#       "Syntactic class of the target word",
#       "Length of the target word",
#       "Participant's first language",
#       "Participant's second language",
#       "Participant's score in LexIta according to CEFR levels",
#       "Participant's score in LexIta",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Repeated variable from the original dataset (unused)",
#       "Variable from ANEW",
#       "Variable from ANEW",
#       "Variable from ANEW",
#       "Variable from ANEW",
#       "Variable from ANEW",
#       "Variable from ANEW",
#       "Variable from ANEW",
#       "Variable from Italian perceptual norms",
#       "Standardized Age of Acquisition",
#       "Variable from ANEW specificity ratings",
#       "Variable from Italian perceptual norms",
#       "Word frequency from SUBTLEX-IT",
#       "Density from FastText",
#       "Accuracy in the lexical decision task",
#       "Reaction time in the lexical decision task",
#       "Z-scored reaction time in the lexical decision task",
#       "Letter frequency",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Variable from Italian perceptual norms",
#       "Accuracy in the naming task",
#       "Reaction time in the naming task",
#       "Z-scored reaction time in the naming task"
#     )
#   )
# 
# write.csv(codebook_new, "CODEBOOK.csv", row.names = FALSE)


processed_data <- original_data %>% 
  rename(participant_id = participant, 
         stimulus = word,
         response = rating,
         group = L,
         target_word = Ita_Word_x,
         eng_translation = Eng_Word,
         word_length = length,
         word_class = WordClass) 


names(processed_data)

## add demographic info per participant
# languages
processed_data <- processed_data %>%
  mutate(
    first_language  = if_else(group == 1, "ita", "eng"),
    second_language = if_else(group == 1, "", "ita")
  )

names(processed_data)

# Italian competence level (LexIta proficiency scores) only for L2 Ita speakers
lexita <- read.delim("original_data/all_lexita.tsv")
names(lexita)

lexita <- lexita %>% 
  rename(participant_id = id, 
         lexita_self_cefr = self_cefr,
         lexita_score = score) 
names(lexita)

processed_data <- processed_data %>%
  left_join(lexita, by = "participant_id")

names(processed_data)


## order columns
processed_data_final <- processed_data[, c(1:8, 38, 41:44, 9:37, 39:40)]
names(processed_data_final)
# columns c(1:13) are now the ones collected in this study

### save processed data file ###

write.csv(processed_data_final,
          "processed_data/exp1.csv",
          row.names = FALSE,
          fileEncoding = "UTF-8")

