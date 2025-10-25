import random
import time
import threading
import pygame

# Inițializare sunet pentru notificare la 5 secunde
pygame.mixer.init()
try:
    beep_sound = pygame.mixer.Sound("data/beep.wav")
except:
    beep_sound = None


class QuizSession:
    def __init__(self, questions, num_questions=10, mode="train", time_limit_sec=None, update_ui_callback=None):
        """
        Clasa principală pentru gestionarea quizului.

        :param questions: listă de întrebări
        :param num_questions: câte întrebări se aleg
        :param mode: "train" sau "exam"
        :param time_limit_sec: secunde per întrebare (doar pentru exam)
        :param update_ui_callback: funcție pentru actualizarea interfeței
        """
        self.questions = random.sample(questions, min(num_questions, len(questions)))
        self.mode = mode
        self.time_limit = time_limit_sec
        self.current_index = 0
        self.score = 0
        self.results = []
        self.timer_thread = None
        self.time_left = time_limit_sec
        self.timer_running = False
        self.update_ui_callback = update_ui_callback

    def get_current_question(self):
        """Returnează întrebarea curentă."""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def answer_question(self, choice_index):
        """Procesează răspunsul utilizatorului."""
        q = self.get_current_question()
        if not q:
            return False, "Nu mai sunt întrebări."

        is_correct = choice_index == q["correct_index"]
        if is_correct:
            self.score += 1

        self.results.append({
            "idx": self.current_index + 1,
            "question": q["question"],
            "choices": q["choices"],
            "correct_index": q["correct_index"],
            "user_index": choice_index,
            "correct": is_correct,
            "explanation": q.get("explanation", ""),
            "domain": q.get("domain", "n/a"),
        })

        feedback = ""
        if self.mode == "train":
            if is_correct:
                feedback = "✅ Corect!"
            else:
                correct_text = q["choices"][q["correct_index"]]
                feedback = f"❌ Greșit. Corect: {correct_text}\nExplicație: {q.get('explanation', '')}"

        self.current_index += 1
        return is_correct, feedback

    def has_next(self):
        """Verifică dacă există o întrebare următoare."""
        return self.current_index < len(self.questions)

    def start_timer(self):
        """Pornește timerul pentru întrebare (doar în EXAM)."""
        if self.mode != "exam" or not self.time_limit:
            return
        self.time_left = self.time_limit
        self.timer_running = True

        def countdown():
            while self.time_left > 0 and self.timer_running:
                time.sleep(1)
                self.time_left -= 1

                # Redă sunet la ultimele 5 secunde
                if self.time_left == 5 and beep_sound:
                    beep_sound.play()

                if self.update_ui_callback:
                    self.update_ui_callback()

            # Timp expirat
            if self.timer_running and self.time_left <= 0:
                self.timer_running = False
                if self.update_ui_callback:
                    self.update_ui_callback(timeout=True)

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        """Oprește timerul (la trecerea la următoarea întrebare)."""
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=0.1)

    def get_score_summary(self):
        """Returnează rezumatul scorului."""
        total = len(self.questions)
        pct = (self.score / total) * 100 if total > 0 else 0
        return self.score, total, pct
