dat=read.csv("original_data/PopovicStijacicFilipovicDurdevic_2100nounsVLD.csv",T)

dim(dat)
colnames(dat)


library(dplyr)
# library(lubridate)
# 
# # Parse mixed-format datetime strings
# dat <- dat %>%
#   mutate(datetime = parse_date_time(
#     datetime,
#     orders = c("mdy HMS", "a b d HMS Y")
#   ))
# 
# # Check for parsing failures before proceeding
# sum(is.na(dat$datetime))          # how many failed to parse
# dat %>% filter(is.na(datetime))   # inspect which rows failed, if any
# 
# # Create session rank per participant, based on datetime
# dat <- dat %>%
#   group_by(subject_nr) %>%
#   mutate(session_number = dense_rank(datetime)) %>%
#   ungroup()
# 
# # create single per-participant trial order based on session order and trial order
# dat <- dat %>%
#   arrange(subject_nr, session_number, count__mouse_response) %>%
#   group_by(subject_nr) %>%
#   mutate(count__mouse_response_single = row_number()) %>%
#   ungroup()


dat$count__mouse_response_corrected = as.numeric(dat$count__mouse_response) + 1


dat$list = dat$title
dat$participant_id = dat$subject_nr
dat$trial_id = dat$trial_number
dat$stimulus = dat$rec
dat$trial_order = dat$count__mouse_response_corrected
dat$lexicality = dat$leksikalnost
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$response_time

df <- dat[, c("list", "participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
write.csv(df, "processed_data/exp1.csv", row.names = FALSE)



