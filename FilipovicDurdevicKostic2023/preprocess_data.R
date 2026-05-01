dat1=read.csv("original_data/matrica.round1x.csv",T)

dim(dat1)
colnames(dat1)


#dat1$list = dat1$Block_name
dat1$participant_id = dat1$subject_code
dat1$trial_id = dat1$trial_number
dat1$stimulus = dat1$rec
dat1$trial_order = dat1$Trial_order
dat1$lexicality = dat1$leksikalnost
dat1$response = dat1$Response
dat1$accuracy = dat1$correct
dat1$rt = dat1$Reaction_time


df1 <- dat1[, c("participant_id", "trial_id", "stimulus",  "trial_order", "lexicality", "response", "accuracy", "rt")]
dim(df1)

###
dat2=read.csv("original_data/matrica.round2ax.csv",T)

dim(dat2)
colnames(dat2)


#dat2$list = dat2$exp_title
dat2$participant_id = dat2$Subject.number
dat2$trial_id = dat2$trial_number
dat2$stimulus = dat2$rec
dat2$trial_order = dat2$Trial.order
dat2$lexicality = dat2$leksikalnost
dat2$response = dat2$Response
dat2$accuracy = dat2$ErrorCode
dat2$rt = dat2$RT

df2 <- dat2[, c("participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
dim(df2)

###
dat3=read.csv("original_data/matrica.round3x.csv",T)

dim(dat3)
colnames(dat3)


#dat3$list = dat3$exp_title
dat3$participant_id = dat3$subject_code
dat3$trial_id = dat3$trial_number
dat3$stimulus = dat3$rec
dat3$trial_order = dat3$Trial_order
dat3$lexicality = dat3$leksikalnost
dat3$response = dat3$response
dat3$accuracy = dat3$correct
dat3$rt = dat3$response_time

df3 <- dat3[, c("participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
dim(df3)


###
dat4=read.csv("original_data/matrica.round4x.csv",T)

dim(dat4)
colnames(dat4)


#dat4$list = dat4$exp_title
dat4$participant_id = dat4$subject_code
dat4$trial_id = dat4$trial_number
dat4$stimulus = dat4$rec
dat4$trial_order = dat4$Trial_order
dat4$lexicality = dat4$leksikalnost
dat4$response = dat4$response
dat4$accuracy = dat4$correct
dat4$rt = dat4$response_time

df4 <- dat4[, c("participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
dim(df4)

dim(df1) + dim(df2) + dim(df3) + dim(df4)


###

df1234 = rbind(df1, df2, df3, df4)
dim(df1234)

df1234$participant_id = as.character(df1234$participant_id)
df1234$trial_id = as.character(df1234$trial_id)
df1234$stimulus = as.character(df1234$stimulus)
df1234$trial_order = as.character(df1234$trial_order)
df1234$lexicality = as.character(df1234$lexicality)
df1234$response = as.character(df1234$response)
df1234$accuracy = as.character(df1234$accuracy)
df1234$rt = as.character(df1234$rt)

write.csv(df1234, "processed_data/exp1.csv", row.names = FALSE)


