import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
import time
from fpdf import FPDF
from quiz_logic import QuizWindow
from stats import show_stats


class FEATrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("600x600")
        self.configure(bg="#111")

        # Titlu principal
        tk.Label(
            self, text="Setări sesiune", font=("Segoe UI", 16, "bold"),
            fg="#00FFFF", bg="#111"
        ).pack(pady=15)

        # Domeniu
        tk.Label(self, text="Domeniu:", font=("Segoe UI", 12), bg="#111", fg="white").pack()
        self.domain_var = tk.StringVar(value="structural")
        domains = ["structural", "crash", "moldflow", "cfd", "nvh"]
        ttk.Combobox(self, textvariable=self.domain_var, values=domains, width=20).pack(pady=5)

        # Număr întrebări
        tk.Label(self, text="Număr întrebări:", font=("Segoe UI", 12), bg="#111", fg="white").pack()
        self.num_questions = tk.Spinbox(self, from_=1, to=20, width=5)
        self.num_questions.pack(pady=5)

        # Mod clar vizibil (butoane personalizate)
        tk.Label(self, text="Mod:", font=("Segoe UI", 12), bg="#111", fg="white").pack(pady=5)
        self.mode_var = tk.StringVar(value="TRAIN")

        def set_mode(mode):
            self.mode_var.set(mode)
            train_btn.config(bg="#00FFFF" if mode == "TRAIN" else "#222", fg="black" if mode == "TRAIN" else "white")
            exam_btn.config(bg="#00FFFF" if mode == "EXAM" else "#222", fg="black" if mode == "EXAM" else "white")

        train_btn = tk.Button(
            self, text="TRAIN (feedback imediat)", command=lambda: set_mode("TRAIN"),
            bg="#00FFFF", fg="black", font=("Segoe UI", 11, "bold"),
            relief="flat", width=30, pady=4
        )
        train_btn.pack(pady=3)

        exam_btn = tk.Button(
            self, text="EXAM (limită timp, feedback final)", command=lambda: set_mode("EXAM"),
            bg="#222", fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", width=30, pady=4
        )
        exam_btn.pack(pady=3)

        # Timp per întrebare
        tk.Label(
            self, text="Timp per întrebare (secunde, doar EXAM):",
            font=("Segoe UI", 12), bg="#111", fg="white"
        ).pack(pady=5)
        self.time_per_q = tk.Spinbox(self, from_=5, to=120, width=5)
        self.time_per_q.pack(pady=5)

        # Buton Start Quiz
        tk.Button(
            self, text="▶ Start Quiz", command=self.start_quiz,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=6
        ).pack(pady=20)

        # Linie separatoare
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=15)

        # Secțiunea rapoarte
        tk.Label(
            self, text="Rapoarte & Analiză", font=("Segoe UI", 14, "bold"),
            fg="#00FFFF", bg="#111"
        ).pack(pady=5)

        tk.Button(
            self, text="📊 Grafic progres", command=self.show_progress,
            bg="#00FFFF", fg="black", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=10, pady=5
        ).pack(pady=6)

        tk.Button(
            self, text="🧾 Generează PDF", command=self.generate_pdf,
            bg="#00FFFF", fg="black", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=10, pady=5
        ).pack(pady=6)

        tk.Button(
            self, text="📈 Statistici", command=self.show_stats,
            bg="#00FFFF", fg="black", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=10, pady=5
        ).pack(pady=6)

    # ------------------------------------------------------

    def start_quiz(self):
        domain = self.domain_var.get()
        mode = self.mode_var.get()
        num = int(self.num_questions.get())
        tlim = int(self.time_per_q.get()) if mode == "EXAM" else None

        # CAUTĂ FEIȘIERUL ÎN FOLDERUL DATA/
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "data", "fea_questions.json")

        if not os.path.exists(file_path):
            messagebox.showerror("Eroare", "Fișierul fea_questions.json nu a fost găsit în folderul /data!")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            all_questions = json.load(f)

        domain_q = [q for q in all_questions if q.get("domain") == domain]
        if not domain_q:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul '{domain}'!")
            return

        selected = random.sample(domain_q, min(num, len(domain_q)))
        QuizWindow(self, selected, mode, tlim)

    # ------------------------------------------------------

    def show_progress(self):
        history_file = os.path.join(os.path.dirname(__file__), "score_history.txt")
        if not os.path.exists(history_file):
            messagebox.showinfo("Info", "Nu există încă rezultate salvate.")
            return
        os.startfile(history_file)

    # ------------------------------------------------------

    def generate_pdf(self):
        history_file = os.path.join(os.path.dirname(__file__), "score_history.txt")
        if not os.path.exists(history_file):
            messagebox.showinfo("Info", "Nu există rezultate pentru generarea PDF-ului.")
            return

        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(reports_dir, exist_ok=True)

        pdf_path = os.path.join(reports_dir, f"FEA_Report_{int(time.time())}.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="FEA Quiz Trainer - Raport Rezultate", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        with open(history_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    domain, mode, total, score = parts
                    pdf.cell(0, 10, txt=f"Domeniu: {domain} | Mod: {mode} | Întrebări: {total} | Scor: {score}%", ln=True)

        try:
            pdf.output(pdf_path)
            messagebox.showinfo("Succes", f"PDF generat cu succes!\n\nSalvat în:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o problemă la generarea PDF-ului:\n{e}")

    # ------------------------------------------------------

    def show_stats(self):
        try:
            show_stats()
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-au putut încărca statisticile.\n\n{e}")


if __name__ == "__main__":
    app = FEATrainerApp()
    app.mainloop()
