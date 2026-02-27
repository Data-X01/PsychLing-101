import pandas as pd
import json

# ---------- PARAMETERS ----------

instruction_text = (
    "Instruction:\n"
    "Rate how correct each sentence sounds.\n"
    "Options: correct / neither correct nor wrong / wrong.\n\n"
)

# Stimuli: Greek + English
stimuli = [
    ("Περισσότεροι άνθρωποι έχουν πάει στο Λονδίνο απ’ ό,τι εγώ.",
     "More people have been to London than I have."),

    ("Περισσότεροι άνθρωποι έχουν πάει στο Μιλάνο απ’ ό,τι εσύ.",
     "More people have been to Milan than you have."),

    ("Περισσότερα αγόρια έχουν πάει στο Παρίσι απ’ ό,τι αυτός.",
     "More boys have been to Paris than he has."),

    ("Περισσότερα κορίτσια έχουν πάει στη Στοκχόλμη απ’ ό,τι αυτός.",
     "More girls have been to Stockholm than he has."),

    ("Λιγότεροι άνθρωποι έχουν πάει στο Βερολίνο απ’ ό,τι εγώ.",
     "Fewer people have been to Berlin than I have."),

    ("Περισσότερα παιδιά έχουν τελειώσει το λύκειο απ’ ό,τι εγώ.",
     "More kids have finished high school than I have."),

    ("Περισσότερα παιδιά έχουν τελειώσει το σχολείο απ’ ό,τι εσύ.",
     "More kids have finished school than you have."),

    ("Περισσότεροι άντρες έχουν τελειώσει το σχολείο απ’ ό,τι αυτός.",
     "More men have finished school than he has."),

    ("Περισσότεροι άντρες έχουν τελειώσει το λύκειο απ’ ό,τι αυτή.",
     "More men have finished high school than she has."),

    ("Λιγότεροι άνθρωποι έχουν τελειώσει το λύκειο απ’ ό,τι εγώ.",
     "Fewer people have finished high school than I have."),

    ("Περισσότερες φορές πήγα στην Αγγλία απ’ ό,τι στη Γερμανία.",
     "More times I visited England than Germany."),

    ("Περισσότερες φορές τρώω στο γραφείο μου απ’ ό,τι στο σπίτι μου.",
     "More times I eat at my office than at my house."),

    ("Περισσότερες φορές πηγαίνω στο σινεμά απ’ ό,τι στο θέατρο.",
     "More times I go to the cinema than to the theater."),

    ("Περισσότερες φορές πηγαίνουμε στη θάλασσα απ’ ό,τι στο βουνό.",
     "More times we go to the sea than to the mountain."),

    ("Περισσότερες φορές μαγειρεύω μόνη μου απ’ ό,τι με τους φίλους.",
     "More times I cook alone than with friends."),

    ("Το κλειδί εκείνων των συρταριών βρίσκονται στο μαρμάρινο τραπέζι.",
     "The key to these cabinets are on the marble table."),

    ("Η κόρη των δασκάλων της Μαρίνας στέκονται στην αυλή του σχολείου.",
     "The daughter of Marina’s teachers are standing in the school yard."),

    ("Το σκυλάκι των παιδιών των γειτόνων μας παίζουν ήσυχα στον κήπο τους.",
     "The doggie of our neighbours’ kids are playing quietly in the garden."),

    ("Η φλόγα των κεριών στα τραπεζάκια του μπαρ τρεμόπαιζαν στο σκοτάδι.",
     "The flame of the candles on the tables of the bar were flickering in the darkness."),

    ("Ο θόρυβος από τα τραγούδια των μαθητών μας δεν σταματούν ποτέ.",
     "The noise from the songs of our students never end."),

    ("Τα βιβλία της κόρης του Κωνσταντίνου βρίσκεται στη βιβλιοθήκη.",
     "The books of Konstantinos’ daughter is at the library."),

    ("Η βαλίτσα των διάσημων τραγουδιστών ξεχάστηκαν μέσα στο ταξί.",
     "The suitcase of the famous singers were forgotten in the taxi."),

    ("Η θήκη εκείνων των φακών επαφής βρίσκονται στο πάνω συρτάρι.",
     "The case of these contact lenses are on the top shelf."),

    ("Οι ηθοποιοί που ο σκηνοθέτης οδηγεί τους ακούει σιωπηλά.",
     "The actors that the director guides listens to them silently."),

    ("Οι ποδηλάτες που ο οδηγός βλέπει κάθε Δευτέρα τους χαιρετά.",
     "The bicyclists that the driver sees every Monday salutes them."),

    ("Οι μαθητές που ο δάσκαλος απέβαλλε τους έκανε παράπονο.",
     "The students that the teacher expelled complained to them."),

    ("Οι ασθενείς που ο γιατρός κούραρε τους ευχαρίστησε πολύ θερμά.",
     "The patients that the doctor cured thanked them profoundly."),

    ("Οι μουσικοί που ο μαέστρος διευθύνει τους ακούει προσεκτικά.",
     "The musicians that the maestro conducts listens to them carefully."),

    ("Οι κολυμβητές που ο προπονητής ανέλαβε πάντα τους ακούει.",
     "The swimmers that the trainer took on always listen to them."),

    ("Οι γραμματείς που ο διευθυντής προσέλαβε τους απογοήτευσε.",
     "The secretaries that the director hired disappointed them.")
]

# ---------- FUNCTION ----------

def generate_json(df, experiment_name):

    # Find all Acceptability judgment columns and RT columns
    response_columns = [c for c in df.columns if "Acceptability" in c]
    rt_columns = [c for c in df.columns if "Reaction" in c]

    all_entries = []

    for _, row in df.iterrows():

        text_prompt = instruction_text
        rt_list = []

        # Iterate through trials based on the stimuli
        for i in range(len(stimuli)):

            # Safety check: some participants may have fewer columns
            if i >= len(response_columns):
                break

            response_col = response_columns[i]
            rt_col = rt_columns[i] if i < len(rt_columns) else None

            greek, english = stimuli[i]
            response = row[response_col]
            rt = row[rt_col] if rt_col and pd.notna(row[rt_col]) else None

            text_prompt += (
                f"Sentence {i+1}:\n"
                f"{greek}\n"
                f"{english}\n"
                f"Your response: <<{response}>>\n"
            )

            if rt is not None:
                text_prompt += f"Reaction time: {rt} ms\n"

                rt_list.append(rt)

            text_prompt += "\n"

        # Build JSON entry
        entry = {
            "text": text_prompt,
            "experiment": experiment_name,
            "participant": row["participant_id"],
            "rt": rt_list
        }

        # Optional metadata
        for meta_col in ["age", "Gender (F/M)", "country_of_residence", "years_spent_in_countries_of_residence"]:
            if meta_col in df.columns:
                entry[meta_col] = row[meta_col]

        all_entries.append(entry)

    return all_entries

# ---------- LOAD DATA ----------

exp1 = pd.read_csv("exp1.csv")
exp2 = pd.read_csv("exp2.csv")

all_data = []
all_data.extend(generate_json(exp1, "exp1"))
all_data.extend(generate_json(exp2, "exp2"))

# ---------- SAVE JSON ----------

with open("prompts.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print("Done. JSON saved as prompts.json")