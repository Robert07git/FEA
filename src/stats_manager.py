import json
import os
from datetime import datetime


# ==========================================================
#  📊 StatsManager (original din Moment 0)
# ==========================================================

class StatsManager:
    def __init__(self, filepath="data/stats.json"):
        self.filepath = filepath
        self.data = self.load_stats()

    def load_stats(self):
        """Încarcă statisticile salvate din fișier."""
        if not os.path.exists(self.filepath):
            return {"sessions": 0, "scores": []}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"sessions": 0, "scores": []}

    def save_stats(self):
        """Salvează statisticile în fișier."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Eroare la salvarea statisticilor: {e}")

    def add_score(self, score):
        """Adaugă un nou scor la statistici."""
        self.data["sessions"] += 1
        self.data["scores"].append(score)
        self.save_stats()

    def get_average(self):
        """Returnează media scorurilor."""
        scores = self.data.get("scores", [])
        if not scores:
            return 0
        return sum(scores) / len(scores)

    def get_best_score(self):
        """Returnează cel mai mare scor."""
        scores = self.data.get("scores", [])
        if not scores:
            return 0
        return max(scores)


# ==========================================================
#  🏆 LeaderboardManager (nou adăugat — FEA Trainer 6.0)
# ==========================================================

class LeaderboardManager:
    """
    Gestionează scorurile locale din fișierul leaderboard.json.
    Păstrează top 10 scoruri (descrescător) și asigură salvarea persistentă.
    """

    def __init__(self, filepath="data/leaderboard.json"):
        self.filepath = filepath
        self.max_entries = 10
        self.data = self.load_leaderboard()

    # ----------------------------------------------------------
    def load_leaderboard(self):
        """Încarcă leaderboard-ul din fișierul JSON."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Eroare la citirea leaderboard-ului: {e}")
            return []

    # ----------------------------------------------------------
    def save_leaderboard(self):
        """Salvează leaderboard-ul în fișierul JSON."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Eroare la salvarea leaderboard-ului: {e}")

    # ----------------------------------------------------------
    def add_score(self, name, mode, domain, score):
        """
        Adaugă un scor nou și actualizează leaderboard-ul.
        name: numele utilizatorului (string)
        mode: mod quiz ("train" / "exam")
        domain: domeniul testului (string)
        score: scor numeric (float)
        """
        entry = {
            "name": name if name else "Anonim",
            "mode": mode,
            "domain": domain,
            "score": round(score, 1),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.data.append(entry)
        # Sortare descrescătoare după scor
        self.data = sorted(self.data, key=lambda x: x["score"], reverse=True)
        # Limităm la top 10
        self.data = self.data[:self.max_entries]
        # Salvăm modificările
        self.save_leaderboard()

    # ----------------------------------------------------------
    def get_top_scores(self):
        """Returnează lista celor mai bune scoruri."""
        return self.data

    # ----------------------------------------------------------
    def clear_leaderboard(self):
        """Șterge toate scorurile salvate."""
        self.data = []
        self.save_leaderboard()
