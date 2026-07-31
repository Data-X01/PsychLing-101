dat=read.csv("original_data/Prekovicetal2016.csv",T)


dim(dat)
colnames(dat)


VLDlista = read.csv("VLD_stimuli_list.csv",F)
dat <- dat[dat$rec %in% VLDlista[[1]], ]
dim(dat)
head(dat)



dat$participant_id = dat$Subject
dat$trial_id = dat$Trial.name
dat$stimulus = dat$rec
dat$trial_order = dat$Trial.order
dat$lexicality = dat$leksikalnost
dat$letter_order = dat$FWD_BCW
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$RT


df <- dat[, c("participant_id", "trial_id", "stimulus",  "trial_order", "lexicality", "letter_order",  "response", "accuracy", "rt")]
dim(df)


write.csv(df, "processed_data/exp1.csv", row.names = FALSE)


