import random
import time


class QuizSession:
    def __init__(self, app, questions, mode="train", time_limit=None):
        self.app = app
        self.questions = random.sample(questions, len(questions))
        self.mode = mode
        self.time_limit = time_limit
        self.index = 0
        self.score = 0
        self.results = []
        self.start_time = time.time()
        self.running = True

    def current_question(self):
        if self.index < len(self.questions):
            return self.questions[self.index]
        return None

    def answer(self, selected_index):
        """Procesează răspunsul utilizatorului."""
        question = self.questions[self.index]
        correct = selected_index == question["correct_index"]

        # Salvează rezultatul pentru raport
        self.results.append({
            "idx": self.index + 1,
            "question": question["question"],
            "choices": question["choices"],
            "correct_index": question["correct_index"],
            "selected_index": selected_index,
            "correct": correct,
            "explanation": question.get("explanation", ""),
            "domain": question["domain"]
        })

        if correct:
            self.score += 1

        # Modul TRAIN – feedback instant în fereastra quizului
        if self.mode == "train":
            self.app.show_train_feedback(
                correct,
                question["choices"][question["correct_index"]],
                question.get("explanation", "")
            )
        else:
            self.next_question()

    def next_question(self):
        """Trece la următoarea întrebare sau finalizează quizul."""
        self.index += 1
        if self.index < len(self.questions):
            self.app.show_question()
        else:
            self.end_quiz()

    def end_quiz(self):
        """Finalizează quizul și afișează rezultatele."""
        self.running = False
        total = len(self.questions)
        pct = (self.score / total) * 100 if total > 0 else 0
        duration = time.time() - self.start_time

        if self.mode == "exam":
            # Arată feedback detaliat în fereastra principală
            self.app.show_exam_summary(self.results, self.score, total, pct, duration)
        else:
            # Revine la meniu direct
            self.app.show_main_menu()
