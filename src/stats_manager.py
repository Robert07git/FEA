import json
import os
from datetime import datetime

# ==========================
# 🔧 Setări fișiere
# ==========================
DATA_DIR = "data"
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")

# ==========================
# 🗂 Funcții pentru fișiere
# ==========================
def ensure_data_folder():
    """Creează folderul /data dacă nu există"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def safe_read_json(path):
    """Încărcare JSON în siguranță"""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def safe_write_json(path, data):
    """Scriere JSON în siguranță"""
    ensure_data_folder()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==========================
# 💾 Salvare rezultate quiz
# ==========================
def save_quiz_result(username, domain, score, total, mode):
    """
    Salvează rezultatul unui quiz în stats.json și actualizează leaderboard-ul.
    """
    ensure_data_folder()
    data = safe_read_json(STATS_FILE)

    percent = round((score / total) * 100, 1) if total else 0
    entry = {
        "username": username,
        "domain": domain,
        "mode": mode,
        "score": score,
        "total": total,
        "percent": percent,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    data.append(entry)
    safe_write_json(STATS_FILE, data)

    # actualizare leaderboard
    update_leaderboard(username, domain, percent)
    return entry

# ==========================
# 📊 Încărcare statistici
# ==========================
def load_stats():
    """
    Returnează toate sesiunile salvate din stats.json.
    """
    return safe_read_json(STATS_FILE)

# ==========================
# 🏆 Leaderboard global
# ==========================
def update_leaderboard(username, domain, percent):
    """
    Actualizează leaderboard-ul global cu cel mai bun scor al fiecărui user.
    """
    ensure_data_folder()
    leaderboard = safe_read_json(LEADERBOARD_FILE)

    # caută dacă userul există deja
    existing = next((x for x in leaderboard if x["username"] == username and x["domain"] == domain), None)
    if existing:
        if percent > existing["score"]:
            existing["score"] = percent
    else:
        leaderboard.append({
            "username": username,
            "domain": domain,
            "score": percent
        })

    # sortează descrescător și păstrează top 10
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
    safe_write_json(LEADERBOARD_FILE, leaderboard)

# ==========================
# 📈 Citire leaderboard
# ==========================
def load_leaderboard():
    """
    Returnează lista cu top 10 scoruri globale.
    """
    return safe_read_json(LEADERBOARD_FILE)

# ==========================
# 🧹 Resetare date
# ==========================
def clear_stats():
    """Șterge toate rezultatele din stats.json"""
    safe_write_json(STATS_FILE, [])
    print("[INFO] Stats resetat.")

def clear_leaderboard():
    """Șterge toate datele din leaderboard.json"""
    safe_write_json(LEADERBOARD_FILE, [])
    print("[INFO] Leaderboard resetat.")
