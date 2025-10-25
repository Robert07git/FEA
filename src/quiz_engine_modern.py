# quiz_engine_modern.py
"""
Logică modernă pentru FEA Quiz Trainer — compatibilă cu structura fea_questions.json,
cu suport pentru:
- filtrare pe domeniu
- limitare număr întrebări
- colectare răspunsuri utilizator pentru feedback la final (Exam Mode)
"""

import random


class QuizManagerModern:
    """Gestionează logica quizului (întrebări, scor, progres)."""

    def __init__(self, questions, domain="mix", num_questions=None):
        """
        questions: list[dict] fiecare dict trebuie să aibă cheile:
           "question": str
           "choices": list[str]
           "correct_index": int
           "explanation": str (optional)
           "domain": str (ex: "structural", "crash", etc.)
        domain: str - "mix" sau un nume de domeniu
        num_questions: int sau None
        """

        # 1. Filtrăm întrebările după domeniu, dacă nu e 'mix'
        if domain and domain.lower() != "mix":
            questions = [
                q for q in questions
                if q.get("domain", "").lower() == domain.lower()
            ]

        # 2. Amestecăm ordinea întrebărilor
        random.shuffle(questions)

        # 3. Limităm numărul de întrebări
        if num_questions is not None and num_questions > 0:
            questions = questions[:num_questions]

        self.questions = questions
        self.current_index = 0
        self.score = 0

        # pentru analiză la final (mai ales în Exam Mode)
        self.user_answers = []  # list[ {question, user_answer, correct_answer, is_correct, explanation} ]

    # ------------------ info despre progres ------------------

    def total_questions(self):
        """Returnează numărul total de întrebări din sesiune."""
        return len(self.questions)

    def get_current_question(self):
        """Returnează întrebarea curentă (dict) sau None dacă nu mai sunt întrebări."""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    # ------------------ răspunsuri ------------------

    def check_answer(self, selected_index: int):
        """
        Verifică răspunsul utilizatorului.
        Returnează (is_correct, correct_text, explanation).
        Înregistrează răspunsul pentru raportul final.
        """
        q = self.questions[self.current_index]

        options = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "")

        is_correct = (selected_index == correct_index)

        # Textul răspunsului corect
        if 0 <= correct_index < len(options):
            correct_text = options[correct_index]
        else:
            correct_text = "—"

        # Textul răspunsului dat de utilizator
        if 0 <= selected_index < len(options):
            user_text = options[selected_index]
        else:
            user_text = "—"

        # Scor
        if is_correct:
            self.score += 1

        # Salvăm pentru feedback final (Exam Mode)
        self.user_answers.append({
            "question": q.get("question", ""),
            "user_answer": user_text,
            "correct_answer": correct_text,
            "is_correct": is_correct,
            "explanation": explanation
        })

        return is_correct, correct_text, explanation

    # ------------------ avans ------------------

    def advance(self):
        """
        Treci la următoarea întrebare.
        Returnează True dacă mai sunt întrebări după avans, altfel False.
        """
        self.current_index += 1
        return self.current_index < len(self.questions)
