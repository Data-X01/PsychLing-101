import os
import pandas as pd

#### Read data ####
script_dir = os.path.dirname(os.path.abspath(__file__))

df_old_part = pd.read_csv(os.path.join(script_dir,"original_data/older_adult_data.txt"), sep="\t")
df_old_trial = pd.read_csv(os.path.join(script_dir,"original_data/older_adult_trial_data.txt"), sep="\t")
df_young_part = pd.read_csv(os.path.join(script_dir,"original_data/younger_adult_data.txt"), sep="\t")
df_young_trial = pd.read_csv(os.path.join(script_dir,"original_data/younger_adult_trial_data.txt"), sep="\t")

# Merge and concat dfs
df_old_merged = pd.merge(df_old_trial, df_old_part, on="id")
df_young_merged = pd.merge(df_young_trial, df_young_part, on="id")

df_all = pd.concat([df_old_merged, df_young_merged], ignore_index=True)

#### Data cleaning ####

# Rename Variables
df_all = df_all.rename(columns={
    "id": "participant_id",
    "native_language": "first_language",
    "stimulus_word": "stimulus",
    "rating": "response"
})

# Convert rt seconds to ms
df_all["rt"] = round(df_all["rt"]*1000, 1)

# Add trial no (assumption: order in df is order that words were presented; 0 indexed)
df_all["trial_id"] = df_all.groupby("participant_id").cumcount().mod(90)

# Add block no. (each session 90 words; 0 indexed)
df_all["session_no"] = df_all.groupby("participant_id").cumcount().floordiv(90)


# Reorder columns to put key IDs and RT at the front
cols = list(df_all.columns)
front_cols = ["participant_id", "session_no", "trial_id"]
if "rt" in cols:
    front_cols.append("rt")

# Exclude front columns from the rest
rest_cols = [c for c in cols if c not in front_cols]
df_all = df_all[front_cols + rest_cols]

# Fix coding of 'response'
df_all["response"] = pd.to_numeric(df_all["response"], errors="coerce").astype("Int64")

# Fix coding of 'first_language'
df_all.loc[df_all["first_language"] == "enlis", "first_language"] = "english"
df_all.loc[df_all["first_language"] == "enligh", "first_language"] = "english"

# Create new variable 'childhood_country'
df_all["childhood_location_clean"] = (
    df_all["childhood_location"]
    .astype(str)
    .str.lower()
    .str.replace(r"[^a-z]", "", regex=True)
)

uk_keywords = {
    'kent', 'uk', 'unitedkingdom', 'anglesey', 'england', 'surrey', 'monmouthshire', 'suffolk', 'scotland', 'staffordshire', 'hampshire', 'swanseawalesuk', 'newcastleupontyne', 'leicestershire', 'liverpoollancashireslashmanchesteruk', 'manchester', 'cumbria', 'northeastengland', 'cheshire', 'britain', 'nottinghamshire', 'london', 'hertfordshire', 'cambridgeshire', 'countydurhamengland', 'yorkshire', 'westyorkshire', 'berkshire', 'essexuk', 'eastyorkshire', 'westmidlands', 'berksuk', 'lancashire', 'fife', 'cardiff', 'dumfrieshire', 'lincolnshire', 'wales', 'essex', 'tyneandwear', 'birmingham', 'scotlandmidlothian', 'yorkshireuk', 'hamshireuk', 'sloughengland', 'warwickshireslashengland', 'londonuk', 'wiltshire', 'lancashireengland', 'surreyengland', 'surreyuk', 'lancashireslashengland', 'lanarkshire', 'nottingham', 'isleofely', 'southyorkshireengland', 'derbyshireunitedkingdomrightright', 'warwickshire', 'northeastlincs', 'sussex', 'ilivedintheuk', 'southyorkshire', 'lincolnshireengland', 'plymouth', 'suffolkuk', 'bristolengland', 'angus', 'gb', 'eastanglia', 'shropshire', 'sloughengland', 'warwickshireslashengland', 'rhyl', 'derbyshire', 'wiltshire', 'lancashireengland', 'surreyengland', 'surreyuk', 'lancashireslashengland', 'southyorkshireengland', 'derbyshireunitedkingdomrightright', 'warwickshire', 'sussex', 'ilivedintheuk', 'southyorkshire', 'lincolnshireengland', 'plymouth', 'suffolkuk', 'bristolengland', 'angus', 'northernitreland', 'durham', 'merseyside', 'northampton', 'oxfordshire', 'devon', 'norfolk', 'northernireland', 'bedfordshire', 'warrington', 'derby', 'somerset', 'herefordshire', 'lcontrollcontrollcontrollcontrollcontrollcontrollcontrolibirmingham', 'worcestershire', 
}

