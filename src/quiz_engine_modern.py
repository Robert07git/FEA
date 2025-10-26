# quiz_engine_modern.py
import random
import datetime

class QuizManagerModern:
    """
    Gestionează:
    - selecția întrebărilor
    - scorul
    - istoricul răspunsurilor (pt feedback și PDF)
    """

    def __init__(self, data, domain="mix", num_questions=10):
        # filtrează pe domeniu dacă nu e "mix"
        if domain != "mix":
            data = [q for q in data if q.get("domain", "").lower() == domain.lower()]

        # alege random întrebările
        self.questions = random.sample(data, min(num_questions, len(data)))

        self.current_index = 0
        self.score = 0
        self.user_answers = []  # pentru feedback final + PDF

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
        """
        idx = indexul opțiunii alese de user în lista de choices
        returnează (is_correct, correct_text, explanation)
        """
        q = self.questions[self.current_index]

        # structura întrebare:
        # {
        #  "domain": "structural",
        #  "question": "...",
        #  "choices": ["a","b","c","d"],
        #  "correct_index": 2,
        #  "explanation": "..."
        # }

        selected_text = q["choices"][idx]
        correct_text = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "Nicio explicație disponibilă.")
        is_correct = (selected_text == correct_text)

        if is_correct:
            self.score += 1

        # salvăm pentru feedback final
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

        return {
            "mode": mode,
            "domain": domain_used,
            "score": self.score,
            "total": total,
            "percent": percent,
            "time_used": time_used,
            "correct": self.score,
            "incorrect": total - self.score,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
