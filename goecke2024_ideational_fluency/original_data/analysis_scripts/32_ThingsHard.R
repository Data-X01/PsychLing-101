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

#### data first scorer 
data_long <-  read.csv2("things_base_short_hard_az_full_03-06-2022.csv", encoding="UTF-8") #JL data


#### start recode routine  ####
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

things_rep$rep.instruct_TH1_base_hard_s_NA <- NULL
things_rep$date <- NULL
things_rep$time <- NULL
things_rep$trialcode <- NULL
things_rep$subject <- NULL

things_flu$flu.instruct_TH1_base_hard_s_NA <- NULL
things_flu$date <- NULL
things_flu$time <- NULL
things_flu$trialcode <- NULL
things_flu$subject <- NULL

#merge flu and rep
data_wide <- merge(things_flu, things_rep, by="vpcode_hd1")
names(data_wide)

#rename variables
colnames(data_wide) <- sub("TH", "th", colnames(data_wide))
colnames(data_wide) <- sub("rep", "az_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "az_flu", colnames(data_wide))
colnames(data_wide) <- sub("_s", "", colnames(data_wide))


names(data_wide)

data_wide_AZ <- data_wide



#### scorer 2 AR
data_long <-  read.csv2("things_base_short_hard_AR_full_03-06-2022.csv", encoding="UTF-8") #JL data

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

data_long_plot <- data_long

#get wide format
things_flu <- reshape(data_long, v.names="flu", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "rep"))
things_rep <- reshape(data_long, v.names="rep", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "latency", "response", "flu"))
things_lat <- reshape(data_long, v.names="latency", timevar="trial_new", idvar=c("vpcode_hd1"), direction="wide", drop=c("trialnum", "blockcode", "blocknum", "stimulus1", "response", "flu"))

names(things_flu)
names(things_rep)
names(things_lat)

things_rep$rep.instruct_TH1_base_hard_s_NA <- NULL
things_rep$date <- NULL
things_rep$time <- NULL
things_rep$trialcode <- NULL
things_rep$subject <- NULL

things_flu$flu.instruct_TH1_base_hard_s_NA <- NULL
things_flu$date <- NULL
things_flu$time <- NULL
things_flu$trialcode <- NULL
things_flu$subject <- NULL

things_lat$latency.instruct_TH1_base_hard_s_NA <- NULL
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
colnames(data_wide) <- sub("rep", "ar_rep", colnames(data_wide))
colnames(data_wide) <- sub("flu", "ar_flu", colnames(data_wide))
colnames(data_wide) <- sub("latency", "lat", colnames(data_wide))
colnames(data_wide) <- sub("_s", "", colnames(data_wide))

names(data_wide)

data_wide_AR <- data_wide




#### merge data and get sum scores ####

data_wide <- merge(data_wide_AZ, data_wide_AR, by="vpcode_hd1", all=T)
data_wide$vpcode_hd1 <- as.factor(data_wide$vpcode_hd1)
data_wide <- data_wide %>% mutate_if(is.character, as.numeric)

data_wide$az_sum_th1_h <- rowSums(data_wide[grep("az_flu.th1.*", names(data_wide))], na.rm=T)
data_wide$az_sum_th2_h <- rowSums(data_wide[grep("az_flu.th2.*", names(data_wide))], na.rm=T)

data_wide$ar_sum_th1_h <- rowSums(data_wide[grep("ar_flu.th1.*", names(data_wide))], na.rm=T)
data_wide$ar_sum_th2_h <- rowSums(data_wide[grep("ar_flu.th2.*", names(data_wide))], na.rm=T)
hist(data_wide$ar_sum_th1_h)
hist(data_wide$ar_sum_th2_h)
cor(data_wide$ar_sum_th1_h, data_wide$ar_sum_th2_h, use="complete.obs")
pairs.panels(cbind(data_wide$ar_sum_th1_h, data_wide$ar_sum_th2_h))

names(data_wide)

#### write data ####

#write wide data file
#write.csv2(data_wide, paste0("../../../02_WideData/things-hard_wide_", Sys.Date(), ".csv"), row.names = FALSE)

psych::ICC(data_wide[, c("az_sum_th1_h", "ar_sum_th1_h")])
psych::ICC(data_wide[, c("az_sum_th2_h", "ar_sum_th2_h")])






#### quick check of information #### 

#basic information 
data_wide$mrt_th1_h <- rowMeans(data_wide[grep("lat.th1.*", names(data_wide))], na.rm=T)
pairs.panels(cbind(data_wide$ar_sum_th1_h, data_wide$mrt_th1_h))

####
data <- data_long_plot %>%
  filter(blockcode == "TH1_base_hard_s") %>%
  mutate(latency = latency/1000) %>%
  group_by(trialnum) %>%
  summarise(mean_lat = mean(latency))
ggplot(data, aes(x = trialnum, y = mean_lat)) +
  geom_line()


data <- data_long_plot %>%
  filter(blockcode == "TH1_base_l") %>%
  mutate(latency = latency/1000)
ggplot(data, aes(x = trialnum, y = latency, group = vpcode_hd1)) +
  geom_line()

