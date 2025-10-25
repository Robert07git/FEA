# stats_manager.py
"""
Gestionare statistici și leaderboard pentru FEA Quiz Trainer.
Folosește un fișier local data/stats.json
"""

import json
import os
from datetime import datetime

DATA_PATH = os.path.join("data", "stats.json")


def load_stats():
    """Întoarce lista tuturor sesiunilor salvate până acum."""
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_stats(stats):
    """Salvează lista completă de sesiuni în stats.json."""
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)


def add_session(result_data):
    """
    Adaugă o nouă sesiune la stats.json.
    result_data trebuie să conțină cel puțin:
    {
        "mode", "domain", "score", "total",
        "percent", "time_used", "correct", "incorrect"
    }
    """
    stats = load_stats()
    result_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    stats.append(result_data)
    save_stats(stats)


def get_summary(stats):
    """
    Calculează statistici globale:
    - media scorurilor în %
    - numărul total de sesiuni
    - cel mai bun scor (%)
    """
    if not stats:
        return {
            "avg_score": 0,
            "total_sessions": 0,
            "best_score": 0,
        }

    scores = [entry["percent"] for entry in stats]
    avg = sum(scores) / len(scores)
    best = max(scores)

    return {
        "avg_score": round(avg, 1),
        "total_sessions": len(stats),
        "best_score": round(best, 1),
    }


def get_leaderboard(stats, top_n=5):
    """
    Returnează top N rezultate după procentaj.
    Fiecare element conține domain, percent, mode, date etc.
    """
    sorted_stats = sorted(stats, key=lambda s: s["percent"], reverse=True)
    return sorted_stats[:top_n]
