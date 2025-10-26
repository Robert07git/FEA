# src/quiz_engine_modern.py
import random
import datetime
from src.stats_manager import StatsManager
from src.settings_manager import SettingsManager

class QuizManagerModern:
    """
    Gestionează:
    - selecția întrebărilor
    - scorul
    - istoricul răspunsurilor
    - leaderboard (prin StatsManager)
    - setările utilizatorului
    """

    def __init__(self, data, domain="mix", num_questions=10):
        settings = SettingsManager()
        num_questions = settings.get("num_questions")

        if domain != "mix":
            data = [q for q in data if q.get("domain", "").lower() == domain.lower()]

        self.questions = random.sample(data, min(num_questions, len(data)))
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.username = settings.get("username")

    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def total_questions(self):
        return len(self.questions)

    def advance(self):
        self.current_index += 1
        return self.current_index < len(self.questions)

    def check_answer(self, idx):
        q = self.questions[self.current_index]
        selected_text = q["choices"][idx]
        correct_text = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "Nicio explicație disponibilă.")
        is_correct = (selected_text == correct_text)

        if is_correct:
            self.score += 1

        self.user_answers.append({
            "question": q["question"],
            "selected": selected_text,
            "correct": correct_text,
            "explanation": explanation
        })

        return is_correct, correct_text, explanation

    def get_result_data(self, mode, time_used):
        total = len(self.questions)
        percent = round((self.score / total) * 100, 1) if total else 0
        domain_used = "mix" if not self.questions else self.questions[0].get("domain", "mix")

        # salvează scorul global
        StatsManager().add_score({
            "username": self.username or "Anonim",
            "score": percent,
            "mode": mode,
            "domain": domain_used,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        return {
            "mode": mode,
            "score": self.score,
            "total": total,
            "percent": percent,
            "domain": domain_used,
            "answers": self.user_answers,
            "time_used": time_used
        }
