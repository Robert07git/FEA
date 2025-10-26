import json
import os
import random

# ================================================================
#  DATA LOADER - Moment 2 (versiune completă cu Leaderboard Local)
# ================================================================

# === 1. ÎNCĂRCARE ÎNTREBĂRI QUIZ ===
def load_questions():
    """
    Încarcă întrebările din fișierul fea_questions.json
    Returnează o listă de dicționare.
    """
    path = os.path.join("data", "fea_questions.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                # uneori fișierul poate conține un singur domeniu, transformăm în listă
                questions = []
                for domain, qlist in data.items():
                    for q in qlist:
                        q["domain"] = domain
                        questions.append(q)
                return questions
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        print("[WARN] Nu s-au putut încărca întrebările.")
        return []


# === 2. SELECTARE ALEATORIE DE ÎNTREBĂRI ===
def get_random_questions(domain="mix", count=10):
    """
    Returnează un set de întrebări aleatorii din domeniul ales.
    """
    all_questions = load_questions()
    if not all_questions:
        return []

    if domain.lower() != "mix":
        filtered = [q for q in all_questions if q.get("domain", "").lower() == domain.lower()]
    else:
        filtered = all_questions

    random.shuffle(filtered)
    return filtered[:count]


# === 3. GESTIONARE STATISTICI (Moment 1 - neschimbat) ===
def load_stats():
    path = os.path.join("data", "results.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_stats(data):
    path = os.path.join("data", "results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_session(result):
    """
    Adaugă o nouă sesiune în istoricul general (train/exam).
    """
    stats = load_stats()
    stats.append(result)
    save_stats(stats)


# === 4. LEADERBOARD LOCAL (Moment 2 nou) ===
def load_leaderboard():
    """
    Încarcă leaderboard-ul local.
    Creează automat fișierul dacă lipsește sau este invalid.
    """
    path = os.path.join("data", "leaderboard.json")

    # Dacă nu există folderul data, îl creăm
    os.makedirs("data", exist_ok=True)

    # Dacă fișierul nu există, îl creăm cu o listă goală
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        return []

    # Citire sigură
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):  # dacă e dict în loc de listă, resetăm
                data = []
    except json.JSONDecodeError:
        data = []

    return data


def save_leaderboard(data):
    """
    Salvează leaderboard-ul local în fișierul JSON.
    Se asigură că fișierul este o listă validă.
    """
    path = os.path.join("data", "leaderboard.json")
    os.makedirs("data", exist_ok=True)

    if not isinstance(data, list):
        data = []

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
