import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import json
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from quiz_logic import QuizWindow


class FEATrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("800x650")
        self.configure(bg="#111")
        self.resizable(False, False)

        self.questions_data = None
        self.domains = []
        self.load_questions()

        self.create_ui()

    # ----------------------------------------------------------
    def load_questions(self):
        """Încarcă fișierul JSON cu întrebări."""
        try:
            path = os.path.join(os.path.dirname(__file__), "../data/fea_questions.json")
            with open(path, "r", encoding="utf-8") as f:
                self.questions_data = json.load(f)
            self.domains = list(self.questions_data.keys())
        except FileNotFoundError:
            messagebox.showerror("Eroare", "Fișierul fea_questions.json nu a fost găsit!")
            self.questions_data = {}
            self.domains = []

    # ----------------------------------------------------------
    def create_ui(self):
        title = tk.Label(self, text="Setări sesiune",
                         font=("Segoe UI", 18, "bold"),
                         fg="#00FFFF", bg="#111")
        title.pack(pady=15)

        # Domeniu
        frm_domain = tk.Frame(self, bg="#111")
        frm_domain.pack(pady=5)
        tk.Label(frm_domain, text="Domeniu:", bg="#111", fg="white",
                 font=("Segoe UI", 11)).pack(side="left", padx=5)
        self.domain_var = tk.StringVar()
        self.domain_cb = ttk.Combobox(frm_domain, textvariable=self.domain_var,
                                      values=self.domains, width=25, state="readonly")
        self.domain_cb.pack(side="left", padx=5)
        if self.domains:
            self.domain_cb.current(0)

        # Număr întrebări
        frm_num = tk.Frame(self, bg="#111")
        frm_num.pack(pady=5)
        tk.Label(frm_num, text="Număr întrebări:", bg="#111", fg="white",
                 font=("Segoe UI", 11)).pack(side="left", padx=5)
        self.num_var = tk.IntVar(value=5)
        tk.Spinbox(frm_num, from_=1, to=50, textvariable=self.num_var,
                   width=5, font=("Segoe UI", 10)).pack(side="left", padx=5)

        # Mod
        frm_mode = tk.Frame(self, bg="#111")
        frm_mode.pack(pady=5)
        tk.Label(frm_mode, text="Mod:", bg="#111", fg="white",
                 font=("Segoe UI", 11)).pack(pady=5)
        self.mode_var = tk.StringVar(value="TRAIN")
        tk.Radiobutton(frm_mode, text="TRAIN (feedback imediat)", variable=self.mode_var,
                       value="TRAIN", bg="#111", fg="white", activebackground="#111",
                       selectcolor="#111", font=("Segoe UI", 10)).pack(anchor="w", padx=300)
        tk.Radiobutton(frm_mode, text="EXAM (limită timp, feedback final)", variable=self.mode_var,
                       value="EXAM", bg="#111", fg="white", activebackground="#111",
                       selectcolor="#111", font=("Segoe UI", 10)).pack(anchor="w", padx=300)

        # Limită timp
        frm_time = tk.Frame(self, bg="#111")
        frm_time.pack(pady=5)
        tk.Label(frm_time, text="Timp pe întrebare (secunde, doar EXAM):", bg="#111",
                 fg="white", font=("Segoe UI", 11)).pack(side="left", padx=5)
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(frm_time, from_=5, to=120, textvariable=self.time_var,
                   width=5, font=("Segoe UI", 10)).pack(side="left", padx=5)

        # Start Quiz
        tk.Button(self, text="► Start Quiz", command=self.start_quiz,
                  bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=20, pady=6).pack(pady=15)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # Secțiune rapoarte
        tk.Label(self, text="Rapoarte & Analiză",
                 font=("Segoe UI", 14, "bold"),
                 fg="#00FFFF", bg="#111").pack(pady=10)

        frm_reports = tk.Frame(self, bg="#111")
        frm_reports.pack(pady=5)

        tk.Button(frm_reports, text="📊 Grafic progres",
                  command=self.show_progress_chart,
                  bg="#00FFFF", fg="black", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=10, pady=5).grid(row=0, column=0, padx=10, pady=5)

        tk.Button(frm_reports, text="📄 Generează PDF",
                  command=self.generate_pdf_report,
                  bg="#00FFFF", fg="black", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=10, pady=5).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(frm_reports, text="📈 Statistici",
                  command=self.show_stats,
                  bg="#00FFFF", fg="black", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=10, pady=5).grid(row=0, column=2, padx=10, pady=5)

    # ----------------------------------------------------------
    def start_quiz(self):
        selected = self.domain_var.get()
        mode = self.mode_var.get()
        tlim = self.time_var.get() if mode == "EXAM" else None

        if not selected or selected not in self.questions_data:
            messagebox.showerror("Eroare", "Selectează un domeniu valid!")
            return

        questions = self.questions_data[selected][:self.num_var.get()]
        for q in questions:
            q["domain"] = selected

        QuizWindow(self, questions, mode, tlim)

    # ----------------------------------------------------------
    def show_progress_chart(self):
        """Desenează grafic progres."""
        try:
            path = os.path.join(os.path.dirname(__file__), "score_history.txt")
            if not os.path.exists(path):
                messagebox.showinfo("Info", "Nu există date de progres încă.")
                return

            domains, scores = [], []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 4:
                        domain, mode, total, pct = parts
                        domains.append(domain)
                        scores.append(float(pct))

            plt.figure(figsize=(8, 4))
            plt.title("Progresul scorurilor în timp")
            plt.plot(scores, marker="o", color="#00FFFF")
            plt.xlabel("Sesiune")
            plt.ylabel("Scor (%)")
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o problemă la afișarea graficului:\n{e}")

    # ----------------------------------------------------------
    def generate_pdf_report(self):
        """Generează raport PDF cu scorurile."""
        try:
            path = os.path.join(os.path.dirname(__file__), "score_history.txt")
            if not os.path.exists(path):
                messagebox.showinfo("Info", "Nu există date pentru raport PDF.")
                return

            pdf_dir = os.path.join(os.path.dirname(__file__), "../reports")
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, "FEA_Quiz_Report.pdf")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "FEA Quiz Report", ln=True, align="C")

            pdf.set_font("Arial", "", 12)
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    pdf.cell(0, 10, line.strip(), ln=True)

            pdf.output(pdf_path)
            messagebox.showinfo("Succes", f"Raport PDF generat:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generarea PDF:\n{e}")

    # ----------------------------------------------------------
    def show_stats(self):
        """Afișează medie scoruri."""
        try:
            path = os.path.join(os.path.dirname(__file__), "score_history.txt")
            if not os.path.exists(path):
                messagebox.showinfo("Info", "Nu există date pentru statistici.")
                return

            scores = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 4:
                        scores.append(float(parts[3]))

            if not scores:
                messagebox.showinfo("Info", "Nu există scoruri valide.")
                return

            avg = sum(scores) / len(scores)
            messagebox.showinfo("Statistici", f"Media scorurilor: {avg:.2f}%")

        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la calculul statisticilor:\n{e}")


# ----------------------------------------------------------
if __name__ == "__main__":
    app = FEATrainerApp()
    app.mainloop()
