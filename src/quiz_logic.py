import time
from data_loader import save_result


class QuizSession:
    def __init__(self, app, questions, mode="train", time_limit=None):
        self.app = app
        self.questions = questions
        self.mode = mode
        self.time_limit = time_limit
        self.index = 0
        self.correct_count = 0
        self.start_time = None
        self.results = []
        self.timer_running = False
        self.timer_job = None

    # ===================== PORNIRE QUIZ =====================
    def run(self):
        self.start_time = time.time()
        self.index = 0
        self.correct_count = 0
        self.results = []
        self.show_question()

    def current_question(self):
        if 0 <= self.index < len(self.questions):
            return self.questions[self.index]
        return None

    # ===================== AFIȘARE ÎNTREBARE =====================
    def show_question(self):
        question = self.current_question()
        if question:
            # Resetăm orice timer vechi
            self.stop_timer()
            if self.mode == "exam" and self.time_limit:
                self.timer_running = True
                self.app.start_timer(self.time_limit)
            self.app.show_question()
        else:
            self.end_quiz()

    # ===================== OPRIRE TIMER =====================
    def stop_timer(self):
        """Oprește timerul activ, dacă există."""
        self.timer_running = False
        if self.timer_job:
            try:
                self.app.root.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

    # ===================== RĂSPUNS =====================
    def answer(self, choice_index):
        question = self.current_question()
        if not question:
            return

        correct = (choice_index == question["correct_index"])
        self.results.append({
            "question": question["question"],
            "choices": question["choices"],
            "correct_index": question["correct_index"],
            "user_answer": choice_index,
            "correct": correct,
            "explanation": question.get("explanation", "")
        })

        if correct:
            self.correct_count += 1

        # ================== MOD TRAIN ==================
        if self.mode == "train":
            correct_text = question["choices"][question["correct_index"]]
            expl = question.get("explanation", "")
            if correct:
                msg = f"✅ Corect!\n\nExplicație: {expl}"
            else:
                msg = f"❌ Greșit!\n\nRăspuns corect: {correct_text}\nExplicație: {expl}"
            self.app.show_train_feedback(correct, msg)
        else:
            self.next_question()

    # ===================== URMĂTOAREA ÎNTREBARE =====================
    def next_question(self):
        self.stop_timer()
        self.index += 1
        if self.index < len(self.questions):
            self.show_question()
        else:
            self.end_quiz()

    # ===================== FINAL QUIZ =====================
    def end_quiz(self):
        self.stop_timer()
        duration = time.time() - self.start_time if self.start_time else 0
        total = len(self.questions)
        pct = (self.correct_count / total) * 100 if total > 0 else 0

        save_result({
            "mod": self.mode,
            "domeniu": self.questions[0].get("domain", "necunoscut"),
            "scor": self.correct_count,
            "total": total,
            "procent": pct,
            "timp_total": round(duration, 1),
            "timp_intrebare": self.time_limit if self.time_limit else "n/a"
        })

        # ✅ doar un singur apel, fără duplicare
        if self.mode == "exam":
            self.app.show_exam_summary(self.results, self.correct_count, total, pct, duration)
        else:
            self.app.show_main_menu()
