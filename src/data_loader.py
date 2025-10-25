import json
import os
import random


def load_questions(domain=None):
    """
    Încarcă întrebările din fișierul data/fea_questions.json.
    Poate încărca întrebările doar pentru un domeniu sau mixate.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "fea_questions.json")

    if not os.path.exists(data_path):
        print(f"[Eroare] Fișierul {data_path} nu există!")
        return []

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            all_questions = json.load(f)
    except Exception as e:
        print(f"[Eroare] Nu s-au putut încărca întrebările: {e}")
        return []

    # Dacă s-a cerut un domeniu anume
    if domain and domain.lower() != "mix":
        domain_questions = [q for q in all_questions if q["domain"].lower() == domain.lower()]
        if not domain_questions:
            print(f"[Avertisment] Nu există întrebări pentru domeniul '{domain}'. Se folosește MIX.")
            return all_questions
        return domain_questions

    # Domeniu = mix → toate întrebările combinate
    return all_questions


def get_domains():
    """
    Returnează lista domeniilor disponibile din fișierul JSON.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "fea_questions.json")

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            all_questions = json.load(f)
        domains = sorted(list(set(q["domain"].lower() for q in all_questions)))
        return domains
    except Exception:
        return []
