import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

from data_loader import load_questions
from quiz_logic import run_quiz
from stats import show_dashboard as show_stats  # ✅ FIX: import corectat
from export_pdf import main as export_pdf
from progress_chart import main as generate_chart


class QuizWindow(tk.Toplevel):
    def __init__(self, parent, domain, num_questions, mode, time_limit):
        super().__init__(parent)
        self.title(f"FEA Quiz - Sesiune Quiz")
        self.geometry("500x600")
        self.configure(bg="#111")

        self.domain = domain
        self.num_questions = num_questions
        self.mode = mode
        self.time_limit = time_limit

        self.questions = [q for q in load_questions() if q["domain"] == domain]
        if len(self.questions) < num_questions:
            messagebox.showwarning("Atenție", f"Există doar {len(self.questions)} întrebări în domeniul ales.")
            self.num_questions = len(self.questions)

        self.current_index = 0
        self.score = 0
        self.results = []
        self.remaining_time = self.time_limit

        self.create_widgets()
        self.show_question()

        if self.mode == "exam" and self.time_limit > 0:
            self.update_timer()

    # --------------------------- UI Setup ---------------------------

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

        self.lbl_title = tk.Label(self, text=f"Domeniu: {self.domain} | Mod: {self.mode.upper()}",
                                  font=("Segoe UI", 11, "bold"), fg="#00ffff", bg="#111")
        self.lbl_title.pack(pady=8)

        self.lbl_timer = tk.Label(self, text="", font=("Segoe UI", 10), fg="#ffcc00", bg="#111")
        self.lbl_timer.pack()

        self.lbl_question = tk.Label(self, text="", wraplength=450, justify="left",
                                     font=("Segoe UI", 10), fg="white", bg="#111")
        self.lbl_question.pack(pady=15)

        self.var_choice = tk.IntVar(value=-1)
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self, text="", variable=self.var_choice, value=i,
                                font=("Segoe UI", 10), fg="white", bg="#111",
                                selectcolor="#222", anchor="w", justify="left")
            rb.pack(fill="x", padx=25, pady=2)
            self.radio_buttons.append(rb)

        self.btn_submit = tk.Button(self, text="Răspunde / Finalizează", bg="#00bfff", fg="white",
                                    font=("Segoe UI", 10, "bold"), command=self.submit_answer)
        self.btn_submit.pack(pady=15)

        self.lbl_feedback = tk.Label(self, text="", wraplength=450, justify="left",
                                     font=("Segoe UI", 9, "italic"), fg="#ffb3b3", bg="#111")
        self.lbl_feedback.pack(pady=5)

        self.btn_close = tk.Button(self, text="Închide", bg="#333", fg="white",
                                   font=("Segoe UI", 9), command=self.destroy)
        self.btn_close.pack(pady=10)

    # --------------------------- Timer ---------------------------

    def update_timer(self):
        if self.mode != "exam" or self.time_limit <= 0:
            return
        if self.remaining_time > 0:
            self.lbl_timer.config(text=f"Timp rămas: {self.remaining_time}s")
            self.remaining_time -= 1
            self.after(1000, self.update_timer)
        else:
            self.lbl_timer.config(text="⏰ Timp expirat!")
            self.submit_answer(timeout=True)

    # --------------------------- Logică întrebări ---------------------------

    def show_question(self):
        if self.current_index >= self.num_questions:
            self.show_result()
            return

        q = self.questions[self.current_index]
        self.lbl_question.config(text=f"Întrebarea {self.current_index + 1}/{self.num_questions}\n\n{q['question']}")
        for i, choice in enumerate(q["choices"]):
            self.radio_buttons[i].config(text=choice)
        self.var_choice.set(-1)
        self.lbl_feedback.config(text="")
        self.remaining_time = self.time_limit

    def submit_answer(self, timeout=False):
        q = self.questions[self.current_index]
        correct_index = q["correct_index"]
        explanation = q["explanation"]

        chosen = self.var_choice.get()
        is_correct = (chosen == correct_index)

        if timeout:
            self.results.append((q, None, False, True))
        else:
            self.results.append((q, chosen, is_correct, False))
            if is_correct:
                self.score += 1

        # Feedback instant doar în modul TRAIN
        if self.mode == "train":
            if timeout:
                self.lbl_feedback.config(text="⏰ Timp expirat!")
            elif is_correct:
                self.lbl_feedback.config(text="✅ Corect!\n" + explanation)
            else:
                self.lbl_feedback.config(
                    text=f"❌ Greșit.\nRăspuns corect: {correct_index + 1}. {q['choices'][correct_index]}\nExplicație: {explanation}"
                )

        self.current_index += 1
        self.after(1500 if self.mode == "train" else 500, self.show_question)

    # --------------------------- Rezultat final ---------------------------

    def show_result(self):
        pct = (self.score / self.num_questions) * 100 if self.num_questions > 0 else 0
        summary = f"=== REZULTAT FINAL ===\nScor: {self.score}/{self.num_questions}\nProcent: {pct:.1f}%\nMod: {self.mode.upper()}\n"

        if pct < 50:
            summary += "\nNu-i panică. Reia teoria de bază. Asta se învață 📘"
        else:
            summary += "\nExcelent! Se vede progresul 🚀"

        if self.mode == "exam":
            summary += "\n\nÎntrebări pentru revizuit:\n"
            for (q, chosen, correct, timeout) in self.results:
                if not correct:
                    summary += f"- {q['question']}\n  Răspuns corect: {q['choices'][q['correct_index']]}\n  Explicație: {q['explanation']}\n\n"

        self.lbl_question.config(text=summary)
        for rb in self.radio_buttons:
            rb.pack_forget()
        self.lbl_feedback.pack_forget()
        self.lbl_timer.pack_forget()
        self.btn_submit.config(state="disabled")


