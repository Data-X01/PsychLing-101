################################################################################
#
#                      Generate Prompts - PsychLing101
#
################################################################################

#Exp1
library(readr)
E1 <- read_csv("processed_data/exp1.csv")
E1[E1$accuracy=="Incorrect", "accuracy"] <- "Incorretto"
E1[E1$accuracy=="Correct", "accuracy"] <- "Corretto"

#initialize
text <- rep(NA, length(unique(E1$participant_id)))
experiment <- rep(NA, length(unique(E1$participant_id)))
participant_id <- rep(NA, length(unique(E1$participant_id)))

D <- data.frame(text, experiment, participant_id)


#loop 
for (id in unique(E1$participant_id)){
print(id)
this_participant <- E1[E1$participant_id==id,]
opts<- sample(letters, 2, replace = FALSE)

text <-  paste("Grazie per aver scelto di partecipare a questo studio. In ogni round di questo compito vedrai comparire sullo schermo in alto una parola scritta in minuscolo. Nella parte bassa dello schermo vedrai scritte in MAIUSCOLO due nuove parole, cioè due parole che non esistono. Una di queste nuove parole è un sinonimo della parola scritta in alto. L'altra è una nuova parola che non c'entra. La nuova parola che è un sinonimo della parola in alto è più simile in significato alla parola in minuscolo rispetto all'altra nuova parola. In ogni round ti chiediamo d'indicare quale delle due nuove parole in MAIUSCOLO è più vicina in significato alla parola scritta in minuscolo. In altri termini, dovrai indicare quale tra le due nuove parole in MAIUSCOLO è un sinonimo della parola scritta in minuscolo. Per rispondere, premi i tasti", opts[1], "o", opts[2], "sulla tastiera. Cerca di rispondere più accuratamente che puoi. Non preoccuparti se ti sembra difficile. concentrati sul significato delle parole e dai la risposta che ti sembra più corretta.") 

for (i in 1:(dim(this_participant)[1])){

this_response <- paste("<<", opts[this_participant$response[i]], ">>", sep="")
P<- paste("La parola", this_participant$stimulus[i], "appare sullo schermo . L'opzione associata al tasto ", opts[1], "è", this_participant$response_option_1[i], ". L'opzione associata al tasto", opts[2], "è", this_participant$response_option_2[i], ". Tu premi ", this_response, ".", this_participant$accuracy[i] ,".")
text <- paste(text, P)
}
D$text[id] <- text
D$participant_id[id] <- (unique(E1$participant_id)[id])
}
D$experiment <- "bonandrini2026_SPChumaneval_Exp1"
D1 <- D

rm(list = setdiff(ls(), "D1")) #clean and keep only final
################################################################################
#Exp2
library(readr)
E2 <- read_csv("processed_data/exp2.csv")
E2[E2$accuracy=="Incorrect", "accuracy"] <- "Incorretto"
E2[E2$accuracy=="Correct", "accuracy"] <- "Corretto"

#initialize
text <- rep(NA, length(unique(E2$participant_id)))
experiment <- rep(NA, length(unique(E2$participant_id)))
participant_id <- rep(NA, length(unique(E2$participant_id)))

D <- data.frame(text, experiment, participant_id)


