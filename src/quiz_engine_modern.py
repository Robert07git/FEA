# quiz_engine_modern.py
"""
Logică modernă pentru FEA Quiz Trainer — compatibilă cu structura fea_questions.json,
cu suport pentru filtrare pe domenii și feedback de final.
"""

import random


class QuizManagerModern:
    """Gestionează logica quizului (întrebări, scor, progres)."""

    def __init__(self, questions, domain="mix", num_questions=None):
        # Filtrăm întrebările după domeniu
        if domain.lower() != "mix":
            questions = [q for q in questions if q.get("domain", "").lower() == domain.lower()]

        # Amestecăm și limităm numărul de întrebări
        random.shuffle(questions)
        if num_questions:
            questions = questions[:num_questions]

        self.questions = questions
        self.current_index = 0
        self.score = 0
        self.user_answers = []

    def total_questions(self):
        return len(self.questions)

    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def check_answer(self, selected_index):
        """Verifică răspunsul și salvează pentru feedback final."""
        q = self.questions[self.current_index]
        options = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "")
        is_correct = (selected_index == correct_index)

        correct_text = options[correct_index] if 0 <= correct_index < len(options) else "—"
        user_text = options[selected_index] if 0 <= selected_index < len(options) else "—"

        # Salvăm pentru feedback la final
        self.user_answers.append({
            "question": q["question"],
            "user_answer": user_text,
            "correct_answer": correct_text,
            "is_correct": is_correct,
            "explanation": explanation
        })

        if is_correct:
            self.score += 1

        return is_correct, correct_text, explanation

    def advance(self):
        self.current_index += 1
        return self.current_index < len(self.questions)