# ============================== Fereastra Principală ==============================

class FEAGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("950x700")
        self.configure(bg="#111")

        self.create_main_widgets()

    def create_main_widgets(self):
        title = tk.Label(self, text="Setări sesiune", font=("Segoe UI", 12, "bold"), fg="#00ffff", bg="#111")
        title.pack(pady=10)

        # Domeniu
        tk.Label(self, text="Domeniu:", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.domain_var = tk.StringVar(value="structural")
        domain_box = ttk.Combobox(self, textvariable=self.domain_var, width=50,
                                  values=["structural", "crash", "moldflow", "cfd", "nvh", "mix"])
        domain_box.pack(pady=5)

        # Număr întrebări
        tk.Label(self, text="Număr întrebări:", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.num_var = tk.IntVar(value=5)
        tk.Spinbox(self, from_=1, to=50, textvariable=self.num_var, width=5).pack(pady=5)

        # Mod
        tk.Label(self, text="Mod:", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.mode_var = tk.StringVar(value="train")
        tk.Radiobutton(self, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train",
                       bg="#111", fg="white", selectcolor="#222").pack()
        tk.Radiobutton(self, text="EXAM (limită timp, feedback la final)", variable=self.mode_var, value="exam",
                       bg="#111", fg="white", selectcolor="#222").pack()

        # Timp per întrebare (doar EXAM)
        tk.Label(self, text="Timp per întrebare (secunde, doar EXAM):", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(self, from_=5, to=120, textvariable=self.time_var, width=5).pack(pady=5)

        # Start quiz
        tk.Button(self, text="Start Quiz", bg="#00bfff", fg="white", font=("Segoe UI", 11, "bold"),
                  command=self.start_quiz).pack(pady=10)

        # Linie separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # Secțiune rapoarte
        tk.Label(self, text="Rapoarte & Analiză", font=("Segoe UI", 11, "bold"), fg="#00ffff", bg="#111").pack(pady=5)

        tk.Button(self, text="Generează grafic progres (.png)", bg="#333", fg="white",
                  font=("Segoe UI", 10), command=self.run_chart).pack(pady=5)

        tk.Button(self, text="Generează PDF din ultimul EXAM", bg="#333", fg="white",
                  font=("Segoe UI", 10), command=self.run_pdf).pack(pady=5)

        tk.Button(self, text="Arată progres text (stats)", bg="#333", fg="white",
                  font=("Segoe UI", 10), command=self.run_stats).pack(pady=5)

    # --------------------------- Funcții principale ---------------------------

    def start_quiz(self):
        domain = self.domain_var.get()
        num = self.num_var.get()
        mode = self.mode_var.get()
        time_per_q = self.time_var.get() if mode == "exam" else 0

        win = QuizWindow(self, domain, num, mode, time_per_q)
        win.grab_set()

    def run_chart(self):
        try:
            generate_chart()
            messagebox.showinfo("Succes", "Grafic generat cu succes! (progress_chart.png)")
        except Exception as e:
            messagebox.showerror("Eroare la grafic", str(e))

    def run_pdf(self):
        try:
            export_pdf()
            messagebox.showinfo("Succes", "PDF generat cu succes!")
        except Exception as e:
            messagebox.showerror("Eroare la PDF", str(e))

    def run_stats(self):
        try:
            show_stats()
        except Exception as e:
            messagebox.showerror("Eroare la statistici", str(e))


if __name__ == "__main__":
    app = FEAGui()
    app.mainloop()
