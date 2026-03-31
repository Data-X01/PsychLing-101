
library(data.table)

responses  <- fread("original_data/responses.txt")
sessions   <- fread("original_data/sessions.txt")

responses[, String := as.character(String)]

setkey(responses, Id_Session)
setkey(sessions, Id_Session)
df <- sessions[responses]

cols_keep <- c(
  "Id_Session", "Device", "Age", "Gender", "Raising", "Education", "Proficiency",
  "First_Contact", "Mother", "Father", "Exposure", "Languages",
  "Trial_Order", "String",
  "Is_Word", "Correct"
)
df <- df[, ..cols_keep]
setorder(df, Id_Session, Trial_Order)

setnames(df, old = c(
  "Id_Session","Device","Age","Gender","Raising","Education",
  "Proficiency","First_Contact","Mother","Father","Exposure",
  "Languages","Trial_Order","String","Is_Word","Correct"
), new = c(
  "session_id","device","age","sex","raising","education",
  "proficiency","age_first_contact","mother_language","father_language",
  "exposure","n_languages","trial_order","stimulus", "is_word","accuracy"
))

df[, session_id := as.integer(factor(session_id))]

df[, sex := fcase(sex=="Home","male", sex=="Dona","female", default=NA_character_)]
df[, device := fcase(device=="PC","keyboard", device=="MB","touch", default=NA_character_)]
df[, education := fcase(
  education==1,"no_edu",education==2,"primary",education==3,"secondary",
  education==4,"vocat_mid",education==5,"vocat_high",education==6,"high_school",
  education==7,"univ",education==8,"postgrad",default=NA_character_
)]

raising_map <- c(
  "Catalunya"="Catalonia","Balears"="Balearic_Islands","Comunitat valenciana"="Valencian_Community",
  "Andorra"="Andorra","Resta d'Espanya"="Rest_of_Spain","Mèxic"="Mexico","França"="France",
  "Portugal"="Portugal","Xile"="Chile","Bèlgica"="Belgium","Estats Units"="United_States",
  "Brasil"="Brazil","Argentina"="Argentina","Àustria"="Austria","Suècia"="Sweden",
  "Veneçuela"="Venezuela","Colòmbia"="Colombia","Equador"="Ecuador","Marroc"="Morocco",
  "Alemanya"="Germany","Regne Unit"="United_Kingdom","Suïssa"="Switzerland",
  "Canadà"="Canada","Itàlia"="Italy","Guinea Equatorial"="Equatorial_Guinea",
  "Bahames"="Bahamas","Salvador"="El_Salvador","Madagascar"="Madagascar",
  "Rússia"="Russia","Uruguai"="Uruguay","Afganistan"="Afghanistan",
  "Guatemala"="Guatemala","Sudan"="Sudan","República Dominicana"="Dominican_Republic",
  "Països Baixos"="Netherlands","Cuba"="Cuba","Trinitat i Tobago"="Trinidad_and_Tobago",
  "Panamà"="Panama","Líban"="Lebanon","Noruega"="Norway","Perú"="Peru",
  "Romania"="Romania","Dominica"="Dominica","Bulgària"="Bulgaria",
  "Antigua i Barbuda"="Antigua_and_Barbuda","Egipte"="Egypt","Bolívia"="Bolivia",
  "Xina"="China","Tailàndia"="Thailand","Nepal"="Nepal","Algèria"="Algeria",
  "Síria"="Syria","Luxemburg"="Luxembourg","Índia"="India","Djibouti"="Djibouti",
  "Albània"="Albania","Costa Rica"="Costa_Rica","Emirats Àrabs Units"="United_Arab_Emirates",
  "Estònia"="Estonia","Armènia"="Armenia","Paraguai"="Paraguay","Angola"="Angola",
  "Austràlia"="Australia","Sud-àfrica"="South_Africa","Dinamarca"="Denmark",
  "Ucraïna"="Ukraine","Sudan del Sud"="South_Sudan","Camerun"="Cameroon",
  "Nicaragua"="Nicaragua"
)
df[, raising := raising_map[raising]]

lang_map <- c(
  "Català"="Catalan","Castellà"="Spanish","Francès"="French","Gallec"="Galician",
  "Portuguès"="Portuguese","Alemany"="German","Anglès"="English","Danès"="Danish",
  "Romanès"="Romanian","Basc"="Basque","Aranés"="Aranese","Aranès"="Aranese",
  "Neerlandès"="Dutch","Italià"="Italian","Suec"="Swedish","Retoromànic"="Rhaeto-Romance",
  "Eslovè"="Slovenian","Japonès"="Japanese","Fala"="Fala","Àzeri"="Azerbaijani",
  "Tai"="Thai","Polonès"="Polish","Noruec"="Norwegian","Islandès"="Icelandic",
  "Lleonès"="Leonese","Hongarès"="Hungarian","Maltès"="Maltese","Alsacià"="Alsatian",
  "Albanès"="Albanian","Rus"="Russian","Grec"="Greek","Bretón"="Breton","Croat"="Croatian",
  "Cantonès"="Cantonese","Finès"="Finnish","Hebreu"="Hebrew","Occità"="Occitan",
  "Àrab"="Arabic","Afrikaans"="Afrikaans","Macedoni"="Macedonian","Sicilià"="Sicilian",
  "Turc"="Turkish","Ioruba"="Yoruba","Gaèlic Irlandès"="Irish_Gaelic",
  "Napolitano"="Neapolitan","Kirundi"="Kirundi","Txec"="Czech","Mandinka"="Mandinka",
  "Kurd"="Kurdish","Serbi"="Serbian","Amhàric"="Amharic"
)
df[, mother_language := lang_map[mother_language]]
df[, father_language := lang_map[father_language]]

df[, is_word  := as.integer(is_word)]
df[, accuracy := as.integer(accuracy)]
df[, age := as.integer(age)]
df[, sex := factor(sex)]
df[, device := factor(device)]

dir.create("processed_data", showWarnings = FALSE)
fwrite(df, "processed_data/exp1.csv")

rm(responses, sessions, lang_map, raising_map, cols_keep)
gc()
