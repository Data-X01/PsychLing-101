dat1=read.csv("original_data/FilipovicDurdevicFeldman2024_bialphabeticVLD_block1.csv",T)

dim(dat1)
colnames(dat1)

dat1$phase_id <- dat1$phase
dat1$list = dat1$title
dat1$participant_id = dat1$ima_fajla_sa_podacima
dat1$trial_id = dat1$item_id
dat1$stimulus = dat1$rec
dat1$trial_order = dat1$count_new_mouse_response
dat1$target_alphabet = dat1$alphabet
dat1$phonological_ambiguity = dat1$ambiguity
dat1$lexicality = dat1$Lexicality
dat1$response = dat1$response
dat1$accuracy = dat1$correct
dat1$rt = dat1$response_time

block1 <- dat1[, c("phase_id", "list", "participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "target_alphabet",  "phonological_ambiguity", "response", "accuracy", "rt")]


dat2=read.csv("original_data/FilipovicDurdevicFeldman2024_bialphabeticVLD_block2.csv",T)

dim(dat2)
colnames(dat2)

dat2$phase_id <- dat2$phase
dat2$list = dat2$title
dat2$participant_id = dat2$ima_fajla_sa_podacima
dat2$trial_id = dat2$item_code
dat2$stimulus = dat2$rec
dat2$trial_order = dat2$count_new_mouse_response
dat2$target_alphabet = dat2$alphabet
dat2$phonological_ambiguity = dat2$ambiguity
dat2$lexicality = dat2$lexicality
dat2$response = dat2$response
dat2$accuracy = dat2$correct
dat2$rt = dat2$response_time

block2 <- dat2[, c("phase_id", "list", "participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "target_alphabet",  "phonological_ambiguity", "response", "accuracy", "rt")]

block1_block2 = rbind(block1, block2)
write.csv(block1_block2, "processed_data/exp1.csv", row.names = FALSE)

