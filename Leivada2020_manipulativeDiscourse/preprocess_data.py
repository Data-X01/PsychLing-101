import pandas as pd
import numpy as np
import chardet
import csv
import os

# --- Create folder if it doesn't exist ---
os.makedirs("processed_data", exist_ok=True)

# --- Detect CSV encoding ---
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    detected = chardet.detect(rawdata)
    if detected and detected.get('encoding') and detected.get('confidence', 0) > 0.7 and detected['encoding'].upper() != 'ASCII':
        return detected['encoding']
    for enc in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
        try:
            rawdata.decode(enc)
            return enc
        except:
            continue
    return 'latin-1'

# --- Stimulus list ---
stimulus = [
    "1. Περισσότεροι άνθρωποι έχουν πάει στο Λονδίνο απ’ ό,τι εγώ. More people have been to London than I have.",
    "2. Περισσότεροι άνθρωποι έχουν πάει στο Μιλάνο απ’ ό,τι εσύ. More people have been to Milan than you have.",
    "3. Περισσότερα αγόρια έχουν πάει στο Παρίσι απ’ ό,τι αυτός. More boys have been to Paris than he has.",
    "4. Περισσότερα κορίτσια έχουν πάει στη Στοκχόλμη απ’ ό,τι αυτός. More girls have been to Stockholm than he has.",
    "5. Λιγότεροι άνθρωποι έχουν πάει στο Βερολίνο απ’ ό,τι εγώ. Fewer people have been to Berlin than I have.",
    "6. Περισσότερα παιδιά έχουν τελειώσει το λύκειο απ’ ό,τι εγώ. More kids have finished high school than I have.",
    "7. Περισσότερα παιδιά έχουν τελειώσει το σχολείο απ’ ό,τι εσύ. More kids have finished school than you have.",
    "8. Περισσότεροι άντρες έχουν τελειώσει το σχολείο απ’ ό,τι αυτός. More men have finished school than he has.",
    "9. Περισσότεροι άντρες έχουν τελειώσει το λύκειο απ’ ό,τι αυτή. More men have finished high school than she has.",
    "10. Λιγότεροι άνθρωποι έχουν τελειώσει το λύκειο απ’ ό,τι εγώ. Fewer people have finished high school than I have.",
    "11. Περισσότερες φορές πήγα στην Αγγλία απ’ ό,τι στη Γερμανία. More times I visited England than Germany.",
    "12. Περισσότερες φορές τρώω στο γραφείο μου απ’ ό,τι στο σπίτι μου. More times I eat at my office than at my house.",
    "13. Περισσότερες φορές πηγαίνω στο σινεμά απ’ ό,τι στο θέατρο. More times Ι go to the cinema than to the theater.",
    "14. Περισσότερες φορές πηγαίνουμε στη θάλασσα απ’ό,τι στο βουνό. More times we go to the sea than to the mountain.",
    "15. Περισσότερες φορές μαγειρεύω μόνη μου απ’ ό,τι με τους φίλους.",
    "16. Το κλειδί εκείνων των συρταριών βρίσκονται στο μαρμάρινο τραπέζι. The key to these cabinets are on the marble table.",
    "17. Η κόρη των δασκάλων της Μαρίνας στέκονται στην αυλή του σχολείου. The daughter of Marina’s teachers are standing in the school yard.",
    "18. To σκυλάκι των παιδιών των γειτόνων μας παίζουν ήσυχα στον κήπο τους. The doggie of our neighbours’ kids are playing quietly in the garden.",
    "19. Η φλόγα των κεριών στα τραπεζάκια του μπαρ τρεμόπαιζαν στο σκοτάδι. The flame of the candles on the tables of the bar were flickering in the darkness.",
    "20. Ο θόρυβος από τα τραγούδια των μαθητών μας δεν σταματούν ποτέ. The noise from the songs of our students never end.",
    "21. Τα βιβλία της κόρης του Κωνσταντίνου βρίσκεται στη βιβλιοθήκη. The books of Konstantinos’ daughter is at the library.",
    "22. H βαλίτσα των διάσημων τραγουδιστών ξεχάστηκαν μέσα στο ταξί. The suitcase of the famous singers were forgotten in the taxi.",
    "23. Η θήκη εκείνων των φακών επαφής βρίσκονται στο πάνω συρτάρι. The case of these contact lenses are on the top shelf.",
    "24. Οι ηθοποιοί που ο σκηνοθέτης οδηγεί τους ακούει σιωπηλά. The actors that the director guides listens to them silently.",
    "25. Οι ποδηλάτες που ο οδηγός βλέπει κάθε Δευτέρα τους χαιρετά. The bicyclists that the driver sees every Monday salutes them.",
    "26. Οι μαθητές που ο δάσκαλος απέβαλλε τους έκανε παράπονο. The students that the teacher expelled complained to them.",
    "27. Οι ασθενείς που ο γιατρός κούραρε τους ευχαρίστησε πολύ θερμά. The patients that the doctor cured thanked them profoundly.",
    "28. Οι μουσικοί που ο μαέστρος διευθύνει τους ακούει προσεκτικά. The musicians that the maestro conducts listens to them carefully.",
    "29. Οι κολυμβητές που ο προπονητής ανέλαβε πάντα τους ακούει. The swimmers that the trainer took on always listen to them.",
    "30. Οι γραμματείς που ο διευθυντής προσέλαβε τους απογοήτευσε. The secretaries that the director hired disappointed them."
]

