# quiz_engine_modern.py
import random
from datetime import datetime


class QuizManagerModern:
    """Gestionează întrebările, scorul și logica testului."""

    def __init__(self, questions, domain="mix", num_questions=None):
        if domain.lower() != "mix":
            questions = [
                q for q in questions if q.get("domain", "").lower() == domain.lower()
            ]
        random.shuffle(questions)
        if num_questions:
            questions = questions[:num_questions]

        self.questions = questions
        self.current_index = 0
        self.score = 0
        self.domain = domain
        self.user_answers = []

    def total_questions(self):
        return len(self.questions)

    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def check_answer(self, selected_index):
        q = self.questions[self.current_index]
        choices = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "")

        correct = (selected_index == correct_index)
        if correct:
            self.score += 1

        self.user_answers.append({
            "question": q["question"],
            "selected": choices[selected_index],
            "correct": choices[correct_index],
            "is_correct": correct,
            "explanation": explanation,
        })

        return correct, choices[correct_index], explanation

    def advance(self):
        self.current_index += 1
        return self.current_index < len(self.questions)

    def get_result_data(self, mode, time_used):
        total = len(self.questions)
        percent = round((self.score / total) * 100, 2) if total else 0
        incorrect = total - self.score
        return {
            "mode": mode,
            "domain": self.domain,
            "score": self.score,
            "total": total,
            "percent": percent,
            "time_used": time_used,
            "correct": self.score,
            "incorrect": incorrect,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
