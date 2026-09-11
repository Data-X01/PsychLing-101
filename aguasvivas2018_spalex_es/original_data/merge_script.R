# Merge Script
# By José Aguasvivas
# Last update February 26, 2018
#
# This script will read the separate .csv files and combine the users, sessions and lexical
# files into a single table so that analyses can be run from there. Intermediate steps
# are also created and can be modified as needed.
#

rm(list = ls())
require_install <- function(x) {
  if (!require(x, character.only = TRUE)) {
    install.packages(x, dependencies = TRUE)
  }
}
require_install('rstudioapi')
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
#Read the correct encoding of files
options(encoding = 'utf-8')

lexical <-
  read.table(
    'lexical.csv',
    sep = ',',
    header = TRUE,
    fill = TRUE,
    na.strings = c("", "NA")
  )

users <-
  read.table(
    'users.csv',
    sep = ',',
    header = TRUE,
    fill = TRUE,
    na.strings = c("", "NA")
  )

sessions <-
  read.table(
    'sessions.csv',
    sep = ',',
    header = TRUE,
    fill = TRUE,
    na.strings = c("", "NA")
  )

word.info <-
  read.table(
    'word_info.csv',
    sep = ',',
    header = TRUE,
    fill = TRUE,
    na.strings = c("", "NA")
  )

users.sessions <- merge(sessions, users, by = 'profile_id', all = T)
users.sessions.lexical <-
  merge(users.sessions, lexical, by = 'exp_id', all = T)

data.table::fwrite(users.sessions.lexical, "merged.csv") 