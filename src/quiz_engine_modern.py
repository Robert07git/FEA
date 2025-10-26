import random
import time
from stats_manager import save_quiz_result

class QuizEngine:
    def __init__(self, questions, mode="train", username="Guest"):
        self.questions = questions
        self.mode = mode
        self.username = username
        self.current_index = 0
        self.correct_answers = 0
        self.start_time = None
        self.end_time = None
        self.results = []

    def start(self):
        self.start_time = time.time()
        self.current_index = 0
        self.correct_answers = 0
        self.results = []

    def get_next_question(self):
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.current_index += 1
            return q
        return None

    def submit_answer(self, question, selected_option):
        correct = question["answer"] == selected_option
        self.results.append({
            "question": question["question"],
            "selected": selected_option,
            "correct": question["answer"],
            "is_correct": correct,
            "explanation": question.get("explanation", "")
        })
        if correct:
            self.correct_answers += 1
        return correct

    def finish(self):
        self.end_time = time.time()
        score = round((self.correct_answers / len(self.questions)) * 100, 2)
        total_time = round(self.end_time - self.start_time, 2)
        save_quiz_result(self.username, self.mode, score, total_time)
        return {
            "score": score,
            "total_time": total_time,
            "results": self.results
        }
