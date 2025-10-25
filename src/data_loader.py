import json
import os

def load_questions(domain):
    """Încărcare întrebări din fișierul fea_questions.json în funcție de domeniu."""
    data_path = os.path.join(os.path.dirname(__file__), "../data/fea_questions.json")
    if not os.path.exists(data_path):
        raise FileNotFoundError("Fișierul fea_questions.json nu a fost găsit în folderul /data")

    with open(data_path, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    return [q for q in all_questions if q["domain"] == domain]
