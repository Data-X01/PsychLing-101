rm(list = ls())

#install.packages("tidyverse")  
#install.packages("textutils")
#install.packages("reshape2")

library(tidyverse)  
library(textutils)
library(reshape2)

###############################################
##### Preprocessing data for experiment 1 #####
###############################################

### set the folder 
setwd("C:/Users/tscha/PsychLing-101/guenther2026_crosslingcommunication")

### list all the .csv files in the data folder
folder <- "original_data"

# only the production data
files <- unique(dir(folder)[grep(dir(folder), pattern = ".csv$")])
files <- files[grep(files, pattern = "production")]

# empty data frame
dat <- NULL

for (f in files) {
  # read an individual file
  sdat <- read.csv(paste(folder, "/", f, sep = ""))
  
  # participant ID is just the file name
  sdat$participant <- f
  
  
  # get the completion time
  sdat$completion_time <-
    round(sdat[nrow(sdat), "time_elapsed"] / (60 * 1000), 2)
  
  ### get the demographic data (assuming it's the only line containing the string "gender")
  demo  <- sdat[grep(sdat$response, pattern = '\\{"gender'), "response"]
  demo2 <- sdat[grep(sdat$response, pattern = '\\{"previous'), "response"]
  
  sdat$gender      <-
    tolower(gsub(
      gsub(demo, pattern = ".*gender\":\"", replacement = ""),
      pattern = "\",.*",
      replacement = ""
    ))
  
  # extract age
  sdat$age         <-
    as.integer(gsub(
      gsub(demo, pattern = ".*\"age\":\"", replacement = ""),
      pattern = "\",.*",
      replacement = ""
    ))
  
  # extract language
  sdat$language    <-
    tolower(gsub(
      gsub(demo, pattern = ".*language\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  
  # extract other languages
  sdat$other_lang    <-
    tolower(gsub(
      gsub(demo, pattern = ".*other_lang\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  
  # extract which other languages
  sdat$which_other    <-
    tolower(gsub(
      gsub(demo, pattern = ".*which_other_lang\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  
  # extract previous experience
  sdat$previous_experience    <-
    tolower(gsub(
      gsub(demo2, pattern = ".*previous_experience\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  
  # extract response method
  sdat$response_method    <-
    tolower(gsub(
      gsub(demo2, pattern = ".*response_method\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  
  # keep only actual experimental data
  
  sdat <- sdat[sdat$word != "", ]
  
  # extract responses and basic cleaning
  sdat$response1    <-
    tolower(gsub(
      gsub(sdat$response, pattern = ".*response1\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  sdat$response2    <-
    tolower(gsub(
      gsub(sdat$response, pattern = ".*response2\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  sdat$response3   <-
    tolower(gsub(
      gsub(sdat$response, pattern = ".*response3\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  sdat <- sdat[, names(sdat) != "response"]
  
  sdat <- melt(
    sdat,
    measure.vars = c("response1", "response2", "response3"),
    value.name = "response",
    variable.name = "response_order"
  )
  sdat <- sdat[order(sdat$trial_index, sdat$response_order), ]
  
  
  # keep only interesting columns
  
  sdat <- sdat[, c(
    "word",
    "response",
    "response_order",
    "rt",
    "trial_index",
    "participant",
    "completion_time",
    "gender",
    "age",
    "language",
    "other_lang",
    "which_other",
    "previous_experience",
    "response_method"
  )]
  
  # info about version
  
  sdat$version <- 1
  if ("aeroporto" %in% sdat$word) {
    sdat$version <- 0
  }
  
  #
  dat <- bind_rows(dat, sdat)
}


### number of participants (initial)
length(table(dat$participant))

### tolower responses
dat$response <- tolower(dat$response)


### exclude German-speaking participants
table(dat$which_other)
dat2 <- dat[!grepl(dat$which_other, pattern = "tedesc"), ]
table(dat2$which_other)

## exclude participants with missing demographic info
dat2 <- dat2[!is.na(dat2$age), ]
dat2 <- dat2[!is.na(dat2$gender), ]
dat2 <- dat2[!is.na(dat2$language), ]


## completion time
mean(dat$completion_time)
median(dat$completion_time)


table(dat2$word) / 3
length(unique(dat2$participant))

### Import original words
translations <- read.table("resources/items_Italian_German.txt", header = T)
translations <- translations[, c("it", "de")]
names(translations) <- c("word", "translation")
dat2 <- merge(dat2, translations)


### exclusion based on open responses at the end of the experiment
participants.out <- unique(
  c(
    "itde_production_803184.csv",
    "itde_production_135443.csv",
    "itde_production_264771.csv",
    "itde_production_293400.csv",
    "itde_production_322150.csv",
    "itde_production_365106.csv",
    "itde_production_447499.csv",
    "itde_production_509559.csv",
    "itde_production_529539.csv",
    "itde_production_639301.csv",
    "itde_production_717989.csv",
    "itde_production_757568.csv",
    "itde_production_803184.csv",
    "itde_production_822834.csv",
    "itde_production_823319.csv",
    "itde_production_902983.csv",
    "itde_production_929817.csv",
    "itde_production_945365.csv",
    "itde_production_560533.csv",
    "itde_production_533249.csv",
    "itde_production_333916.csv",
    "itde_production_750782.csv",
    "itde_production_770388.csv",
    "itde_production_550028.csv",
    "itde_production_652860.csv",
    "itde_production_809330.csv",
    "itde_production_994381.csv"
  )
)
dat_new <- dat2[!dat2$participant %in% participants.out, ]

length(unique(dat_new$participant))
table(dat_new$version) / 36

table(dat_new$word)


## exclude target items embedded in the response
dat_new$embedded <- FALSE
for (i in 1:nrow(dat_new)) {
  dat_new[i, "embedded"] <- grepl(dat_new[i, "word"], dat_new[i, "response"])
}
dat_new <- dat_new[!dat_new$embedded, ]


## exclude Italian word responses
italist <- read.csv2("resources/subtlex_it.csv", fileEncoding = "Latin1")
italist <- italist[order(italist$FREQcount, decreasing = TRUE), ]
italist <- italist[1:50000, ]
italist <- tolower(italist$Word)

unique(dat_new$response[dat_new$response %in% italist])


dat_new <- dat_new[!(dat_new$response %in% italist), ]

# remove another non-compliant participant
non_compl <- "itde_production_113612.csv"
dat_new <- dat_new[!(dat_new$participant %in% non_compl), ]

#########################################
##### Data cleaning and translating #####
#########################################

# Columns to keep
cols_to_keep <- c("participant", "word", "response", "trial_index", "response_order", "rt", "age", "gender", "other_lang")

# Select only those columns
df_selected <- dat2 %>%
  select(all_of(cols_to_keep))

# Adjust the participant id
df_selected <- df_selected %>%
  mutate(participant = participant %>%
           str_remove("^itde_production_") %>%
           str_remove(".csv$"))
df_selected <- df_selected %>%
  rename(participant_id = participant)

# Translate gender to English and clean
df_selected %>% distinct(gender)
df_selected <- df_selected %>%
  mutate(gender = gender %>%
           str_trim() %>%
           str_to_lower(),
         gender = recode(gender,
                         "femmina" = "female",
                         "donna" = "female",
                         "f" = "female",
                         "femminile" = "female",
                         "maschio" = "male",
                         "m" = "male",
                         "maschile" = "male",
                         .default = NA_character_))

# Translate and clean other languages column
df_selected %>% distinct(other_lang)

valid_langs <- c("albanese",
                 "bergamasco",
                 "francese",
                 "greco",
                 "inglese",
                 "latino",
                 "russo",
                 "spagnolo")

df_selected <- df_selected %>%
  mutate(other_lang = other_lang %>%
           str_to_lower() %>%
           str_squish() %>%
           str_replace_all("\\bno\\b", "none") %>%
           str_replace_all("\\bnessuna\\b", "none") %>%
           str_replace_all("\\s+e\\s+", ", ") %>%
           str_replace_all("\\ba livello scolastico\\b", "") %>%
           str_replace_all("\\bun po['’]? di\\b", "") %>%
           str_replace_all("\\bqualcosa di\\b", "") %>%
           str_replace_all("\\bmolto bene\\b", "") %>%
           str_replace("^inglese francese$", "inglese, francese") %>%
           str_replace_all("\\s*,\\s*", ", ") %>%
           str_replace_all("^,\\s*|,\\s*$", "") %>%
           str_split(",\\s*")) %>%
  mutate(other_lang = map_chr(other_lang, \(x) {
    x <- x %>%
      str_trim() %>%
      discard(~ .x == "")
    
    if (length(x) == 0 || all(x %in% "none")) {
      return("none")}
    
    langs <- x %>%
      discard(~ .x == "none") %>%
      keep(~ .x %in% valid_langs) %>%
      unique() %>%
      sort()
    
    if (length(langs) == 0) {"none"}
    else {str_c(langs, collapse = ", ")}}))

df_selected <- df_selected %>%
  mutate(other_lang = str_replace_all(other_lang, c(
    "albanese" = "albanian",
    "bergamasco" = "bergamasque",
    "francese" = "french",
    "greco" = "greek",
    "inglese" = "english",
    "latino" = "latin",
    "russo" = "russian",
    "spagnolo" = "spanish")),
    other_lang = other_lang %>%
      str_split(",\\s*") %>%
      map(~ sort(.x)) %>%
      map_chr(~ str_c(.x, collapse = ", ")))

df_selected <- df_selected %>% rename(other_languages = other_lang)

# Rename trial_index and make it 0-indexed
df_selected <- df_selected %>%
  rename(trial_order = trial_index)

df_selected$trial_order <- df_selected$trial_order - 5

# Save preprocessed data as .csv
write_csv2(df_selected, "processed_data/exp1.csv")




################################################
##### Preprocessing data for experiment 2 ######
################################################

# Clear global workspace (important)
rm(list = ls())

### list all the .csv files in the folder
folder <- "original_data"

files <- unique(dir(folder)[grep(dir(folder), pattern = ".csv$")])
files <- files[grep(files,pattern="reception")]

# empty data frame
dat <- NULL


for (f in files) {
  # read an individual file
  sdat <- read.csv(paste(folder,"/",f,sep=""),encoding = "UTF-8")
  
  # participant ID is just the file name
  sdat$participant <- f
  
  
  # get the completion time
  sdat$completion_time <-
    round(sdat[nrow(sdat), "time_elapsed"] / (60 * 1000), 2)
  
  ### get the demographic data (assuming it's the only line containing the string "gender")
  demo  <- sdat[grep(sdat$response, pattern = '\\{"gender'), "response"]
  demo2 <- sdat[grep(sdat$response, pattern = '\\{"previous'), "response"]
  demo3 <- sdat[grep(sdat$response, pattern = '\\{"guess_native'), "response"]
  
  sdat$gender      <-
    tolower(gsub(
      gsub(demo, pattern = ".*gender\":\"", replacement = ""),
      pattern = "\",.*",
      replacement = ""
    ))
  
  # extract age
  sdat$age         <-
    as.integer(gsub(
      gsub(demo, pattern = ".*\"age\":\"", replacement = ""),
      pattern = "\",.*",
      replacement = ""
    ))
  
  # extract language
  sdat$language    <-
    tolower(gsub(
      gsub(demo, pattern = ".*language\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    ))
  
  # extract other languages
  sdat$other_lang    <-
    tolower(gsub(
      gsub(demo, pattern = ".*other_lang\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    )) 
  
  # extract which other languages
  sdat$which_other    <-
    tolower(gsub(
      gsub(demo, pattern = ".*which_other_lang\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    )) 
  
  # guess about original language
  sdat$guess_native    <-
    tolower(gsub(
      gsub(demo3, pattern = ".*guess_native\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    )) 
  
  # save the rating scores and responses
  scores <- sdat[sdat$trial_type=="html-slider-response",]
  scores <- scores[,c("target","response")]
  names(scores)[names(scores) == "response"] <- "rating"
  sdat <-   sdat[sdat$trial_type!="html-slider-response",]
  sdat <- sdat[sdat$target != "",]
  
  # extract responses and basic cleaning
  sdat$response1    <-
    tolower(gsub(
      gsub(sdat$response, pattern = ".*response1\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    )) 
  sdat$response2    <-
    tolower(gsub(
      gsub(sdat$response, pattern = ".*response2\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    )) 
  sdat$response3   <-
    tolower(gsub(
      gsub(sdat$response, pattern = ".*response3\":\"", replacement = ""),
      pattern = "\".*",
      replacement = ""
    )) 
  sdat <- sdat[,names(sdat) != "response"]
  
  
  
  sdat <- melt(sdat,measure.vars = c("response1","response2","response3"),value.name = "response",variable.name = "response_order")
  sdat <- sdat[order(sdat$trial_index,sdat$response_order),]
  
  
  # keep only interesting columns
  
  sdat <- sdat[,c("target","original_word","original_translation","response","response_order","rt","trial_index","participant","ID","completion_time",
                  "gender","age","language","other_lang","which_other","guess_native")]
  sdat <- merge(sdat,scores)
  dat <- bind_rows(dat, sdat)
}

length(table(dat$participant))

table(dat$which_other)

### tolower responses
dat$response <- tolower(dat$response)

# tolower original translation
dat$original_translation <- tolower(dat$original_translation)


### check native language
table(dat$language)

### exclude Italian-speaking participants
dat2 <- dat[!grepl(dat$which_other,pattern="ital"),]
table(dat2$which_other)

## manual removal of non-German words
out <- unlist(read.table("resources/non_German_words.txt"))
dat2 <- dat2[!(dat2$response %in% out),]

#########################################
##### Data cleaning and translating #####
#########################################

cols_to_keep <- c("participant", "target", "response", "trial_index", "response_order", "rt", "gender", "age", "other_lang")

# Select only those columns
df_selected <- dat2 %>%
  select(all_of(cols_to_keep))

# Adjust the participant id
df_selected <- df_selected %>%
  mutate(participant = participant %>%
           str_remove("^itde_reception_") %>%
           str_remove(".csv$"))
df_selected <- df_selected %>%
  rename(participant_id = participant)

# Translate gender to English and clean
df_selected %>% distinct(gender)
df_selected <- df_selected %>%
  mutate(gender = gender %>%
           str_trim() %>%
           str_to_lower(),
         gender = recode(gender,
                         "nicht-binär" = "non-binary",
                         "non-binär" = "non-binary",
                         "männlich" = "male",
                         "w" = "female",
                         "weiblich" = "female",
                         "weiblichg" = "female",
                         "queer" = "genderqueer",
                         "m" = "male",
                         "mann" = "male",
                         .default = NA_character_))

# Translate and clean other languages column
valid_langs_de <- c("arabisch",
                    "dänisch",
                    "dgs",
                    "englisch",
                    "finnisch",
                    "französisch",
                    "indonesisch",
                    "japanisch",
                    "koreanisch",
                    "latein",
                    "mandarin",
                    "niederländisch",
                    "norwegisch",
                    "polnisch",
                    "russisch",
                    "schwedisch",
                    "spanisch",
                    "türkisch")

df_selected <- df_selected %>%
  mutate(other_lang = other_lang %>%
           str_to_lower() %>%
           str_squish() %>%
           str_replace_all("\\bnein\\b", "none") %>%
           str_replace_all("\\(([^)]*)\\)", "\\1") %>%
           str_replace_all("\\betwas\\s+", "") %>%
           str_replace_all("\\bfranzoesisch\\b", "französisch") %>%
           str_replace_all("\\bniederlaendisch\\b", "niederländisch") %>%
           str_replace_all("\\bspanish\\b", "spanisch") %>%
           str_replace("^englisch französisch$", "englisch, französisch") %>%
           str_replace_all("\\s*,\\s*", ", ") %>%
           str_replace_all("^,\\s*|,\\s*$", "") %>%
           str_split(",\\s*")) %>%
  mutate(other_lang = map_chr(other_lang, \(x) {x <- x %>%
    str_trim() %>%
    discard(~ .x == "")
  
  if (length(x) == 0 || all(x %in% "none")) {
    return("none")}
  
  langs <- x %>%
    discard(~ .x == "none") %>%
    keep(~ .x %in% valid_langs_de) %>%
    unique() %>%
    sort()
  
  if (length(langs) == 0) {"none"} else {str_c(langs, collapse = ", ")}}))

df_selected <- df_selected %>%
  mutate(other_lang = str_replace_all(other_lang, c("arabisch" = "arabic",
                                                    "dgs" = "german sign language",
                                                    "dänisch" = "danish",
                                                    "englisch" = "english",
                                                    "finnisch" = "finnish",
                                                    "französisch" = "french",
                                                    "indonesisch" = "indonesian",
                                                    "japanisch" = "japanese",
                                                    "koreanisch" = "korean",
                                                    "latein" = "latin",
                                                    "mandarin" = "mandarin",
                                                    "niederländisch" = "dutch",
                                                    "norwegisch" = "norwegian",
                                                    "polnisch" = "polish",
                                                    "russisch" = "russian",
                                                    "schwedisch" = "swedish",
                                                    "spanisch" = "spanish",
                                                    "türkisch" = "turkish")),
         other_lang = other_lang %>%
           str_split(",\\s*") %>%
           map(~ sort(.x)) %>%
           map_chr(~ str_c(.x, collapse = ", ")))

df_selected <- df_selected %>% rename(other_languages = other_lang)

# Rename "trial_index" and make it 0-indexed
df_selected <- df_selected %>%
  rename(trial_order = trial_index)

df_selected$trial_order <- (df_selected$trial_order / 2) - 2

# Rename "target" to "word"
df_selected <- df_selected %>% rename(word = target)

### Export
write_csv2(df_selected, "processed_data/exp2.csv")