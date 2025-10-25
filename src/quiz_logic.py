import tkinter as tk
from tkinter import messagebox
import threading
import time
from playsound import playsound
import os


class QuizWindow(tk.Toplevel):
    def __init__(self, master, questions, mode="TRAIN", time_limit=None):
        super().__init__(master)
        self.title("FEA Quiz Session")
        self.geometry("800x500")
        self.configure(bg="#111")

        self.questions = questions
        self.mode = mode
        self.time_limit = time_limit
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.remaining_time = time_limit if mode == "EXAM" else None

        self.alert_path = os.path.join(os.path.dirname(__file__), "alert.mp3")

        self.title_label = tk.Label(
            self, text="FEA Quiz", font=("Segoe UI", 20, "bold"), bg="#111", fg="#00FFFF"
        )
        self.title_label.pack(pady=20)

        self.question_label = tk.Label(
            self, text="", wraplength=700, justify="center",
            font=("Segoe UI", 14), bg="#111", fg="white"
        )
        self.question_label.pack(pady=30)

        self.var_selected = tk.IntVar()
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(
                self, text="", variable=self.var_selected, value=i,
                font=("Segoe UI", 12), bg="#111", fg="white",
                selectcolor="#222", activebackground="#111"
            )
            rb.pack(anchor="w", padx=150, pady=5)
            self.radio_buttons.append(rb)

        self.next_button = tk.Button(
            self, text="Următoarea ➜", command=self.next_question,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=15, pady=5
        )
        self.next_button.pack(pady=30)

        self.timer_label = tk.Label(
            self, text="", font=("Segoe UI", 12), bg="#111", fg="#00FFFF"
        )
        self.timer_label.pack()

        self.show_question()

        if self.mode == "EXAM" and self.time_limit:
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()

    def show_question(self):
        q = self.questions[self.current_index]
        self.var_selected.set(-1)
        self.question_label.config(
            text=f"Întrebarea {self.current_index + 1}/{len(self.questions)}:\n{q['question']}"
        )
        opts = q.get("options", [])
        for i in range(4):
            if i < len(opts):
                self.radio_buttons[i].config(text=opts[i], state="normal")
            else:
                self.radio_buttons[i].config(text="", state="disabled")

    def next_question(self):
        selected = self.var_selected.get()
        q = self.questions[self.current_index]
        correct = q.get("correct", 0)
        is_correct = selected == correct
        self.user_answers.append((q["question"], is_correct))
        if is_correct:
            self.score += 1
            if self.mode == "TRAIN":
                messagebox.showinfo("Corect!", "✅ Răspuns corect!")
        elif self.mode == "TRAIN":
            messagebox.showerror("Greșit", f"❌ Răspuns greșit!\nCorect era: {q['options'][correct]}")

        self.current_index += 1

        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.finish_quiz()

    def countdown(self):
        while self.remaining_time > 0:
            mins, secs = divmod(self.remaining_time, 60)
            self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}")
            time.sleep(1)
            self.remaining_time -= 1

        if self.remaining_time == 0:
            if os.path.exists(self.alert_path):
                try:
                    playsound(self.alert_path, block=False)
                except Exception:
                    pass
            messagebox.showinfo("Timp expirat", "Timpul pentru test a expirat!")
            self.finish_quiz()

    def finish_quiz(self):
        total = len(self.questions)
        correct = self.score
        wrong = total - correct
        percentage = (correct / total) * 100 if total > 0 else 0

        history_file = os.path.join(os.path.dirname(__file__), "score_history.txt")
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(f"{self.questions[0]['domain']},{self.mode},{total},{percentage:.1f}\n")

        summary = (
            f"Rezultate finale:\n\nÎntrebări totale: {total}\n"
            f"Corecte: {correct}\nGreșite: {wrong}\n\n"
            f"Scor: {percentage:.1f}%"
        )
        messagebox.showinfo("Rezumat", summary)
        self.destroy()
