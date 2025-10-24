import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys

# Adaugăm automat folderul src în sys.path, pentru importuri corecte
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_questions        # ✅ corect: întrebările sunt în data_loader
from stats import show_stats
from progress_chart import main as generate_chart
from export_pdf import main as export_pdf


class QuizWindow(tk.Toplevel):
    def __init__(self, master, domain, mode, num_questions, time_limit):
        super().__init__(master)
        self.title("FEA Quiz - Sesiune Quiz")
        self.geometry("560x600")
        self.configure(bg="#0d0d0d")

        self.domain = domain
        self.mode = mode
        self.num_questions = num_questions
        self.time_limit = time_limit

        # încărcăm întrebările
        all_questions = load_questions()
        self.questions = [q for q in all_questions if q["domain"] == domain]
        self.current_q = 0
        self.score = 0
        self.selected = tk.IntVar()
        self.timer_running = False

        self.create_widgets()
        self.display_question()

    def create_widgets(self):
        self.label_header = tk.Label(
            self,
            text=f"Domeniu: {self.domain} | Mod: {self.mode}",
            fg="#00BFFF",
            bg="#0d0d0d",
            font=("Segoe UI", 11, "bold")
        )
        self.label_header.pack(pady=10)

        self.label_question = tk.Label(
            self,
            text="",
            fg="white",
            bg="#0d0d0d",
            wraplength=500,
            justify="left"
        )
        self.label_question.pack(pady=10)

        self.option_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(
                self,
                text="",
                variable=self.selected,
                value=i + 1,
                style="TRadiobutton"
            )
            rb.pack(anchor="w", padx=20, pady=4)
            self.option_buttons.append(rb)

        self.button_next = tk.Button(
            self,
            text="Răspunde / Finalizează",
            bg="#00BFFF",
            fg="black",
            font=("Segoe UI", 10, "bold"),
            command=self.check_answer
        )
        self.button_next.pack(pady=10)

        self.label_explanation = tk.Label(
            self,
            text="",
            fg="#FFD700",
            bg="#0d0d0d",
            wraplength=500,
            justify="left"
        )
        self.label_explanation.pack(pady=5)

        self.label_result = tk.Label(
            self,
            text="",
            fg="white",
            bg="#0d0d0d"
        )
        self.label_result.pack(pady=5)

        self.button_close = tk.Button(
            self,
            text="Închide",
            command=self.destroy,
            bg="#2b2b2b",
            fg="white",
            font=("Segoe UI", 9)
        )
        self.button_close.pack(pady=10)

    def display_question(self):
        if self.current_q >= self.num_questions:
            self.show_result()
            return

        q = self.questions[self.current_q]
        self.selected.set(0)
        self.label_question.config(
            text=f"Întrebarea {self.current_q + 1}/{self.num_questions}\n\n{q['question']}"
        )

        for i, choice in enumerate(q["choices"]):
            self.option_buttons[i].config(text=choice)

        self.label_explanation.config(text="")
        self.label_result.config(text="")

    def check_answer(self):
        q = self.questions[self.current_q]
        answer = self.selected.get()

        if answer == 0:
            messagebox.showwarning("Atenție", "Selectează un răspuns înainte de a continua.")
            return

        correct = q["correct_index"]

        if answer == correct:
            self.score += 1
            feedback = "✅ Corect!"
        else:
            feedback = f"❌ Greșit! Răspuns corect: {correct}. {q['choices'][correct - 1]}"

        # ✅ În TRAIN arătăm explicația imediat
        if self.mode == "TRAIN":
            self.label_explanation.config(text=f"Explicație: {q['explanation']}")

        self.label_result.config(text=feedback)

        # Următoarea întrebare după 2s în TRAIN, 1s în EXAM
        self.current_q += 1
        self.after(2000 if self.mode == "TRAIN" else 1000, self.display_question)

    def show_result(self):
        percent = (self.score / self.num_questions) * 100
        result_text = (
            f"=== REZULTAT FINAL ===\n"
            f"Scor: {self.score}/{self.num_questions}\n"
            f"Procent: {percent:.1f}%\n"
            f"Mod: {self.mode}\n\n"
            f"Nu-i panică. Reia teoria de bază. Asta se învață 📘"
        )

        self.label_question.config(text=result_text)
        self.label_explanation.config(text="")
        self.label_result.config(text="")
        for rb in self.option_buttons:
            rb.config(state="disabled")


class FEAGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("1000x520")
        self.configure(bg="#0d0d0d")
        self.create_main_ui()

    def create_main_ui(self):
        tk.Label(
            self, text="Setări sesiune", bg="#0d0d0d", fg="#00BFFF", font=("Segoe UI", 11, "bold")
        ).pack(pady=5)

        # Domeniu
        self.domain_var = tk.StringVar(value="structural")
        tk.Label(self, text="Domeniu:", bg="#0d0d0d", fg="white").pack()
        self.domain_combo = ttk.Combobox(
            self,
            textvariable=self.domain_var,
            values=["structural", "crash", "moldflow", "cfd", "nvh"]
        )
        self.domain_combo.pack(pady=5)

        # Număr întrebări
        self.num_q_var = tk.IntVar(value=5)
        tk.Label(self, text="Număr întrebări:", bg="#0d0d0d", fg="white").pack()
        tk.Entry(self, textvariable=self.num_q_var, width=5).pack(pady=5)

        # Mod
        self.mode_var = tk.StringVar(value="TRAIN")
        tk.Label(self, text="Mod:", bg="#0d0d0d", fg="white").pack()
        ttk.Radiobutton(
            self, text="TRAIN (fără limită timp, feedback imediat)", variable=self.mode_var, value="TRAIN"
        ).pack()
        ttk.Radiobutton(
            self, text="EXAM (limită timp, review la final)", variable=self.mode_var, value="EXAM"
        ).pack()

        # Timp (doar EXAM)
        self.time_var = tk.IntVar(value=15)
        tk.Label(self, text="Timp pe întrebare (secunde, doar EXAM):", bg="#0d0d0d", fg="white").pack()
        tk.Entry(self, textvariable=self.time_var, width=5).pack(pady=5)

        # Buton start quiz
        tk.Button(
            self,
            text="Start Quiz",
            bg="#00BFFF",
            fg="black",
            font=("Segoe UI", 10, "bold"),
            command=self.start_quiz
        ).pack(pady=10)

        # Secțiune Rapoarte
        tk.Label(
            self,
            text="Rapoarte & Analiză",
            bg="#0d0d0d",
            fg="#00BFFF",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        tk.Button(
            self,
            text="Generează grafic progres (.png)",
            bg="#2b2b2b",
            fg="white",
            command=self.safe_generate_chart
        ).pack(fill="x", padx=20, pady=3)

        tk.Button(
            self,
            text="Generează PDF din ultimul EXAM",
            bg="#2b2b2b",
            fg="white",
            command=self.safe_export_pdf
        ).pack(fill="x", padx=20, pady=3)

        tk.Button(
            self,
            text="Arată progres text (stats)",
            bg="#2b2b2b",
            fg="white",
            command=self.safe_show_stats
        ).pack(fill="x", padx=20, pady=3)

    def start_quiz(self):
        QuizWindow(
            self,
            self.domain_var.get(),
            self.mode_var.get(),
            self.num_q_var.get(),
            self.time_var.get()
        )

    def safe_generate_chart(self):
        try:
            generate_chart()
            messagebox.showinfo("Succes", "Grafic generat cu succes!")
        except Exception as e:
            messagebox.showerror("Eroare la grafic", str(e))

    def safe_export_pdf(self):
        try:
            export_pdf()
            messagebox.showinfo("Succes", "PDF generat cu succes!")
        except Exception as e:
            messagebox.showerror("Eroare la PDF", str(e))

    def safe_show_stats(self):
        try:
            show_stats()
        except Exception as e:
            messagebox.showerror("Eroare la stats", str(e))


if __name__ == "__main__":
    app = FEAGUI()
    app.mainloop()
