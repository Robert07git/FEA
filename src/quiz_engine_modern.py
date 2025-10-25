# quiz_engine_modern.py
"""
Logică simplificată pentru noul UI modern (CustomTkinter).
Nu afectează versiunea veche a aplicației.
"""

import random


class QuizManagerModern:
    """Gestionează quizul: întrebări, scor, progres."""

    def __init__(self, questions):
        # questions = listă dicturi de forma:
        # {
        #   "question": "...",
        #   "options": ["a", "b", "c", "d"],
        #   "answer_index": 1,
        #   "explanation": "de ce",
        #   ...
        # }

        # amestecăm ordinea întrebărilor ca să nu fie mereu la fel
        self.questions = random.sample(questions, len(questions))
        self.score = 0
        self.current_index = 0

    def total_questions(self):
        return len(self.questions)

    def get_current_question(self):
        """Returnează întrebarea curentă ca dict, sau None dacă nu mai sunt."""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def check_answer(self, selected_index):
        """
        Verifică dacă răspunsul ales e corect.
        Returnează (is_correct, correct_text, explanation)
        """
        q = self.questions[self.current_index]
        is_correct = (selected_index == q["answer_index"])
        correct_text = q["options"][q["answer_index"]]

        explanation = q.get("explanation", "")

        if is_correct:
            self.score += 1

        return is_correct, correct_text, explanation

    def advance(self):
        """
        Merge la următoarea întrebare.
        Returnează True dacă mai sunt întrebări după asta,
        False dacă am ajuns la final.
        """
        self.current_index += 1
        return self.current_index < len(self.questions)
