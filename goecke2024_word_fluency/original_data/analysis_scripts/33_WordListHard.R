#### Recode Wide ####
#### Retrieval Study 2022
#### last updated: 21th May 2022
#### Benjamin.Goecke@uni-ulm.de

#### basics ####
#### load packages
library(psych)
library(tidyr)
library(dplyr)
library(car)
library(lavaan)
library(semTools)
library(ggplot2)
library(naniar)

#### clean environment
rm(list = ls())

#### set working directory
setwd("../../01b_ScoredRawData/02_Scored/Gesamt") #change date to folder of last data backup

#### load functions
#source("../WideAufbereitung/functions/plot_idiff.R")

#### scorer 1 NB
data_long <-  read.csv2("wordlist_base_short_hard_nb_full_03-06-2022.csv", encoding="UTF-8") #JL data

#### start recode routine JL ####
#remove all rows with NA
#data <- na.omit(data)

#exchange -99 with NA
data_long <- data_long %>% replace_with_na(replace = list(flu = -99))
#alle nas auf rep mit 0 ersetzen?
table(is.na(data_long$rep))
data_long$rep[is.na(data_long$rep)] <- 0
#data_long <- data_long %>% tidyr::replace_na(list(rep))
table(is.na(data_long$rep))

table(data_long$rep)
table(data_long$flu)

#remove wrong VPCodes
data_long <- data_long %>%
  filter(vpcode_hd1 != "99TEST99" & vpcode_hd1 != "04TEST04" & vpcode_hd1 != "" & vpcode_hd1 != "00TEST00" & subject !="811805689")

data_long$trial_new <- paste0(data_long$blockcode, "_", data_long$trialnum)

#get wide format
words_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
words_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))
words_lat <- reshape(data_long, v.names="latency", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "response", "flu"))

names(words_flu)
names(words_rep)
names(words_lat)

words_rep$rep.instruct_WL1_base_1_NA <- NULL
words_rep$date <- NULL
words_rep$time <- NULL
words_rep$trialcode <- NULL
words_rep$subject <- NULL

words_flu$flu.instruct_WL1_base_1_NA <- NULL
words_flu$date <- NULL
words_flu$time <- NULL
words_flu$trialcode <- NULL
words_flu$subject <- NULL

words_lat$latency.instruct_WL1_base_1_NA <- NULL
words_lat$date <- NULL
words_lat$time <- NULL
words_lat$trialcode <- NULL
words_lat$rep <- NULL
words_lat$subject <- NULL

#merge flu and rep
data_wide <- merge(words_flu, words_rep, by="vpcode_hd1")
data_wide <- merge(data_wide, words_lat, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("WL", "wl", colnames(data_wide))
colnames(data_wide) <- sub("latency", "lat", colnames(data_wide))
colnames(data_wide) <- sub("rep", "nb_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "nb_flu", colnames(data_wide))


names(data_wide)

data_wide_NB <- data_wide



#### data AZ
data_long <-  read.csv2("wordlist_base_short_hard_az_full_03-06-2022.csv", encoding="UTF-8") #JL data

#### start recode routine VS ####
#remove all rows with NA
#data <- na.omit(data)

#exchange -99 with NA
data_long <- data_long %>% replace_with_na(replace = list(flu = -99))
#alle nas auf rep mit 0 ersetzen?
table(is.na(data_long$rep))
data_long$rep[is.na(data_long$rep)] <- 0
#data_long <- data_long %>% tidyr::replace_na(list(rep))
table(is.na(data_long$rep))

table(data_long$rep)
table(data_long$flu)

#remove wrong VPCodes
data_long <- data_long %>%
  filter(vpcode_hd1 != "99TEST99" & vpcode_hd1 != "04TEST04" & vpcode_hd1 != "" & vpcode_hd1 != "00TEST00" & subject !="811805689")

data_long$trial_new <- paste0(data_long$blockcode, "_", data_long$trialnum)

#get wide format
words_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
words_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))

names(words_flu)
names(words_rep)
names(words_lat)

words_rep$rep.instruct_WL1_base_1_NA <- NULL
words_rep$date <- NULL
words_rep$time <- NULL
words_rep$trialcode <- NULL
words_rep$subject <- NULL

words_flu$flu.instruct_WL1_base_1_NA <- NULL
words_flu$date <- NULL
words_flu$time <- NULL
words_flu$trialcode <- NULL
words_flu$subject <- NULL

#merge flu and rep
data_wide <- merge(words_flu, words_rep, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("WL", "wl", colnames(data_wide))
colnames(data_wide) <- sub("rep", "az_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "az_flu", colnames(data_wide))

names(data_wide)

data_wide_AZ <- data_wide



#### merge data and get sum scores ####

data_wide <- merge(data_wide_NB, data_wide_AZ, by="vpcode_hd1", all=T)

data_wide$nb_flu.instruct_wl1_base_hard_s_NA <- NULL
data_wide$nb_rep.instruct_wl1_base_hard_s_NA <- NULL
data_wide$lat.instruct_wl1_base_hard_s_NA <- NULL
data_wide$az_flu.instruct_wl1_base_hard_s_NA <- NULL
data_wide$az_rep.instruct_wl1_base_hard_s_NA <- NULL

data_wide$vpcode_hd1 <- as.factor(data_wide$vpcode_hd1)
data_wide <- data_wide %>% mutate_if(is.character, as.numeric)

data_wide$nb_sum_wl1_h <- rowSums(data_wide[grep("nb_flu.wl1.*", names(data_wide))], na.rm=T)
data_wide$nb_sum_wl2_h <- rowSums(data_wide[grep("nb_flu.wl2.*", names(data_wide))], na.rm=T)

data_wide$az_sum_wl1_h <- rowSums(data_wide[grep("az_flu.wl1.*", names(data_wide))], na.rm=T)
data_wide$az_sum_wl2_h <- rowSums(data_wide[grep("az_flu.wl2.*", names(data_wide))], na.rm=T)


names(data_wide)

psych::ICC(data_wide[, c("nb_sum_wl1_h", "az_sum_wl1_h")])
psych::ICC(data_wide[, c("nb_sum_wl1_h", "az_sum_wl1_h")])


#### write data ####

#write wide data file
#write.csv2(data_wide, paste0("../../../02_WideData/wordlist-hard_wide_", Sys.Date(), ".csv"), row.names = FALSE)



