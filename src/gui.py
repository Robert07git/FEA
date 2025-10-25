import tkinter as tk
from tkinter import messagebox
import threading
import time
import random


class QuizSession:
    def __init__(self, root, questions, num_questions, mode, time_limit=None):
        self.root = root
        self.questions = random.sample(questions, min(num_questions, len(questions)))
        self.mode = mode
        self.time_limit = time_limit
        self.current_index = 0
        self.score = 0
        self.answers = []
        self.remaining_time = time_limit
        self.timer_running = False
        self.stop_timer_flag = False

        self.create_ui()
        self.show_question()

    # === INTERFAȚĂ ===
    def create_ui(self):
        self.root.configure(bg="#111")

        self.progress_label = tk.Label(
            self.root, text="Progres: 0%", bg="#111", fg="#00ffff", font=("Arial", 12, "bold")
        )
        self.progress_label.pack(pady=(10, 5))

        self.progress_bar = tk.Canvas(self.root, width=600, height=10, bg="#222", highlightthickness=0)
        self.progress_fill = self.progress_bar.create_rectangle(0, 0, 0, 10, fill="#00ffff", width=0)
        self.progress_bar.pack(pady=5)

        self.question_label = tk.Label(
            self.root, text="", wraplength=750, justify="center",
            bg="#111", fg="white", font=("Arial", 14, "bold")
        )
        self.question_label.pack(pady=(20, 10))

        self.choice_vars = []
        self.choice_buttons = []
        for _ in range(4):
            var = tk.StringVar()
            btn = tk.Radiobutton(
                self.root, text="", variable=var, value="x",
                bg="#111", fg="white", selectcolor="#00ffff",
                font=("Arial", 12), anchor="w", indicatoron=True
            )
            btn.pack(fill="x", padx=120, pady=3)
            self.choice_vars.append(var)
            self.choice_buttons.append(btn)

        self.timer_label = tk.Label(self.root, text="", bg="#111", fg="#00ffff", font=("Arial", 12, "bold"))
        self.timer_label.pack(pady=(10, 0))

        self.next_button = tk.Button(
            self.root, text="Următoarea ➜", font=("Arial", 12, "bold"),
            bg="#00ffff", fg="black", command=self.next_question
        )
        self.next_button.pack(pady=15)

    # === AFIȘARE ÎNTREBARE ===
    def show_question(self):
        self.stop_timer_flag = True
        if self.current_index >= len(self.questions):
            self.end_quiz()
            return

        q = self.questions[self.current_index]
        self.question_label.config(
            text=f"Întrebarea {self.current_index + 1}/{len(self.questions)}:\n{q['question']}"
        )

        # Resetare opțiuni
        for btn in self.choice_buttons:
            btn.deselect()
            btn.config(state="normal", fg="white")

        # Setăm opțiunile de răspuns
        for i, choice in enumerate(q["choices"]):
            self.choice_buttons[i].config(text=choice, command=lambda idx=i: self.select_answer(idx))

        # Resetăm timerul pentru întrebare (doar în EXAM)
        if self.mode == "exam" and self.time_limit:
            self.remaining_time = self.time_limit
            self.update_timer()
            threading.Thread(target=self.timer_countdown, daemon=True).start()
        else:
            self.timer_label.config(text="")

        # Actualizare progres
        progress_percent = (self.current_index / len(self.questions)) * 100
        self.progress_label.config(text=f"Progres: {int(progress_percent)}%")
        self.progress_bar.coords(self.progress_fill, 0, 0, 6 * progress_percent, 10)

    # === SELECȚIE RĂSPUNS ===
    def select_answer(self, choice_index):
        q = self.questions[self.current_index]
        correct = choice_index == q["correct_index"]

        self.answers.append({
            "idx": self.current_index + 1,
            "question": q["question"],
            "choices": q["choices"],
            "correct_index": q["correct_index"],
            "chosen_index": choice_index,
            "correct": correct,
            "explanation": q.get("explanation", ""),
            "domain": q["domain"]
        })

        # Train → feedback imediat
        if self.mode == "train":
            if correct:
                messagebox.showinfo("Corect ✅", "Răspuns corect!")
                self.score += 1
            else:
                messagebox.showerror(
                    "Greșit ❌",
                    f"Răspuns greșit!\n\nCorect era: {q['choices'][q['correct_index']]}\n\nExplicație: {q['explanation']}"
                )
            self.next_question()
        else:
            # Exam → doar înregistrăm, fără feedback imediat
            self.next_question()

    # === TIMER EXAM ===
    def timer_countdown(self):
        self.stop_timer_flag = False
        while self.remaining_time > 0 and not self.stop_timer_flag:
            time.sleep(1)
            self.remaining_time -= 1
            self.update_timer()

        if not self.stop_timer_flag and self.remaining_time <= 0:
            self.timer_label.config(text="Timp expirat!", fg="#ff4444")
            self.answers.append({
                "idx": self.current_index + 1,
                "question": self.questions[self.current_index]["question"],
                "choices": self.questions[self.current_index]["choices"],
                "correct_index": self.questions[self.current_index]["correct_index"],
                "chosen_index": None,
                "correct": False,
                "explanation": self.questions[self.current_index].get("explanation", ""),
                "domain": self.questions[self.current_index]["domain"]
            })
            self.next_question()

    def update_timer(self):
        if self.mode == "exam" and self.time_limit:
            mins, secs = divmod(self.remaining_time, 60)
            self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}", fg="#00ffff")

    # === URMĂTOAREA ÎNTREBARE ===
    def next_question(self):
        self.stop_timer_flag = True
        self.current_index += 1
        self.show_question()

    # === FINAL DE QUIZ ===
    def end_quiz(self):
        self.stop_timer_flag = True
        total = len(self.questions)
        pct = (self.score / total) * 100 if total > 0 else 0

        if self.mode == "exam":
            correct_count = sum(1 for a in self.answers if a["correct"])
            pct = (correct_count / total) * 100
            msg = f"Scor final: {correct_count}/{total} ({pct:.1f}%)"
        else:
            msg = f"Scor final: {self.score}/{total} ({pct:.1f}%)"

        messagebox.showinfo("Rezultat final 🏁", msg)
        self.root.destroy()
