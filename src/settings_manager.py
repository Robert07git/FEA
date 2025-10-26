import json
import os
from datetime import datetime

# Calea spre fișierul de statistici
STATS_FILE = os.path.join("data", "stats.json")
LEADERBOARD_FILE = os.path.join("data", "leaderboard.json")

# ===========================
# 📊 Funcții pentru statistici
# ===========================

def load_stats():
    """Încarcă toate statisticile salvate"""
    if not os.path.exists(STATS_FILE):
        return []
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_stats(stats):
    """Salvează lista completă de statistici"""
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

def save_quiz_result(username, domain, score, total, mode):
    """Salvează rezultatul utilizatorului curent"""
    stats = load_stats()
    entry = {
        "username": username,
        "domain": domain,
        "score": score,
        "total": total,
        "mode": mode,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    stats.append(entry)
    save_stats(stats)
    update_leaderboard(username, score, total)
    return entry

# =====================================
# 🏆 Funcții pentru Leaderboard global
# =====================================

def load_leaderboard():
    """Încarcă leaderboard-ul global"""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_leaderboard(data):
    """Salvează leaderboard-ul"""
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def update_leaderboard(username, score, total):
    """Actualizează leaderboard-ul global"""
    leaderboard = load_leaderboard()
    percent = round((score / total) * 100, 1) if total else 0

    # Verifică dacă utilizatorul există deja
    existing = next((p for p in leaderboard if p["username"] == username), None)
    if existing:
        # Actualizează doar dacă noul scor e mai bun
        if percent > existing["percent"]:
            existing.update({
                "score": score,
                "total": total,
                "percent": percent,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    else:
        leaderboard.append({
            "username": username,
            "score": score,
            "total": total,
            "percent": percent,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Sortează descrescător după procentaj
    leaderboard.sort(key=lambda x: x["percent"], reverse=True)
    save_leaderboard(leaderboard)

# ===========================
# 📈 Funcții pentru statistici
# ===========================

def get_user_stats(username):
    """Returnează statisticile filtrate pentru un utilizator"""
    stats = load_stats()
    return [s for s in stats if s["username"] == username]

def get_global_average():
    """Returnează media scorurilor pentru toți utilizatorii"""
    stats = load_stats()
    if not stats:
        return 0
    total_scores = sum((s["score"] / s["total"]) for s in stats if s["total"] > 0)
    return round((total_scores / len(stats)) * 100, 1)

def reset_all_stats():
    """Resetează complet statisticile și leaderboard-ul"""
    if os.path.exists(STATS_FILE):
        os.remove(STATS_FILE)
    if os.path.exists(LEADERBOARD_FILE):
        os.remove(LEADERBOARD_FILE)
