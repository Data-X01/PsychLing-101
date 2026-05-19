dat1=read.csv("original_data/Prekovicetal2016.csv",T)

dim(dat1)
colnames(dat1)


#dat1$list = dat1$Block_name
dat1$participant_id = dat1$Subject
dat1$trial_id = dat1$Trial.name
dat1$stimulus = dat1$rec
dat1$trial_order = dat1$Trial.order
dat1$lexicality = dat1$leksikalnost
dat1$response = dat1$response
dat1$accuracy = dat1$correct
dat1$rt = dat1$RT


df1 <- dat1[, c("participant_id", "trial_id", "stimulus",  "trial_order", "lexicality", "response", "accuracy", "rt")]
dim(df1)


write.csv(df1, "processed_data/exp1.csv", row.names = FALSE)


