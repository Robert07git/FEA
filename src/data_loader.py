import json
import os
import random

# ================================================================
#  DATA LOADER - Moment 2.2  (bază Moment 1 + Leaderboard Local)
# ================================================================


# === 0. Detectare automată a folderului data ===
def get_data_dir():
    """Determină calea absolută către folderul 'data' indiferent de locul de rulare."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# === 1. Încărcare întrebări ===
def load_questions():
    """Încarcă întrebările din fea_questions.json."""
    path = os.path.join(get_data_dir(), "fea_questions.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
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


# === 2. Selectare aleatorie de întrebări ===
def get_random_questions(domain="mix", count=10):
    all_questions = load_questions()
    if not all_questions:
        return []

    if domain.lower() != "mix":
        filtered = [q for q in all_questions if q.get("domain", "").lower() == domain.lower()]
    else:
        filtered = all_questions

    random.shuffle(filtered)
    return filtered[:count]


# === 3. Gestionare statistici (Moment 1) ===
def load_stats():
    path = os.path.join(get_data_dir(), "results.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_stats(data):
    path = os.path.join(get_data_dir(), "results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_session(result):
    stats = load_stats()
    stats.append(result)
    save_stats(stats)


# === 4. Leaderboard Local (Moment 2.2) ===
def load_leaderboard():
    """
    Încarcă leaderboard-ul local.
    Creează automat fișierul dacă lipsește sau este invalid.
    """
    path = os.path.join(get_data_dir(), "leaderboard.json")

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                print("[WARN] Leaderboard invalid, resetat.")
                data = []
    except json.JSONDecodeError:
        data = []

    return data


def save_leaderboard(data):
    """
    Salvează leaderboard-ul local în fișierul JSON.
    Detectează automat calea corectă și repară fișierul dacă e invalid.
    """
    path = os.path.join(get_data_dir(), "leaderboard.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not isinstance(data, list):
        data = []

    print(f"[DEBUG] Leaderboard salvat în: {os.path.abspath(path)}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