#loop 
for (id in unique(E2$participant_id)){
  print(id)
  this_participant <- E2[E2$participant_id==id,]
  opts<- sample(letters, 2, replace = FALSE)
  
text <- paste("Grazie per aver scelto di partecipare a questo studio. In ogni round di questo compito vedrai comparire sullo schermo in alto IN MAIUSCOLO una nuova parola, cioè una parola che non esiste. Questa nuova parola deriva dal significato di due parole esistenti. Nella parte bassa dello schermo vedrai scritte in minuscolo due coppie di parole: una coppia di parole è quella usata per generare la nuova parola. L'altra è una coppia di parole che non c'entra. La coppia di parole usata per generare la nuova parola è più simile in significato alla parola in MAIUSCOLO rispetto all'altra coppia. Premi il tasto 1 sulla tastiera per procedere. In ogni round ti chiediamo d'indicare quale delle due coppie di parole in minuscolo è più vicina in significato alla nuova parola scritta in MAISUCOLO. In altri termini, dovrai indicare quale tra le due coppie di parole in minuscolo è stata usata per generare la nuova parola scritta in MAIUSCOLO.Per rispondere, premi i tasti" , opts[1], "o", opts[2], "sulla tastiera. Cerca di rispondere più accuratamente che puoi. Non preoccuparti se ti sembra difficile. concentrati sul significato delle parole e dai la risposta che ti sembra più corretta.")

for (i in 1:(dim(this_participant)[1])){
  
  this_response <- paste("<<", opts[this_participant$response[i]], ">>", sep="")
  P<- paste("La parola", this_participant$stimulus[i], "appare sullo schermo . L'opzione associata al tasto ", opts[1], "è", this_participant$response_option_1[i], ". L'opzione associata al tasto", opts[2], "è", this_participant$response_option_2[i], ". Tu premi ", this_response, ".", this_participant$accuracy[i] ,".")
  text <- paste(text, P)
}
D$text[id] <- text
D$participant_id[id] <- (unique(E2$participant_id)[id])
}
D$experiment <- "bonandrini2026_SPChumaneval_Exp2"
D2 <- D
rm(list = setdiff(ls(), c("D1","D2"))) #clean and keep only final

################################################################################
#Exp3
library(readr)
E3 <- read_csv("processed_data/exp3.csv")
E3[E3$accuracy=="Incorrect", "accuracy"] <- "Incorretto"
E3[E3$accuracy=="Correct", "accuracy"] <- "Corretto"

#initialize
text <- rep(NA, length(unique(E3$participant_id)))
experiment <- rep(NA, length(unique(E3$participant_id)))
participant_id <- rep(NA, length(unique(E3$participant_id)))

D <- data.frame(text, experiment, participant_id)


#loop 
for (id in unique(E3$participant_id)){
  print(id)
  this_participant <- E3[E3$participant_id==id,]
  opts<- sample(letters, 2, replace = FALSE)
  
text <- paste("Grazie per aver scelto di partecipare a questo studio. Premi il tasto 1 sulla tastiera per procedere. In ogni round di questo compito vedrai comparire sullo schermo in alto una coppia di parole scritte in minuscolo. Nella parte bassa dello schermo vedrai scritte in MAIUSCOLO due nuove parole, cioè due parole che non esistono. Una di queste nuove parole è stata generata dal significato della coppia di parole scritte in alto. L'altra è una nuova parola che non c'entra. La nuova parola che è stata generata dalla coppia di parole in alto è più simile in significato alla coppia di parole in minuscolo rispetto all'altra nuova parola. In ogni round ti chiediamo d'indicare quale delle due nuove parole in MAIUSCOLO è più vicina in significato alla coppia di parole scritta in minuscolo. In altri termini, dovrai indicare quale tra le due nuove parole in MAIUSCOLO è stata generata dalla coppia di parole scritte in minuscolo. Per rispondere, premi i tasti" , opts[1], "o", opts[2], "sulla tastiera. Cerca di rispondere più accuratamente che puoi. Non preoccuparti se ti sembra difficile. concentrati sul significato delle parole e dai la risposta che ti sembra più corretta.")
for (i in 1:(dim(this_participant)[1])){
  
  this_response <- paste("<<", opts[this_participant$response[i]], ">>", sep="")

this_response <- paste("<<", opts[this_participant$response[i]], ">>", sep="")
P<- paste("La parola", this_participant$stimulus[i], "appare sullo schermo . L'opzione associata al tasto ", opts[1], "è", this_participant$response_option_1[i], ". L'opzione associata al tasto", opts[2], "è", this_participant$response_option_2[i], ". Tu premi ", this_response, ".", this_participant$accuracy[i] ,".")
text <- paste(text, P)
}
D$text[id] <- text
D$participant_id[id] <- (unique(E3$participant_id)[id])
}

D$experiment <- "bonandrini2026_SPChumaneval_Exp3"
D3 <- D
rm(list = setdiff(ls(), c("D1","D2", "D3"))) #clean and keep only final


D <- rbind(D1,D2,D3)

################################################################################
#write
filename <- "prompts.jsonl"
filenamezip <- "prompts.jsonl.zip"

stream_out(D, file(filename))
zip(filenamezip, files = filename)
file.remove(filename)


