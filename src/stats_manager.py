import json
import os

class StatsManager:
    """Gestionarea statisticilor generale."""

    def __init__(self, stats_path="data/stats.json"):
        self.stats_path = stats_path
        self.ensure_file()

    # =============================================================
    # 🧩 INITIALIZARE FIȘIER
    # =============================================================
    def ensure_file(self):
        """Creează fișierul de statistici dacă nu există."""
        if not os.path.exists(self.stats_path):
            with open(self.stats_path, "w", encoding="utf-8") as f:
                json.dump({"sessions": []}, f, indent=4, ensure_ascii=False)

    # =============================================================
    # 🧾 ADAUGARE SESIUNE
    # =============================================================
    def add_score(self, session_data):
        """Adaugă o sesiune nouă în istoricul de statistici."""
        with open(self.stats_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["sessions"].append(session_data)

        with open(self.stats_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # =============================================================
    # 📊 REZUMAT
    # =============================================================
    def get_summary(self):
        """Returnează un sumar al testelor (număr total și medie scoruri)."""
        with open(self.stats_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sessions = data.get("sessions", [])
        if not sessions:
            return {"tests": 0, "avg_score": 0.0}

        avg_score = sum(s["score"] for s in sessions) / len(sessions)
        return {"tests": len(sessions), "avg_score": round(avg_score, 2)}

# =============================================================
# 🏆 LEADERBOARD LOCAL (NOU)
# =============================================================
class LeaderboardManager:
    """Gestionează scorurile locale în leaderboard.json."""

    def __init__(self, file_path="data/leaderboard.json"):
        self.file_path = file_path
        self.ensure_file()

    def ensure_file(self):
        """Creează fișierul leaderboard.json dacă lipsește."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"scores": []}, f, indent=4, ensure_ascii=False)

    def add_score(self, entry):
        """Adaugă un scor nou și păstrează doar top 10."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["scores"].append(entry)
        data["scores"] = sorted(data["scores"], key=lambda x: x["score"], reverse=True)[:10]

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_top_scores(self):
        """Returnează lista top 10 scoruri."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("scores", [])

    def clear_leaderboard(self):
        """Șterge toate scorurile."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump({"scores": []}, f, indent=4, ensure_ascii=False)
