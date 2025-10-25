import json
import os
import random

def load_questions(domain=None):
    """
    Încarcă întrebările din fișierul data/fea_questions.json.
    Poți filtra după domeniu (structural, crash, moldflow, CFD, NVH).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "fea_questions.json")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Fișierul nu există: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    # Filtrare după domeniu
    if domain and domain.lower() != "all":
        filtered = [q for q in all_questions if q.get("domain", "").lower() == domain.lower()]
        return filtered or all_questions

    return all_questions


def get_random_questions(domain, count):
    """Returnează un subset random de întrebări."""
    questions = load_questions(domain)
    random.shuffle(questions)
    return questions[:count]
