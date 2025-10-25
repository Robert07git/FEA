# stats_manager.py
"""
Gestionează statistici și leaderboard pentru FEA Quiz Trainer
"""

import json
import os
from datetime import datetime

STATS_FILE = os.path.join("data", "stats.json")


def load_stats():
    """Încarcă statisticile din fișierul JSON."""
    if not os.path.exists(STATS_FILE):
        return []
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_stats(data):
    """Salvează toate sesiunile în fișier."""
    os.makedirs("data", exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_session(result_data):
    """Adaugă o nouă sesiune la statistici."""
    stats = load_stats()
    result_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    stats.append(result_data)
    save_stats(stats)
    print(f"[INFO] Sesiune salvată: {result_data}")  # debug log


def get_summary(stats):
    """Returnează un sumar cu media, totalul și cel mai bun scor."""
    if not stats:
        return {"total_sessions": 0, "avg_score": 0, "best_score": 0}

    avg = sum(s["percent"] for s in stats) / len(stats)
    best = max(s["percent"] for s in stats)
    return {
        "total_sessions": len(stats),
        "avg_score": round(avg, 2),
        "best_score": round(best, 2),
    }


def get_leaderboard(stats, top_n=5):
    """Returnează topul celor mai bune scoruri."""
    sorted_stats = sorted(stats, key=lambda s: s.get("percent", 0), reverse=True)
    return sorted_stats[:top_n]
