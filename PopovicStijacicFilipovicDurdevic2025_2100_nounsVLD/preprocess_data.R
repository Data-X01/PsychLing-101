dat=read.csv("original_data/PopovicStijacicFilipovicDurdevic_2100nounsVLD.csv",T)

dim(dat)
colnames(dat)


dat$list = dat$title
dat$participant_id = dat$subject_nr
dat$trial_id = dat$trial_number
dat$stimulus = dat$rec
dat$trial_order = dat$count__mouse_response
dat$lexicality = dat$leksikalnost
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$response_time

df <- dat[, c("list", "participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
write.csv(df, "processed_data/exp1.csv", row.names = FALSE)



