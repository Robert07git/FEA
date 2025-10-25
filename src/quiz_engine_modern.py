# quiz_engine_modern.py
"""
Logica pentru FEA Quiz Trainer 3.6 — corectă și sincronizată cu noua interfață
"""

import random
from datetime import datetime


class QuizManagerModern:
    """Gestionează întrebările, scorul, progresul și feedback-ul."""

    def __init__(self, questions, domain="mix", num_questions=None):
        if domain and domain.lower() != "mix":
            questions = [
                q for q in questions
                if q.get("domain", "").lower() == domain.lower()
            ]

        random.shuffle(questions)
        if num_questions is not None and num_questions > 0:
            questions = questions[:num_questions]

        self.questions = questions
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.domain = domain

    # ----------------- INFO -----------------
    def total_questions(self):
        return len(self.questions)

    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    # ----------------- RĂSPUNS -----------------
    def check_answer(self, selected_index: int):
        q = self.questions[self.current_index]
        options = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "")

        is_correct = (selected_index == correct_index)
        correct_text = options[correct_index] if 0 <= correct_index < len(options) else "-"
        user_text = options[selected_index] if 0 <= selected_index < len(options) else "-"

        if is_correct:
            self.score += 1

        self.user_answers.append({
            "question": q.get("question", ""),
            "user_answer": user_text,
            "correct_answer": correct_text,
            "is_correct": is_correct,
            "explanation": explanation
        })

        return is_correct, correct_text, explanation

    # ----------------- PROGRES -----------------
    def advance(self):
        self.current_index += 1
        return self.current_index < len(self.questions)

    # ----------------- STATISTICI -----------------
    def get_result_data(self, mode, time_used):
        total = len(self.questions)
        percent = round((self.score / total) * 100, 2) if total > 0 else 0.0
        correct = self.score
        incorrect = total - correct

        return {
            "mode": mode,
            "domain": self.domain,
            "score": self.score,
            "total": total,
            "percent": percent,
            "time_used": time_used,
            "correct": correct,
            "incorrect": incorrect,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
