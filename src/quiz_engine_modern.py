import json
import os
import random
from datetime import datetime
from stats_manager import LeaderboardManager  # 🏆 nou

class QuizEngine:
    def __init__(self, data_path="data/questions.json"):
        self.data_path = data_path
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.mode = "train"
        self.domain = "General"
        self.username = "User"

        self.load_questions()

    # =============================================================
    # 🧩 LOAD QUESTIONS
    # =============================================================
    def load_questions(self):
        """Încarcă întrebările din fișierul JSON."""
        if not os.path.exists(self.data_path):
            print(f"[Eroare] Fișierul de întrebări nu există: {self.data_path}")
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                self.questions = data.get("questions", [])
            except json.JSONDecodeError:
                print("[Eroare] Format JSON invalid în fișierul de întrebări.")

    # =============================================================
    # 🧠 QUIZ LOGIC
    # =============================================================
    def start_quiz(self, mode="train", domain="General", username="User"):
        self.mode = mode
        self.domain = domain
        self.username = username
        self.score = 0
        self.current_index = 0
        random.shuffle(self.questions)

    def get_current_question(self):
        """Returnează întrebarea curentă."""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def answer_question(self, user_answer):
        """Verifică răspunsul utilizatorului și actualizează scorul."""
        question = self.get_current_question()
        if not question:
            return False

        correct = question.get("correct")
        if user_answer == correct:
            self.score += 1
            result = True
        else:
            result = False

        self.current_index += 1
        return result

    def has_next_question(self):
        """Verifică dacă mai sunt întrebări disponibile."""
        return self.current_index < len(self.questions)

    def get_progress(self):
        """Returnează progresul curent (curent / total)."""
        total = len(self.questions)
        return self.current_index, total

    # =============================================================
    # 🏁 RESULTS
    # =============================================================
    def get_results(self):
        """Returnează rezultatele finale."""
        total = len(self.questions)
        score_percent = round((self.score / total) * 100, 2) if total > 0 else 0
        return {
            "name": self.username,
            "domain": self.domain,
            "mode": self.mode,
            "score": score_percent,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    # =============================================================
    # 🏆 SAVE TO LEADERBOARD
    # =============================================================
    def save_to_leaderboard(self):
        """Salvează rezultatul final în leaderboard.json."""
        result = self.get_results()
        leaderboard = LeaderboardManager()
        leaderboard.add_score(result)
        print(f"[INFO] Scorul a fost salvat în leaderboard: {result}")
