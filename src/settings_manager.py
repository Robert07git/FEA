import json
import os
from datetime import datetime

STATS_FILE = os.path.join("data", "stats.json")

def load_stats():
    if not os.path.exists(STATS_FILE):
        return []
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats(stats):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

def save_quiz_result(username, domain, score, total, mode):
    """Salvează rezultatul utilizatorului în stats.json"""
    stats = load_stats()
    stats.append({
        "username": username,
        "domain": domain,
        "score": score,
        "total": total,
        "mode": mode,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_stats(stats)
