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
setwd("../../01b_ScoredRawData/02_Scored/Pre") #change date to folder of last data backup

#### load functions
#source("../WideAufbereitung/functions/plot_idiff.R")

#### data VS
data_long <-  read.csv2("synonym_base_short_VS1_19-04-2022_copy.csv", encoding="UTF-8") #JL data
data_long_snippet2 <-  read.csv2("../Gesamt/snippet2/synonym_short_VS_full_03-06-2022_snippet2.csv", encoding="UTF-8") #JL data

data_long <- rbind(data_long, data_long_snippet2)
rm(data_long_snippet2)


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
syn_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
syn_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))
syn_lat <- reshape(data_long, v.names="latency", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "response", "flu"))

names(syn_flu)
names(syn_rep)
names(syn_lat)

syn_rep$rep.instruct_NA <- NULL
syn_rep$date <- NULL
syn_rep$time <- NULL
syn_rep$trialcode <- NULL
syn_rep$subject <- NULL

syn_flu$flu.instruct_NA <- NULL
syn_flu$date <- NULL
syn_flu$time <- NULL
syn_flu$trialcode <- NULL
syn_flu$subject <- NULL

syn_lat$latency.instruct_NA <- NULL
syn_lat$date <- NULL
syn_lat$time <- NULL
syn_lat$trialcode <- NULL
syn_lat$rep <- NULL
syn_lat$subject <- NULL

#merge flu and rep
data_wide <- merge(syn_flu, syn_rep, by="vpcode_hd1")
data_wide <- merge(data_wide, syn_lat, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("FS", "syn", colnames(data_wide))
colnames(data_wide) <- sub("latency", "lat", colnames(data_wide))
colnames(data_wide) <- sub("rep", "vs_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "vs_flu", colnames(data_wide))
colnames(data_wide) <- sub("base", "short", colnames(data_wide))


names(data_wide)

data_wide_VS <- data_wide






#### data KH
data_long <-  read.csv2("synonym_base_short_KH1_19-04-2022_copy.csv", encoding="UTF-8") #kH data
data_long_snippet2 <-  read.csv2("../Gesamt/snippet2/synonym_short_kh_full_03-06-2022_snippet2.csv", encoding="UTF-8", sep=";") #KH data


data_long <- rbind(data_long, data_long_snippet2)
rm(data_long_snippet2)


#### start recode routine KH ####
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
syn_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
syn_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))

names(syn_flu)
names(syn_rep)
names(syn_lat)

syn_rep$rep.instruct_NA <- NULL
syn_rep$date <- NULL
syn_rep$time <- NULL
syn_rep$trialcode <- NULL
syn_rep$subject <- NULL

syn_flu$flu.instruct_NA <- NULL
syn_flu$date <- NULL
syn_flu$time <- NULL
syn_flu$trialcode <- NULL
syn_flu$subject <- NULL
#merge flu and rep
data_wide <- merge(syn_flu, syn_rep, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("FS", "syn", colnames(data_wide))
colnames(data_wide) <- sub("rep", "kh_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "kh_flu", colnames(data_wide))
colnames(data_wide) <- sub("base", "short", colnames(data_wide))
names(data_wide)

data_wide_KH <- data_wide


#### merge data and get sum scores ####

data_wide2 <- merge(data_wide_VS, data_wide_KH, by="vpcode_hd1", all=T)
data_wide2$vpcode_hd1 <- as.factor(data_wide2$vpcode_hd1)
data_wide2 <- data_wide2 %>% mutate_if(is.character, as.numeric)

data_wide2$vs_sum_syn1_s <- rowSums(data_wide2[grep("vs_flu.syn1.*", names(data_wide2))], na.rm=T)
data_wide2$vs_sum_syn2_s <- rowSums(data_wide2[grep("vs_flu.syn2.*", names(data_wide2))], na.rm=T)

data_wide2$kh_sum_syn1_s <- rowSums(data_wide2[grep("kh_flu.syn1.*", names(data_wide2))], na.rm=T)
data_wide2$kh_sum_syn2_s <- rowSums(data_wide2[grep("kh_flu.syn2.*", names(data_wide2))], na.rm=T)

names(data_wide2)

psych::ICC(data_wide2[, c("vs_sum_syn1_s", "kh_sum_syn1_s")])
psych::ICC(data_wide2[, c("vs_sum_syn2_s", "kh_sum_syn2_s")])

#### write data ####

#write wide data file
#write.csv2(data_wide2, paste0("../../../02_WideData/synonym-short_wide_", Sys.Date(), ".csv"), row.names = FALSE)


psych::describe(data_wide2$vs_sum_syn1_s)
psych::describe(data_wide2$kh_sum_syn1_s)
psych::describe(data_wide2$vs_sum_syn2_s)
psych::describe(data_wide2$kh_sum_syn2_s)


