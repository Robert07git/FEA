# stats_manager.py
import json
import os
from datetime import datetime

STATS_FILE = os.path.join("data", "stats.json")


def load_stats():
    if not os.path.exists(STATS_FILE):
        return []
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_stats(data):
    os.makedirs("data", exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_session(result):
    stats = load_stats()
    result["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    stats.append(result)
    save_stats(stats)
    print(f"[INFO] Sesiune salvată: {result}")


def get_summary(stats):
    if not stats:
        return {"total_sessions": 0, "avg_score": 0, "best_score": 0}
    avg = sum(s["percent"] for s in stats) / len(stats)
    best = max(s["percent"] for s in stats)
    return {"total_sessions": len(stats), "avg_score": round(avg, 2), "best_score": best}


def get_leaderboard(stats, top_n=5):
    return sorted(stats, key=lambda s: s.get("percent", 0), reverse=True)[:top_n]
