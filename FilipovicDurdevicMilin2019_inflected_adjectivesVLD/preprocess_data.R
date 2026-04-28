dat=read.table("original_data/FilipovicDurdevicMilin2019.dat",T)

dim(dat)
colnames(dat)


dat$list = dat$exp_title
dat$participant_id = dat$naziv_fajla
dat$trial_id = dat$trial_number
dat$stimulus = dat$rec
dat$trial_order = dat$count_exp_sequence
dat$lexicality = dat$leksikalnost
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$response_time

df <- dat[, c("list", "participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
write.csv(df, "processed_data/FilipovicDurdevicMilin2019_clean.csv", row.names = FALSE)



