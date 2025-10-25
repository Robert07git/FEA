import tkinter as tk
from tkinter import messagebox
import threading
import time
from playsound import playsound


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

        # Titlu principal
        self.title_label = tk.Label(
            self, text="FEA Quiz", font=("Segoe UI", 20, "bold"), bg="#111", fg="#00FFFF"
        )
        self.title_label.pack(pady=20)

        # Textul întrebării
        self.question_label = tk.Label(
            self, text="", wraplength=700, justify="center",
            font=("Segoe UI", 14), bg="#111", fg="white"
        )
        self.question_label.pack(pady=30)

        # Opțiuni multiple
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

        # Butonul pentru următoarea întrebare
        self.next_button = tk.Button(
            self, text="Următoarea ➜", command=self.next_question,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=15, pady=5
        )
        self.next_button.pack(pady=30)

        # Label pentru timp (mod EXAM)
        self.timer_label = tk.Label(
            self, text="", font=("Segoe UI", 12), bg="#111", fg="#00FFFF"
        )
        self.timer_label.pack()

        # Pornește testul
        self.show_question()

        # Thread-ul pentru countdown doar în modul EXAM
        if self.mode == "EXAM" and self.time_limit:
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()

    # Afișează întrebarea curentă
    def show_question(self):
        q = self.questions[self.current_index]
        self.var_selected.set(-1)

        self.question_label.config(text=f"Întrebarea {self.current_index + 1}/{len(self.questions)}:\n{q['question']}")

        opts = q.get("options", [])
        for i in range(4):
            if i < len(opts):
                self.radio_buttons[i].config(text=opts[i], state="normal")
            else:
                self.radio_buttons[i].config(text="", state="disabled")

    # Trecerea la următoarea întrebare
    def next_question(self):
        selected = self.var_selected.get()
        q = self.questions[self.current_index]

        # ✅ Fix pentru 'KeyError: correct'
        correct = q.get("correct", q.get("Correct", 0))
        is_correct = selected == correct

        self.user_answers.append((q["question"], is_correct))
        if is_correct:
            self.score += 1

        self.current_index += 1
        self.remaining_time = self.time_limit or 0

        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.finish_quiz()

    # Timer pentru modul EXAM
    def countdown(self):
        while self.remaining_time > 0:
            mins, secs = divmod(self.remaining_time, 60)
            self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}")
            time.sleep(1)
            self.remaining_time -= 1

        # când expiră timpul
        if self.remaining_time == 0 and self.mode == "EXAM":
            try:
                playsound("alert.mp3", block=False)  # 🔊 sunet (opțional)
            except Exception:
                pass
            messagebox.showinfo("Timp expirat", "Timpul pentru test a expirat!")
            self.finish_quiz()

    # Finalul testului
    def finish_quiz(self):
        total = len(self.questions)
        correct = self.score
        wrong = total - correct
        percentage = (correct / total) * 100 if total > 0 else 0

        summary = (
            f"Rezultate finale:\n\n"
            f"Întrebări totale: {total}\n"
            f"Corecte: {correct}\n"
            f"Greșite: {wrong}\n\n"
            f"Scor: {percentage:.1f}%"
        )

        messagebox.showinfo("Rezumat", summary)
        self.destroy()
