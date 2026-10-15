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

#### data JL (full sample)
data_long <-  read.csv2("things_base_short_JL_19-04-2022.csv", encoding="UTF-8") #JL data
data_long_snippet2 <-  read.csv2("../Gesamt/snippet2/things_base_short_ges_JL_full_03-06-2022_snippet2.csv", encoding="UTF-8") #JL data

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
things_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
things_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))
things_lat <- reshape(data_long, v.names="latency", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "response", "flu"))

names(things_flu)
names(things_rep)
names(things_lat)

things_rep$rep.instruct_TH1_base_s_NA <- NULL
things_rep$date <- NULL
things_rep$time <- NULL
things_rep$trialcode <- NULL
things_rep$subject <- NULL

things_flu$flu.instruct_TH1_base_s_NA <- NULL
things_flu$date <- NULL
things_flu$time <- NULL
things_flu$trialcode <- NULL
things_flu$subject <- NULL

things_lat$latency.instruct_TH1_base_s_NA <- NULL
things_lat$date <- NULL
things_lat$time <- NULL
things_lat$trialcode <- NULL
things_lat$rep <- NULL
things_lat$subject <- NULL

#merge flu and rep
data_wide <- merge(things_flu, things_rep, by="vpcode_hd1")
data_wide <- merge(data_wide, things_lat, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("TH", "th", colnames(data_wide))
colnames(data_wide) <- sub("latency", "lat", colnames(data_wide))
colnames(data_wide) <- sub("rep", "jl_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "jl_flu", colnames(data_wide))

names(data_wide)

data_wide_JL <- data_wide



#### load data #change folder once back in Ulm
data_long <-  read.csv2("things_base_short_VS_19-04-2022.csv", encoding="UTF-8") #JL data
data_long_snippet2 <-  read.csv2("../Gesamt/snippet2/things_base_short_ges_Vs_full_03-06-2022_snippet2.csv", encoding="UTF-8") #JL data

data_long <- rbind(data_long, data_long_snippet2)
rm(data_long_snippet2)

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
things_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
things_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))

names(things_flu)
names(things_rep)
names(things_lat)

things_rep$rep.instruct_TH1_base_s_NA <- NULL
things_rep$date <- NULL
things_rep$time <- NULL
things_rep$trialcode <- NULL
things_rep$subject <- NULL

things_flu$flu.instruct_TH1_base_s_NA <- NULL
things_flu$date <- NULL
things_flu$time <- NULL
things_flu$trialcode <- NULL
things_flu$subject <- NULL


#merge flu and rep
data_wide <- merge(things_flu, things_rep, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("TH", "th", colnames(data_wide))
colnames(data_wide) <- sub("rep", "vs_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "vs_flu", colnames(data_wide))

names(data_wide)

data_wide_VS <- data_wide



#### load data #change folder once back in Ulm
data_long <-  read.csv2("things_base_short_KH_19-04-2022.csv", encoding="UTF-8") #JL data

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
things_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
things_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))

names(things_flu)
names(things_rep)
names(things_lat)

things_rep$rep.instruct_TH1_base_s_NA <- NULL
things_rep$date <- NULL
things_rep$time <- NULL
things_rep$trialcode <- NULL
things_rep$subject <- NULL

things_flu$flu.instruct_TH1_base_s_NA <- NULL
things_flu$date <- NULL
things_flu$time <- NULL
things_flu$trialcode <- NULL
things_flu$subject <- NULL


#merge flu and rep
data_wide <- merge(things_flu, things_rep, by="vpcode_hd1")
names(data_wide)