# --- Column mapping ---
column_mapping = {
    'Participant ID': 'participant_id',
    'Age (in years)': 'age',
    'Gender (F/M)': 'gender',
    'Education (Secondary/Tertiary)': 'education',
    'Handedness (R/L)': 'handedness'
}

# --- Transform file ---
# --- Transform file (updated) ---
def transform_file(file_path):
    enc = detect_encoding(file_path)
    df = pd.read_csv(file_path, encoding=enc, engine='python', sep=';', dtype=str, on_bad_lines='skip')
    df.columns = df.columns.str.strip()

    # Rename columns
    for old, new in column_mapping.items():
        df.columns = [col.replace(old, new) if col.startswith(old) else col for col in df.columns]

    # Participant columns to keep
    id_cols = [c for c in ['participant_id','age','gender','education','handedness'] if c in df.columns]

    # --- Extra columns for bilinguals ---
    extra_cols_mapping = {
        'Countries of residence excluding Greece': 'country_of_residence',
        'Years spent in countries of residence (excluding Greece) minimum time abroad: 4 years)': 'years_spent_in_countries_of_residence'
    }

    extra_cols = [col for col in extra_cols_mapping if col in df.columns]
    for old, new in extra_cols_mapping.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)

    # Response and RT columns (excluding any extra_cols)
    response_cols = [c for c in df.columns if "Acceptability judgment" in c and c not in extra_cols]
    rt_cols = [c for c in df.columns if "Reaction time" in c and c not in extra_cols]

    # Flatten responses and RTs
    responses = df[response_cols].values.flatten() if response_cols else np.array([])
    rts = df[rt_cols].values.flatten() if rt_cols else np.array([])

    # --- Swap responses and rts if needed (bilinguals.csv) ---
    if 'bilinguals.csv' in file_path and len(responses) > 0 and len(rts) > 0:
        is_responses_actually_numeric = False
        first_resp_val = next((val for val in responses if pd.notna(val) and str(val).strip() != ''), None)
        if first_resp_val is not None:
            try:
                float(first_resp_val)
                is_responses_actually_numeric = True
            except ValueError:
                pass

        is_rts_actually_string = False
        first_rt_val = next((val for val in rts if pd.notna(val) and str(val).strip() != ''), None)
        if first_rt_val is not None:
            try:
                float(first_rt_val)
                is_rts_actually_string = False
            except ValueError:
                is_rts_actually_string = True

        if is_responses_actually_numeric and is_rts_actually_string:
            responses, rts = rts, responses
            print(f"Swapped 'response' and 'rt' data for {file_path} based on content.")

    n_trials = len(stimulus)  # assuming stimulus length per participant
    participant_info = {col: np.repeat(df[col].values, n_trials) for col in id_cols}

    # --- Include extra bilingual info (repeated per trial) ---
    for col in extra_cols:
        participant_info[extra_cols_mapping[col]] = np.repeat(df[extra_cols_mapping[col]].values, n_trials)

    # Repeat stimulus for all participants
    stimulus_repeated = np.tile(stimulus, len(df))

    # Build final long DataFrame
    long_df = pd.DataFrame(participant_info)
    long_df['stimulus'] = stimulus_repeated
    long_df['response'] = responses
    long_df['rt'] = rts

    # --- Column order ---
    final_cols = id_cols + list(extra_cols_mapping.values()) + ['stimulus', 'response', 'rt']
    final_cols = [c for c in final_cols if c in long_df.columns]  # drop missing
    long_df = long_df[final_cols]

    return long_df

# --- Process files ---
input_files = ["original_data/monolinguals.csv", "original_data/bilinguals.csv"]

for i, file in enumerate(input_files, start=1):
    df_out = transform_file(file)
    output_name = f"processed_data/exp{i}.csv"
    df_out.to_csv(output_name, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Saved {output_name}")