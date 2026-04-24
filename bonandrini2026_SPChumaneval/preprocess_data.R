################################################################################
#
#                   Pre-process data for PsychLing101
#
################################################################################

############################# Experiment 1 #####################################
#load data
library(readr)
E1 <- read_csv("original_data/Exp1.csv")

#remove timeout
E1 <- E1[E1$Accuracy!=99,]

participant_id <- E1$ID
trial_id <- E1$trial
stimulus <- NA
response_option_1 <- NA
response_option_2 <- NA
response <- E1$KEY
accuracy <- NA

for (i in 1:(dim(E1)[1])){
  stimulus[i] <- E1$target1[i]
  if (E1$targetwhere[i]=="left"){
    response_option_1[i] <- E1$stimulus[i]
    response_option_2[i] <- E1$foil[i]
  } else if (E1$targetwhere[i]=="right"){
    response_option_1[i] <- E1$foil[i]
    response_option_2[i] <- E1$stimulus[i]
  }
 if(E1$Accuracy[i]==1){
   accuracy[i] <- "Correct"
 } else if (E1$Accuracy[i]==0){
   accuracy[i] <- "Incorrect"
}
}

#create dataframe
E1_clean <- data.frame(participant_id, trial_id, stimulus, response_option_1, response_option_2, response, accuracy)
#write
write.csv(E1_clean, "exp1.csv")
#clear
rm(list=ls())#clear all
############################# Experiment 2 #####################################
#load data
library(readr)
E2 <- read_csv("original_data/Exp2.csv")

#remove timeout
E2 <- E2[E2$Accuracy!=99,]

participant_id <- E2$ID
trial_id <- E2$trial
stimulus <- NA
response_option_1 <- NA
response_option_2 <- NA
response <- E2$KEY
accuracy <- NA

for (i in 1:(dim(E2)[1])){
  stimulus[i] <- E2$target1[i]
  if (E2$targetwhere[i]=="left"){
    response_option_1[i] <- paste(E2$targetUP[i], E2$targetDOWN[i])
    response_option_2[i] <- paste(E2$foilUP[i], E2$foilDOWN[i])
  } else if (E2$targetwhere[i]=="right"){
    response_option_1[i] <- paste(E2$foilUP[i], E2$foilDOWN[i])
    response_option_2[i] <- paste(E2$targetUP[i], E2$targetDOWN[i])
  }
  if(E2$Accuracy[i]==1){
    accuracy[i] <- "Correct"
  } else if (E2$Accuracy[i]==0){
    accuracy[i] <- "Incorrect"
  }
}
E2_clean <- data.frame(participant_id, trial_id, stimulus, response_option_1, response_option_2, response, accuracy)
#write
write.csv(E2_clean, "exp2.csv")
#clear
rm(list=ls())#clear all

############################# Experiment 3 #####################################
#load data
library(readr)
E3 <- read_csv("original_data/Exp3.csv")

#remove timeout
E3 <- E3[E3$Accuracy!=99,]

participant_id <- E3$ID
trial_id <- E3$trial
stimulus <- NA
response_option_1 <- NA
response_option_2 <- NA
response <- E3$KEY
accuracy <- NA

for (i in 1:(dim(E3)[1])){
  stimulus[i] <- paste(E3$targetUP[i], E3$targetDOWN[i])
  if (E3$targetwhere[i]=="left"){
    response_option_1[i] <- E3$stimulus[i]
    response_option_2[i] <- E3$foil[i]
  } else if (E3$targetwhere[i]=="right"){
    response_option_1[i] <- E3$foil[i]
    response_option_2[i] <- E3$stimulus[i]
  }
  if(E3$Accuracy[i]==1){
    accuracy[i] <- "Correct"
  } else if (E3$Accuracy[i]==0){
    accuracy[i] <- "Incorrect"
  }
}

E3_clean <- data.frame(participant_id, trial_id, stimulus, response_option_1, response_option_2, response, accuracy)
#write
write.csv(E3_clean, "exp3.csv")
#clear
rm(list=ls())#clear all