#rename variables
colnames(data_wide) <- sub("TH", "th", colnames(data_wide))
colnames(data_wide) <- sub("rep", "kh_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "kh_flu", colnames(data_wide))

names(data_wide)

data_wide_KH <- data_wide


#### merge data and get sum scores ####

data_wide <- merge(data_wide_JL, data_wide_VS, by="vpcode_hd1", all=T)
data_wide2 <- merge(data_wide, data_wide_KH, by="vpcode_hd1", all=T)
data_wide2$vpcode_hd1 <- as.factor(data_wide2$vpcode_hd1)
data_wide2 <- data_wide2 %>% mutate_if(is.character, as.numeric)

data_wide2$vs_sum_th1_s <- rowSums(data_wide2[grep("vs_flu.th1.*", names(data_wide2))], na.rm=T)
data_wide2$vs_sum_th2_s <- rowSums(data_wide2[grep("vs_flu.th2.*", names(data_wide2))], na.rm=T)
data_wide2$vs_sum_th3_s <- rowSums(data_wide2[grep("vs_flu.th3.*", names(data_wide2))], na.rm=T)

data_wide2$jl_sum_th1_s <- rowSums(data_wide2[grep("jl_flu.th1.*", names(data_wide2))], na.rm=T)
data_wide2$jl_sum_th2_s <- rowSums(data_wide2[grep("jl_flu.th2.*", names(data_wide2))], na.rm=T)
data_wide2$jl_sum_th3_s <- rowSums(data_wide2[grep("jl_flu.th3.*", names(data_wide2))], na.rm=T)

data_wide2$kh_sum_th1_s <- rowSums(data_wide2[grep("kh_flu.th1.*", names(data_wide2))], na.rm=T)
data_wide2$kh_sum_th2_s <- rowSums(data_wide2[grep("kh_flu.th2.*", names(data_wide2))], na.rm=T)
data_wide2$kh_sum_th3_s <- rowSums(data_wide2[grep("kh_flu.th3.*", names(data_wide2))], na.rm=T)

names(data_wide2)

#### write data ####

#write wide data file
#write.csv2(data_wide2, paste0("../../../02_WideData/things-short_wide_", Sys.Date(), ".csv"), row.names = FALSE)

psych::ICC(data_wide2[, c("vs_sum_th1_s", "jl_sum_th1_s", "kh_sum_th1_s")])
psych::ICC(data_wide2[, c("vs_sum_th2_s", "jl_sum_th2_s", "kh_sum_th2_s")])
psych::ICC(data_wide2[, c("vs_sum_th3_s", "jl_sum_th3_s", "kh_sum_th3_s")])

psych::ICC(data_wide2[, c("vs_sum_th1_s", "jl_sum_th1_s")])
psych::ICC(data_wide2[, c("vs_sum_th2_s", "jl_sum_th2_s")])
psych::ICC(data_wide2[, c("vs_sum_th3_s", "jl_sum_th3_s")])





#### quick check of information #### 

#basic information 
#quick check, delete in ulm
data_wide <- data_wide2

data_wide <- data_wide %>% mutate_if(is.character, as.numeric)

data_wide$vs_sum_rep1 <- rowSums(data_wide[grep("vs_rep.th1.*", names(data_wide))], na.rm=T)
data_wide$jl_sum_rep1 <- rowSums(data_wide[grep("jl_rep.th1.*", names(data_wide))], na.rm=T)
data_wide$kh_sum_rep1 <- rowSums(data_wide[grep("kh_rep.th1.*", names(data_wide))], na.rm=T)
hist(data_wide$vs_sum_rep1)
hist(data_wide$kh_sum_rep1)
hist(data_wide$jl_sum_rep1)
psych::describe(data_wide$vs_sum_rep1)
psych::describe(data_wide$kh_sum_rep1)
psych::describe(data_wide$jl_sum_rep1)

data_wide$vs_sum_th1 <- rowSums(data_wide[grep("vs_flu.th1.*", names(data_wide))], na.rm=T)
data_wide$vs_sum_th2 <- rowSums(data_wide[grep("vs_flu.th2.*", names(data_wide))], na.rm=T)

data_wide$jl_sum_th1 <- rowSums(data_wide[grep("jl_flu.th1.*", names(data_wide))], na.rm=T)
data_wide$jl_sum_th2 <- rowSums(data_wide[grep("jl_flu.th2.*", names(data_wide))], na.rm=T)

data_wide$kh_sum_th1 <- rowSums(data_wide[grep("kh_flu.th1.*", names(data_wide))], na.rm=T)
data_wide$kh_sum_th2 <- rowSums(data_wide[grep("kh_flu.th2.*", names(data_wide))], na.rm=T)

hist(data_wide$vs_sum_th1)
hist(data_wide$vs_sum_th2)

hist(data_wide$jl_sum_th1)
hist(data_wide$jl_sum_th2)

hist(data_wide$kh_sum_th1)
hist(data_wide$kh_sum_th2)

library(psych)
psych::ICC(data_wide[, c("vs_sum_th1", "jl_sum_th1", "kh_sum_th1")])

psych::describe(things_flu$sum_th1)
psych::describe(things_flu$sum_th2)

plot(things_flu$sum_th1, things_flu$sum_th2)
cor(things_flu$sum_th1, things_flu$sum_th2, use="complete.obs")

sort(names(gc_resp))


