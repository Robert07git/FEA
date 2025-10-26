# src/stats_manager.py
import json
import os

class StatsManager:
    def __init__(self, filename="data/stats.json"):
        self.filename = filename
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({"scores": []}, f, indent=4)

    def load(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_score(self, score_entry):
        data = self.load()
        data["scores"].append(score_entry)
        self.save(data)

    def get_leaderboard(self, limit=10):
        data = self.load()["scores"]
        sorted_scores = sorted(data, key=lambda x: x["score"], reverse=True)
        return sorted_scores[:limit]
