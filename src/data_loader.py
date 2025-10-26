import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
QUESTIONS_FILE = os.path.join(DATA_DIR, "fea_questions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")


# ===================== ÎNCĂRCARE ÎNTREBĂRI =====================
def load_questions(domain=None):
    """
    Încarcă întrebările din fișierul JSON.
    Dacă se specifică un domeniu, returnează doar întrebările acelui domeniu.
    """
    if not os.path.exists(QUESTIONS_FILE):
        print(f"[Eroare] Fișierul {QUESTIONS_FILE} nu există.")
        return []

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if domain:
                return [q for q in data if q.get("domain") == domain]
            return data
    except Exception as e:
        print(f"[Eroare la încărcarea întrebărilor]: {e}")
        return []


# ===================== SALVARE / ÎNCĂRCARE SETĂRI =====================
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Eroare la citirea setărilor]: {e}")
        return {}

def save_settings(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Eroare la salvarea setărilor]: {e}")


# ===================== REZULTATE / STATISTICI =====================
def save_results(result_data):
    os.makedirs(DATA_DIR, exist_ok=True)
    results = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []

    results.append(result_data)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

def load_results():
    if not os.path.exists(RESULTS_FILE):
        return []
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Eroare la citirea rezultatelor]: {e}")
        return []


# ===================== LEADERBOARD LOCAL (Exam only) =====================
LEADERBOARD_PATH = os.path.join(DATA_DIR, "leaderboard.json")

def load_leaderboard():
    """Citește scorurile salvate local din data/leaderboard.json."""
    if not os.path.exists(LEADERBOARD_PATH):
        return []
    try:
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard(data):
    """Salvează lista de scoruri în data/leaderboard.json."""
    os.makedirs(os.path.dirname(LEADERBOARD_PATH), exist_ok=True)
    try:
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Eroare la salvarea leaderboard:", e)
