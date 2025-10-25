# quiz_engine_modern.py
"""
Logică modernă pentru FEA Quiz Trainer — compatibilă cu structura fea_questions.json.
"""

import random

class QuizManagerModern:
    """Gestionează logica quizului (întrebări, scor, progres)."""

    def __init__(self, questions):
        # amestecăm întrebările pentru diversitate
        self.questions = random.sample(questions, len(questions))
        self.current_index = 0
        self.score = 0

    def total_questions(self):
        """Returnează numărul total de întrebări."""
        return len(self.questions)

    def get_current_question(self):
        """Returnează întrebarea curentă (dict complet) sau None dacă s-a terminat."""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def check_answer(self, selected_index):
        """Verifică dacă răspunsul ales este corect."""
        q = self.questions[self.current_index]

        # accesează cheile specifice structurii tale JSON
        options = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "")

        is_correct = (selected_index == correct_index)
        correct_text = options[correct_index] if 0 <= correct_index < len(options) else "—"

        if is_correct:
            self.score += 1

        return is_correct, correct_text, explanation

    def advance(self):
        """Trece la următoarea întrebare. Returnează False dacă s-a terminat."""
        self.current_index += 1
        return self.current_index < len(self.questions)
