import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
from playsound import playsound
import os


class QuizWindow(tk.Toplevel):
    def __init__(self, master, questions, mode="TRAIN", time_limit=None):
        super().__init__(master)
        self.title("FEA Quiz Session")
        self.geometry("900x600")
        self.configure(bg="#111")

        self.questions = questions
        self.mode = mode
        self.time_limit = time_limit
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.remaining_time = time_limit if mode == "EXAM" else None

        self.alert_path = os.path.join(os.path.dirname(__file__), "alert.mp3")

        # Titlu
        self.title_label = tk.Label(
            self, text="FEA Quiz", font=("Segoe UI", 22, "bold"), bg="#111", fg="#00FFFF"
        )
        self.title_label.pack(pady=15)

        # Întrebare
        self.question_label = tk.Label(
            self, text="", wraplength=800, justify="center",
            font=("Segoe UI", 14), bg="#111", fg="white"
        )
        self.question_label.pack(pady=25)

        # Butoane pentru opțiuni
        self.var_selected = tk.IntVar()
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(
                self, text="", variable=self.var_selected, value=i,
                font=("Segoe UI", 12), bg="#111", fg="white",
                selectcolor="#222", activebackground="#111"
            )
            rb.pack(anchor="w", padx=160, pady=4)
            self.radio_buttons.append(rb)

        # Buton următoarea
        self.next_button = tk.Button(
            self, text="Următoarea ➜", command=self.next_question,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=7
        )
        self.next_button.pack(pady=25)

        # Timer
        self.timer_label = tk.Label(
            self, text="", font=("Segoe UI", 12), bg="#111", fg="#00FFFF"
        )
        self.timer_label.pack()

        # Afișează prima întrebare
        self.show_question()

        # Pornește timerul dacă e EXAM
        if self.mode == "EXAM" and self.time_limit:
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()

    def show_question(self):
        q = self.questions[self.current_index]
        self.var_selected.set(-1)

        self.question_label.config(
            text=f"Întrebarea {self.current_index + 1}/{len(self.questions)}:\n{q['question']}"
        )

        choices = q.get("choices", [])
        for i in range(4):
            if i < len(choices):
                self.radio_buttons[i].config(text=choices[i], state="normal")
            else:
                self.radio_buttons[i].config(text="", state="disabled")

    def next_question(self):
        selected = self.var_selected.get()
        q = self.questions[self.current_index]

        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "")
        choices = q.get("choices", [])

        is_correct = selected == correct_index
        self.user_answers.append((q["question"], choices, correct_index, selected, explanation))

        if is_correct:
            self.score += 1
            if self.mode == "TRAIN":
                messagebox.showinfo("Corect!", "✅ Răspuns corect!")
        else:
            if self.mode == "TRAIN":
                correct_answer = choices[correct_index] if correct_index < len(choices) else "N/A"
                messagebox.showerror(
                    "Greșit",
                    f"❌ Răspuns greșit!\n\nCorect era: {correct_answer}\n\nExplicație:\n{explanation}"
                )

        self.current_index += 1
        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.finish_quiz()

    def countdown(self):
        while self.remaining_time > 0:
            if not self.winfo_exists():
                return
            mins, secs = divmod(self.remaining_time, 60)
            try:
                if hasattr(self, "timer_label") and self.timer_label.winfo_exists():
                    self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}")
            except tk.TclError:
                return
            time.sleep(1)
            self.remaining_time -= 1

        if self.winfo_exists():
            try:
                if os.path.exists(self.alert_path):
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
            domain = self.questions[0].get("domain", "unknown")
            f.write(f"{domain},{self.mode},{total},{percentage:.1f}\n")

        summary = (
            f"Rezultate finale:\n\nÎntrebări totale: {total}\n"
            f"Corecte: {correct}\nGreșite: {wrong}\n\n"
            f"Scor final: {percentage:.1f}%"
        )

        # Afișează raport final
        self.show_report(summary)

    def show_report(self, summary_text):
        report = tk.Toplevel(self)
        report.title("Rezumat test")
        report.geometry("800x600")
        report.configure(bg="#111")

        tk.Label(
            report, text="Raport Final", font=("Segoe UI", 18, "bold"), fg="#00FFFF", bg="#111"
        ).pack(pady=10)

        tk.Label(
            report, text=summary_text, font=("Segoe UI", 12), fg="white", bg="#111", justify="left"
        ).pack(pady=10)

        wrong_qs = [ans for ans in self.user_answers if ans[3] != ans[2]]

        if wrong_qs:
            text_box = scrolledtext.ScrolledText(
                report, wrap="word", font=("Segoe UI", 11), bg="#222", fg="white", height=20, width=90
            )
            text_box.pack(padx=15, pady=15)

            for q_text, choices, correct_index, selected, explanation in wrong_qs:
                correct = choices[correct_index] if correct_index < len(choices) else "N/A"
                sel = choices[selected] if 0 <= selected < len(choices) else "N/A"
                text_box.insert(
                    "end",
                    f"❌ {q_text}\n"
                    f"Răspunsul tău: {sel}\n"
                    f"Corect: {correct}\n"
                    f"Explicație: {explanation}\n\n"
                )

            text_box.configure(state="disabled")
        else:
            tk.Label(
                report, text="🎉 Toate răspunsurile au fost corecte!", fg="lightgreen", bg="#111",
                font=("Segoe UI", 13, "bold")
            ).pack(pady=25)

        tk.Button(
            report, text="Închide", command=lambda: [report.destroy(), self.destroy()],
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"), relief="flat", padx=20, pady=6
        ).pack(pady=15)
