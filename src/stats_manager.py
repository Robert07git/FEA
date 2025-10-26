import json
import os
from datetime import datetime

STATS_FILE = "data/stats.json"

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"leaderboard": []}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

def add_score(username, domain, score, total_questions, time_spent):
    stats = load_stats()
    new_entry = {
        "username": username,
        "domain": domain,
        "score": round(score, 2),
        "questions": total_questions,
        "time": round(time_spent, 1),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    stats["leaderboard"].append(new_entry)
    # Sortăm descrescător după scor și păstrăm doar primele 10
    stats["leaderboard"] = sorted(stats["leaderboard"], key=lambda x: x["score"], reverse=True)[:10]
    save_stats(stats)

def get_leaderboard():
    stats = load_stats()
    return stats.get("leaderboard", [])
