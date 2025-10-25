import json
import os
import random

def load_questions(domain):
    data_path = os.path.join(os.path.dirname(__file__), "../data/fea_questions.json")

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Eroare: fișierul fea_questions.json lipsește.")
        return []

    # Filtrare după domeniu
    filtered = [q for q in data if q.get("domain", "").lower() == domain.lower()]
    random.shuffle(filtered)
    return filtered
