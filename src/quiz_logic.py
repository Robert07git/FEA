import tkinter as tk
from tkinter import messagebox
import time
import os
import random
from data_loader import get_random_questions

def run_quiz(domain, num_q, mode, tlim=None):
    """Rulează un quiz într-o fereastră nouă (TRAIN / EXAM)."""
    questions = get_random_questions(domain, num_q)
    if not questions:
        messagebox.showerror("Eroare", "Nu s-au găsit întrebări pentru acest domeniu.")
        return

    app = QuizWindow(questions, mode, tlim)
    app.mainloop()


class QuizWindow(tk.Tk):
    def __init__(self, questions, mode, tlim):
        super().__init__()
        self.title("FEA Quiz Session")
        self.geometry("800x500")
        self.configure(bg="#111")

        self.questions = questions
        self.mode = mode
        self.tlim = tlim
        self.index = 0
        self.correct = 0
        self.answers = []

        self.remaining = tlim if mode == "exam" else None
        self.timer_running = False

        self.start_time = time.time()

        self.setup_ui()
        self.show_question()

        if self.mode == "exam" and self.tlim:
            self.start_timer()

    def setup_ui(self):
        self.lbl_title = tk.Label(self, text="FEA Quiz", font=("Segoe UI", 16, "bold"), bg="#111", fg="#00ffff")
        self.lbl_title.pack(pady=10)

        self.lbl_q = tk.Label(self, text="", wraplength=700, bg="#111", fg="white", font=("Segoe UI", 12))
        self.lbl_q.pack(pady=20)

        self.var_ans = tk.StringVar()
        self.option_buttons = []
        for _ in range(4):
            btn = tk.Radiobutton(self, text="", variable=self.var_ans, value="", font=("Segoe UI", 11),
                                 fg="white", bg="#111", selectcolor="#222")
            btn.pack(anchor="w", padx=100)
            self.option_buttons.append(btn)

        self.lbl_timer = tk.Label(self, text="", fg="#00ffff", bg="#111", font=("Segoe UI", 10))
        self.lbl_timer.pack(pady=10)

        self.btn_next = tk.Button(self, text="Următoarea ➜", command=self.next_question,
                                  bg="#00ffff", fg="black", font=("Segoe UI", 10, "bold"))
        self.btn_next.pack(pady=10)

    def show_question(self):
        q = self.questions[self.index]
        self.lbl_q.config(text=f"Întrebarea {self.index + 1}/{len(self.questions)}:\n\n{q['question']}")
        opts = q["options"]
        random.shuffle(opts)

        for i, opt in enumerate(opts):
            self.option_buttons[i].config(text=opt, value=opt)
        self.var_ans.set(None)

    def next_question(self):
        chosen = self.var_ans.get()
        if not chosen:
            messagebox.showwarning("Atenție", "Selectează un răspuns înainte de a continua!")
            return

        correct_ans = self.questions[self.index]["answer"]

        if chosen == correct_ans:
            self.correct += 1
            if self.mode == "train":
                messagebox.showinfo("Corect ✅", f"{correct_ans} este răspunsul corect!")
        else:
            if self.mode == "train":
                messagebox.showerror("Greșit ❌", f"Răspuns corect: {correct_ans}")

        self.index += 1

        if self.index >= len(self.questions):
            self.finish_quiz()
        else:
            self.show_question()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.remaining is not None:
            self.lbl_timer.config(text=f"Timp rămas: {self.remaining}s")
            if self.remaining <= 0:
                self.finish_quiz()
                return
            self.remaining -= 1
            self.after(1000, self.update_timer)

    def finish_quiz(self):
        end_time = time.time()
        duration = end_time - self.start_time
        avg_time_per_q = duration / len(self.questions)

        score = int((self.correct / len(self.questions)) * 100)
        msg = f"Scor final: {self.correct}/{len(self.questions)} ({score}%)\n\nTimp total: {duration:.1f}s\nTimp mediu / întrebare: {avg_time_per_q:.1f}s"
        messagebox.showinfo("Rezultat", msg)
        self.save_score(score, duration, avg_time_per_q)
        self.destroy()

    def save_score(self, score, duration, avg_time):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        hist_path = os.path.join(base_dir, "score_history.txt")

        with open(hist_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | domeniu={self.questions[0]['domain']} | mod={self.mode} | scor={self.correct}/{len(self.questions)} | procent={score}% | timp_total={duration:.1f}s | timp_intrebare={avg_time:.1f}s\n")
