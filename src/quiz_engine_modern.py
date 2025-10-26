# quiz_engine_modern.py
import random
import datetime
import stats_manager  # 🔁 import direct, fără import ciclic

class QuizEngine:
    """
    Gestionează:
    - selecția întrebărilor
    - scorul
    - salvarea rezultatelor
    """

    def __init__(self, data, username="User", domain="mix", num_questions=10, mode="Train"):
        # Filtrare domeniu dacă nu e "mix"
        if domain != "mix":
            data = [q for q in data if q.get("domain", "").lower() == domain.lower()]

        # Alege random întrebările
        self.questions = random.sample(data, min(num_questions, len(data)))
        self.current_index = 0
        self.score = 0
        self.user_answers = []  # pentru feedback + PDF
        self.username = username
        self.domain = domain
        self.mode = mode
        self.start_time = datetime.datetime.now()

    # =======================
    # 🔹 Navigare întrebări
    # =======================
    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def total_questions(self):
        return len(self.questions)

    def advance(self):
        self.current_index += 1
        return self.current_index < len(self.questions)

    # =======================
    # 🔹 Verificare răspuns
    # =======================
    def check_answer(self, idx):
        """
        idx = indexul opțiunii alese de user în lista de choices
        returnează (is_correct, correct_text, explanation)
        """
        q = self.questions[self.current_index]
        selected_text = q["choices"][idx]
        correct_text = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "Nicio explicație disponibilă.")
        is_correct = (selected_text == correct_text)

        if is_correct:
            self.score += 1

        # Salvăm pentru feedback și PDF
        self.user_answers.append({
            "question": q["question"],
            "selected": selected_text,
            "correct": correct_text,
            "is_correct": is_correct,
            "explanation": explanation
        })

        return is_correct, correct_text, explanation

    # =======================
    # 🔹 Finalizare quiz
    # =======================
    def get_result_data(self, time_used=None):
        total = len(self.questions)
        percent = round((self.score / total) * 100, 1) if total else 0
        end_time = datetime.datetime.now()
        time_spent = str(time_used) if time_used else str(end_time - self.start_time)

        result = {
            "username": self.username,
            "domain": self.domain,
            "mode": self.mode,
            "score": self.score,
            "total": total,
            "percent": percent,
            "time_spent": time_spent,
            "date": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Salvăm rezultatul și în leaderboard
        try:
            stats_manager.save_quiz_result(self.username, self.domain, self.score, total, self.mode)
        except Exception as e:
            print(f"[WARN] Nu s-a putut salva scorul: {e}")

        return result

    # =======================
    # 🔹 Reset
    # =======================
    def reset(self):
        """Resetează quiz-ul pentru o nouă sesiune"""
        self.current_index = 0
        self.score = 0
        self.user_answers.clear()
        self.start_time = datetime.datetime.now()
