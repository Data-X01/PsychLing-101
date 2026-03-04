import pandas as pd
import chardet
import csv

def detect_encoding(file_path):
    """Detect encoding, with fallbacks for common European encodings."""
    with open(file_path, 'rb') as f:
        rawdata = f.read()

    detected = chardet.detect(rawdata)
    if detected and detected.get('encoding'):
        print(f"  Chardet detected: {detected['encoding']} (confidence: {detected.get('confidence', 'unknown')})")
        if detected.get('confidence', 0) > 0.7 and detected['encoding'].upper() != 'ASCII':
            return detected['encoding']

    for encoding in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
        try:
            rawdata.decode(encoding)
            print(f"  Successfully decoded with: {encoding}")
            return encoding
        except (UnicodeDecodeError, AttributeError):
            continue

    print(f"  Defaulting to: latin-1")
    return 'latin-1'


def transform_to_target(input_csv, target_columns, column_mapping=None, questions=None):
    encoding = detect_encoding(input_csv)
    print(f"Detected encoding for {input_csv}: {encoding}")

    # Load CSV
    df = pd.read_csv(
        input_csv,
        engine='python',
        encoding=encoding,
        on_bad_lines='skip',
        dtype=str,
        skip_blank_lines=True,
        sep=';'
    )



    # Rename columns with suffix handling
    if column_mapping:
        new_cols = []
        for col in df.columns:
            mapped = None
            for old, new in column_mapping.items():
                if col.startswith(old):
                    suffix = col[len(old):]  # keep .1, .2, etc.
                    mapped = new + suffix
                    break
            if not mapped:
                mapped = col
            new_cols.append(mapped)
        df.columns = new_cols

    # --- Add stimulus columns before each response ---
    if questions:
        # Find all response columns in order
        response_cols = [c for c in df.columns if c.startswith("response")]
        for i, col in enumerate(response_cols):
            if i < len(questions):
                stimulus_col = "stimulus" if i == 0 else f"stimulus.{i}"
                df.insert(df.columns.get_loc(col), stimulus_col, questions[i])

    # Clean up
    df = df.fillna("")
    df = df.replace(r"\.0$", "", regex=True)
    df = df.apply(lambda col: col.str.strip())
    df = df[~(df == "").all(axis=1)]

    return df


# --- Configuration ---

target_columns = [
    'participant_number', 'participant_id','age','gender','response','accuracy','education',
    'handedness','country_of_residence','years_spent_in_countries_of_residence','rt'
]



column_mapping = {
    'Number of participant': 'participant_number',
    'Participant ID': 'participant_id',
    'Age (in years)': 'age',
    'Gender (F/M)': 'gender',
    'Education (Secondary/Tertiary)': 'education',
    'Handedness (R/L)': 'handedness',
    'Countries of residence excluding Greece': 'country_of_residence',
    'Years spent in countries of residence (excluding Greece)': 'years_spent_in_countries_of_residence',
    'stimulus': 'stimulus',
    'Acceptability judgment (Correct/Neither/Wrong)': 'response',
    'Reaction time in ms': 'rt'
}

questions = [
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
    "15. Περισσότερες φορές μαγειρεύω μόνη μου απ’ ό,τι με τους φίλους. ",
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

input_files = [
    "original_data/monolinguals.csv",
    "original_data/bilinguals.csv",
]

for i, file in enumerate(input_files, start=1):
    df_out = transform_to_target(file, target_columns, column_mapping, questions)
    output_name = f"exp{i}.csv"
    df_out.to_csv(
        output_name,
        index=False,
        quoting=csv.QUOTE_MINIMAL
    )
    print(f"Saved {output_name}")