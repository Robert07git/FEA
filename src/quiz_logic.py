import tkinter as tk
from tkinter import messagebox
import random
import time


class QuizSession:
    def __init__(self, root, questions, mode="train", time_limit=15, on_end=None):
        self.root = root
        self.questions = questions
        self.mode = mode
        self.time_limit = time_limit
        self.on_end = on_end

        self.current_index = 0
        self.correct_answers = 0
        self.selected_answer = tk.IntVar(value=-1)
        self.remaining_time = self.time_limit
        self.timer_id = None
        self.results = []

        # UI principal
        self.main_frame = tk.Frame(root, bg="#111")
        self.main_frame.pack(fill="both", expand=True)

        self.progress_label = tk.Label(self.main_frame, text="Progres: 0%", fg="#00ffff", bg="#111", font=("Arial", 10, "bold"))
        self.progress_label.pack(pady=(10, 5))

        self.progress_bar = tk.Canvas(self.main_frame, width=400, height=10, bg="#333", highlightthickness=0)
        self.progress_fill = self.progress_bar.create_rectangle(0, 0, 0, 10, fill="#00ffff", width=0)
        self.progress_bar.pack()

        self.question_label = tk.Label(self.main_frame, text="", fg="white", bg="#111", wraplength=600, justify="center", font=("Arial", 12, "bold"))
        self.question_label.pack(pady=(20, 10))

        self.answers_frame = tk.Frame(self.main_frame, bg="#111")
        self.answers_frame.pack(pady=10)

        self.timer_label = tk.Label(self.main_frame, text="", fg="#00ffff", bg="#111", font=("Arial", 10, "bold"))
        self.timer_label.pack(pady=(5, 10))

        self.timer_bar = tk.Canvas(self.main_frame, width=400, height=10, bg="#333", highlightthickness=0)
        self.timer_fill = self.timer_bar.create_rectangle(0, 0, 0, 10, fill="#00ffff", width=0)
        self.timer_bar.pack(pady=(0, 20))

        self.feedback_label = tk.Label(self.main_frame, text="", fg="#ff5050", bg="#111", wraplength=600, justify="center", font=("Arial", 10, "italic"))
        self.feedback_label.pack(pady=10)

        self.next_button = tk.Button(
            self.main_frame,
            text="Următoarea ➜",
            font=("Arial", 11, "bold"),
            bg="#00ffff",
            activebackground="#00cccc",
            relief="flat",
            command=self.next_question
        )
        self.next_button.pack(pady=(5, 20))

        self.show_question()

    # -------------------------
    # AFIȘARE ÎNTREBARE
    # -------------------------
    def show_question(self):
        # resetare selecție
        self.selected_answer.set(-1)
        self.feedback_label.config(text="")
        self.clear_answers()

        if self.current_index >= len(self.questions):
            self.end_quiz()
            return

        q = self.questions[self.current_index]
        self.question_label.config(text=f"Întrebarea {self.current_index + 1}/{len(self.questions)}:\n{q['question']}")

        for idx, choice in enumerate(q["choices"]):
            rb = tk.Radiobutton(
                self.answers_frame,
                text=choice,
                variable=self.selected_answer,
                value=idx,
                fg="#00ffff",
                bg="#111",
                selectcolor="#111",
                activebackground="#111",
                font=("Arial", 10),
                anchor="w",
                justify="left"
            )
            rb.pack(fill="x", padx=50, pady=2, anchor="w")

        self.update_progress()
        if self.mode == "exam":
            self.start_timer()
        else:
            self.timer_label.config(text="Mod TRAIN (fără timp limită)")
            self.timer_bar.coords(self.timer_fill, 0, 0, 0, 10)

    # -------------------------
    # BUTON URMĂTOAREA
    # -------------------------
    def next_question(self):
        if self.mode == "exam" and self.timer_id:
            self.root.after_cancel(self.timer_id)

        selected = self.selected_answer.get()
        q = self.questions[self.current_index]
        correct = (selected == q["correct_index"])
        if correct:
            self.correct_answers += 1

        result = {
            "idx": self.current_index + 1,
            "question": q["question"],
            "choices": q["choices"],
            "correct_index": q["correct_index"],
            "selected_index": selected,
            "correct": correct,
            "explanation": q["explanation"],
            "domain": q["domain"]
        }
        self.results.append(result)

        if self.mode == "train":
            if not correct:
                self.feedback_label.config(
                    text=f"❌ Răspuns greșit!\nCorect: {q['choices'][q['correct_index']]}\nExplicație: {q['explanation']}",
                    fg="#ff5050"
                )
            else:
                self.feedback_label.config(text="✅ Corect! Bravo!", fg="#00ff88")
            self.root.after(2500, self.advance_question)
        else:
            self.advance_question()

    def advance_question(self):
        self.current_index += 1
        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.end_quiz()

    # -------------------------
    # TIMER
    # -------------------------
    def start_timer(self):
        self.remaining_time = self.time_limit
        self.update_timer_bar()
        self.update_timer_label()
        self.tick_timer()

    def tick_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_timer_bar()
            self.update_timer_label()
            self.timer_id = self.root.after(1000, self.tick_timer)
        else:
            self.next_question()

    def update_timer_label(self):
        self.timer_label.config(text=f"Timp rămas: {self.remaining_time:02d} secunde")

    def update_timer_bar(self):
        progress = 400 * (self.remaining_time / self.time_limit)
        self.timer_bar.coords(self.timer_fill, 0, 0, progress, 10)

    # -------------------------
    # PROGRES & SFÂRȘIT QUIZ
    # -------------------------
    def update_progress(self):
        percent = int((self.current_index / len(self.questions)) * 100)
        self.progress_label.config(text=f"Progres: {percent}%")
        self.progress_bar.coords(self.progress_fill, 0, 0, 4 * percent, 10)

    def end_quiz(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        pct = (self.correct_answers / len(self.questions)) * 100 if self.questions else 0
        end_text = f"✅ Ai terminat!\nScor: {self.correct_answers}/{len(self.questions)} ({pct:.1f}%)"
        tk.Label(self.main_frame, text=end_text, bg="#111", fg="#00ffff", font=("Arial", 14, "bold")).pack(pady=30)

        if self.on_end:
            self.on_end(self.correct_answers, len(self.questions), self.results)

    def clear_answers(self):
        for widget in self.answers_frame.winfo_children():
            widget.destroy()