us_keywords = {
    'california', 'florida', 'tx', 'oregon', 'ny', 'newyork', 'ia', 'illinois', 'missouri', 'pennsylvania', 'mass', 'wi', 'maryland', 'michigan', 'il', 'southcarolina', 'ma', 'pa', 'louisiana', 'ohio', 'pensylvania', 'springfield', 'connecticut', 'hawaii', 'ct', 'iowa', 'newjersey', 'mo', 'newhampshie', 'colorado', 'montana', 'ca', 'wyoming', 'utah', 'or', 'tennessee', 'in', 'kentucky', 'tn', 'kansas', 'newyorkcity', 'indiana', 'nj', 'me', 'wisconsin', 'virginia', 'northcarolina', 'sc', 'washington', 'illinoids', 'minnesota', 'southdakota', 'ga', 'dc', 'mi', 'fl', 'georgia', 'va', 'northdakota', 'nc', 'de', 'arizona', 'ar', 'mn', 'oklahoma', 'ms', 'nevada', 'nv', 'ks', 'ohioandmichigan', 'delaware', 'philadelphia', 'wy', 'dallas', 'pennslyvania', 'unitedstates', 'unitedstatestexas', 'nccharlotte', 'virginianorfolk', 'westvirginia', 'vermont', 'maine', 'brooklyn', 'alabama', 'arkansas', 'kentucky', 'texas', 'massachusetts', 'oh', 'orleansparishlouisiana', 'iledgevillegeorgia', 'nebraska', 'numnumdividohio', 'ky', 'sd', 'newmexico', 'co', 'massachusets', 'ri', 'mich', 'md', 'la', 'al', 'wv','californiatab', 'massachusettsa', 'nh', 'rhodeisland', 'idaho', 'newyorkstate', 'wa', 'ilinois', 'vevermont', 'southcarolinakansasvirginiapennsylvania', 'geogia', 'az', 'mqine'
}

canada_keywords = {
    'ontario', 'quebec', 'saskatchewan', 'britishcolumbia', 'bc', 'alberta', 'britishcolombia', 'mb', 'manitoba', 'ab', 'ontariocanada', 'on', 'novascotia', 'newbrunswick', 'newfoundland', 'montreal', 'regina', 'nl', 'ont'
}

other_keywords = {
    'southafrica', 'hongkong', 'germany'
}

def classify_region(x):
    if pd.isna(x):
        return None
    if x in uk_keywords:
        return "uk"
    if x in us_keywords:
        return "us"
    if x in canada_keywords:
        return "canada"
    if x in other_keywords:
        return "other"

df_all["country_of_birth"] = df_all["childhood_location_clean"].apply(classify_region)

df_all = df_all.drop("childhood_location_clean", axis=1)

# Create new variable 'current_country'
df_all["current_location_clean"] = (
    df_all["current_location"]
    .astype(str)
    .str.lower()
    .str.replace(r"[^a-z]", "", regex=True)
)

# Add additional keywords
uk_keywords = uk_keywords.union({
    'powys', 'newport', 'cornwall', 'northumberland', 'liverpoolmerseysideslashlancashire', 'southeastengland', 'northyorkshire', 'middlesex', 'eastsussex', 'kentunitedkingdom', 'dorsetuk', 'gwynedd', 'northamptonshire', 'nthlincolnshire', 'roxburghshire', 'englandsurrey', 'midwales', 'devonengland', 'eastrenfrewshire', 'morayshire', 'hampshireslashengland', 'bromleykent', 'ayrshirescotland', 'shropshireengland', 'dorset', 'bedfordshireuk', 'hertford', 'eastmidlands', 'fenland', 'greatermanchester', 'eastlindsey', 'brightonuk', 'isleofwight', 'somersetuk', 'northumberlandengland', 'moray', 'merseysideuk', 'westsussex', 'southlanarkshire', 'stockport', 'perthandkinross', 'gloucestershire', 'countyantrim', 'stirlingshire', 'bangor'
})

us_keywords = us_keywords.union({
    'washigton', 'mississippi', 'nashvilletennessee', 'joliet', 'washingtonstate', 'washingtondc', 'newhampshire', 'vt', 'ut', 'ok', 'nd', 'usa', 'pennsylania', 'alaska', 'youngsville', 'brookpark', 'charlotte', 'mt', 'gorgi', 'newyorkcounty', 'cornelia', 'mississppi'
})

canada_keywords = canada_keywords.union({
    'mississauga', 'newbrunsiwck'
})

other_keywords = other_keywords.union({
    'reggioemilia', 'australiaminus', 'auckland', 'abroad', 'franceilledefrance', 'a', 'gs', 'italy', 'portugalporto', 'newzealand'
})

df_all["country_of_residence"] = df_all["current_location_clean"].apply(classify_region)

df_all = df_all.drop("current_location_clean", axis=1)

#### Codebook ####
codebook = pd.read_csv(os.path.join(script_dir,"../CODEBOOK.csv"))

# Add childhood_location and current_location to CODEBOOK.csv
codebook.loc[len(codebook)] = [
    "childhood_location",
    "The participant's self-reported state/province in which they lived the most between birth and 7 years of age. Free-text responses. This location information has not been preprocessed."]
codebook.loc[len(codebook)] = [
    "current_location",
    "The participant's self-reported state/province in which they currently live. Free-text responses. This location information has not been preprocessed."]

codebook.loc[len(codebook)] = [
    "session_no",
    "Sequential index indicating the session number for each participant. Each session consists of a fixed block of 90 trials."]

# Drop rows in codebook that aren't in the df
codebook = codebook[codebook["Recommended Column Name"].isin(df_all.columns)]

# Save codebook
codebook.to_csv(os.path.join(script_dir,"CODEBOOK.csv"), index=False)

# Save processed data
folder = os.path.join(script_dir, "processed_data")
os.makedirs(folder, exist_ok=True)
df_all.to_csv(os.path.join(script_dir,"processed_data/exp1.csv"), index=False)