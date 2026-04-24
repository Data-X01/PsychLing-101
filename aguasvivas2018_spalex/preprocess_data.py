from pathlib import Path
import pandas as pd


def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


def write_codebook(base_dir: Path) -> None:
    codebook_path = base_dir / "CODEBOOK.csv"
    if codebook_path.exists():
        return
    rows = [
        {"column_name": "participant_id", "description": "Unique participant identifier"},
        {"column_name": "age", "description": "Participant age in years"},
        {"column_name": "gender", "description": "Participant gender (m/f/na)"},
        {"column_name": "handedness", "description": "Participant handedness (right/left)"},
        {"column_name": "education", "description": "Highest education level, translated to English"},
        {"column_name": "num_foreign_languages", "description": "Number of foreign languages spoken"},
        {"column_name": "best_foreign_language", "description": "Best (foreign) language spoken"},
        {"column_name": "country_of_birth", "description": "Country of birth"},
        {"column_name": "trial_id", "description": "Unique trial identifier"},
        {"column_name": "trial_order", "description": "Presentation order within session"},
        {"column_name": "stimulus", "description": "Word/nonword string presented to participants"},
        {"column_name": "condition", "description": "Lexicality condition: W (word) or NW (nonword)"},
        {"column_name": "rt", "description": "Response time in milliseconds"},
        {"column_name": "accuracy", "description": "Binary accuracy (1 = correct, 0 = incorrect)"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


EDUCATION_MAP = {
    "Doctorado": "doctorate",
    "Master": "master",
    "Licencitura/Grado": "bachelor",
    "Bachillerato": "high school",
    "Secundaria": "middle school",
    "Primaria": "primary school",
    "Sin estudios": "no formal education",
}

HANDEDNESS_MAP = {
    "Diestro (derecha)": "right",
    "Zurdo (izquierda)": "left",
}

COUNTRY_MAP = {
    "España": "Spain",
    "Argentina": "Argentina",
    "México": "Mexico",
    "Colombia": "Colombia",
    "Chile": "Chile",
    "Perú": "Peru",
    "Venezuela": "Venezuela",
    "Ecuador": "Ecuador",
    "Guatemala": "Guatemala",
    "Cuba": "Cuba",
    "República Dominicana": "Dominican Republic",
    "Panamá": "Panama",
}

LANGUAGE_MAP = {
    "Español": "Spanish",
    "Inglés": "English",
    "No aplicable": "Not applicable",
    "Catalán": "Catalan",
    "Francés": "French",
    "Euskera": "Basque",
    "Gallego": "Galician",
    "Italiano": "Italian",
    "Portugués": "Portuguese",
    "Alemán": "German",
    "Valenciano": "Valencian",
    "Japonés": "Japanese",
    "Hebreo": "Hebrew",
    "Sueco": "Swedish",
    "Ruso": "Russian",
    "Chino mandarín": "Mandarin Chinese",
    "Neerlandés": "Dutch",
    "Árabe": "Arabic",
    "Griego": "Greek",
    "Abjasio": "Abkhaz",
    "Náhuatl": "Nahuatl",
    "Esperanto": "Esperanto",
    "Guaraní": "Guaraní",
    "Latín": "Latin",
    "Coreano": "Korean",
    "Danés": "Danish",
    "Polaco": "Polish",
    "Rumano": "Romanian",
    "Noruego": "Norwegian",
    "Mexicanero": "Mexicanero",
    "Finés": "Finnish",
    "Aimara": "Aymara",
    "Checo": "Czech",
    "Maya": "Mayan",
    "Totonaco": "Totonac",
    "Acateco": "Acatec",
    "Kaqchikel": "Kaqchikel",
    "Escocés": "Scottish",
    "Acano": "Acano",
    "Ingusetio": "Ingush",
    "Croata": "Croatian",
    "Zapoteco": "Zapotec",
    "Turco": "Turkish",
    "Serbio": "Serbian",
    "Mixe": "Mixe",
    "Kichwa": "Kichwa",
    "Indonesio": "Indonesian",
    "Eslovaco": "Slovak",
    "Achagua": "Achagua",
    "Veneciano": "Venetian",
    "Islandés": "Icelandic",
    "Quichua": "Quichua",
    "Tzeltal": "Tzeltal",
    "Persa": "Persian",
    "Papiamento": "Papiamento",
    "Afrikáans": "Afrikaans",
    "Otomí": "Otomi",
    "Feroés": "Faroese",
    "Amuesha": "Amuesha",
    "Istrorrumano": "Istro-Romanian",
    "Búlgaro": "Bulgarian",
    "Aguaruna": "Aguaruna",
    "Sindhi": "Sindhi",
    "Fala": "Fala",
    "Armenio": "Armenian",
    "Cantonés": "Cantonese",
    "Abaza": "Abaza",
    "Adele": "Adele",
    "Mapuche": "Mapuche",
    "Mazateco": "Mazatec",
    "Achuar": "Achuar",
    "Esloveno": "Slovenian",
    "Quiché": "K'iche'",
    "Qeqchi": "Q'eqchi'",
    "Bora": "Bora",
    "Mam": "Mam",
    "Chinanteco": "Chinantecan",
    "Tlapaneco": "Tlapanec",
    "Akawayo": "Akawaio",
    "Creole haitiano": "Haitian Creole",
    "Leonés": "Leonese",
    "Arawak": "Arawak",
    "Wolof": "Wolof",
    "Galés": "Welsh",
    "Hindi": "Hindi",
    "Bororo": "Bororo",
    "Aguacateco": "Aguacatec",
    "Corso": "Corsican",
    "Chabacano": "Chavacano",
    "Alagüilac": "Alagüilac",
    "Chuvasio": "Chuvash",
    "Rapanui": "Rapa Nui",
    "Huichol": "Huichol",
    "Barí": "Barí",
    "Amarakaeri": "Amarakaeri",
    "Chichimeca jonaz": "Chichimec",
    "Romaní": "Romani",
    "Bengalí": "Bengali",
    "Tarahumara o rarámuri": "Tarahumara",
    "Maorí": "Māori",
    "Arpitano": "Arpitan",
    "Apiacá": "Apiaká",
    "Bereber": "Berber",
    "Chamorro": "Chamorro",
    "Chatino": "Chatino",
    "Georgiano": "Georgian",
    "Zoque": "Zoque",
    "Mixteco": "Mixtec",
    "Guyaratí": "Gujarati",
    "Miskito": "Miskito",
    "Ixil": "Ixil",
    "Javanés": "Javanese",
    "Dzongkha": "Dzongkha",
    "Páez": "Nasa Yuwe",
    "Creole colombiano": "Colombian Creole",
    "Amuzgo": "Amuzgo",
    "Lituano": "Lithuanian",
    "Mazahua": "Mazahua",
    "Chol": "Ch'ol",
    "Mongol": "Mongolian",
    "Amahuaca": "Amahuaca",
    "Kanjobal": "Q'anjob'al",
}


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "merged.csv"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    df = pd.read_csv(original_path)

    if "gender" in df.columns:
        df = df.drop(columns=["gender"])

    rename_map = {
        "profile_id": "participant_id",
        "gender_rec": "gender",
        "no_foreign_lang": "num_foreign_languages",
        "best_foreign": "best_foreign_language",
        "country": "country_of_birth",
        "spelling": "stimulus",
        "lexicality": "condition",
    }
    df = df.rename(columns=rename_map)

    # Type conversions
    df["age"] = df["age"].astype(float)
    df["rt"] = df["rt"].astype(float)
    df["accuracy"] = df["accuracy"].astype("Int64")

    # Translate all Spanish fields to English
    df["education"] = df["education"].map(EDUCATION_MAP).fillna(df["education"].str.lower())
    df["handedness"] = df["handedness"].map(HANDEDNESS_MAP).fillna(df["handedness"].str.lower())
    df["best_foreign_language"] = df["best_foreign_language"].map(LANGUAGE_MAP).fillna(df["best_foreign_language"])
    df["country_of_birth"] = df["country_of_birth"].map(COUNTRY_MAP).fillna(df["country_of_birth"])

    # Factorize trial_id to integers starting at 1
    if "trial_id" in df.columns:
        df["trial_id"] = pd.factorize(df["trial_id"])[0] + 1

    cols = [
        "participant_id",
        "age",
        "gender",
        "handedness",
        "education",
        "num_foreign_languages",
        "best_foreign_language",
        "country_of_birth",
        "trial_id",
        "trial_order",
        "stimulus",
        "condition",
        "rt",
        "accuracy",
    ]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant_id", "trial_order"] if c in df_out.columns])
    df_out = df_out.loc[:, ~df_out.columns.duplicated()]

    df_out.to_csv(processed_dir / "exp1.csv", index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())