import tkinter as tk
from tkinter import ttk, messagebox
from data_loader import load_questions
from quiz_logic import QuizWindow
from progress_chart import generate_progress_chart
from export_pdf import generate_exam_report
from stats import show_stats


class FEAQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("800x600")
        self.configure(bg="#111")

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self,
            text="Setări sesiune",
            font=("Segoe UI", 14, "bold"),
            bg="#111",
            fg="#00FFFF",
        )
        title.pack(pady=10)

        # Domeniu
        tk.Label(self, text="Domeniu:", bg="#111", fg="white").pack()
        self.domain_var = tk.StringVar(value="structural")
        self.domain_menu = ttk.Combobox(
            self, textvariable=self.domain_var, values=["structural", "crash", "moldflow", "CFD", "NVH"]
        )
        self.domain_menu.pack(pady=5)

        # Număr întrebări
        tk.Label(self, text="Număr întrebări:", bg="#111", fg="white").pack()
        self.num_var = tk.IntVar(value=5)
        tk.Spinbox(self, from_=1, to=50, textvariable=self.num_var, width=5).pack(pady=5)

        # Mod (TRAIN / EXAM)
        tk.Label(self, text="Mod:", bg="#111", fg="white").pack()
        self.mode_var = tk.StringVar(value="TRAIN")
        tk.Radiobutton(self, text="TRAIN (feedback imediat)", variable=self.mode_var, value="TRAIN", bg="#111", fg="white").pack()
        tk.Radiobutton(self, text="EXAM (limită timp, feedback final)", variable=self.mode_var, value="EXAM", bg="#111", fg="white").pack()

        # Timp per întrebare (doar pentru EXAM)
        tk.Label(self, text="Timp per întrebare (secunde, doar EXAM):", bg="#111", fg="white").pack(pady=3)
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(self, from_=5, to=120, textvariable=self.time_var, width=5).pack(pady=3)

        # Buton Start
        start_btn = tk.Button(
            self,
            text="▶ Start Quiz",
            command=self.start_quiz,
            bg="#00FFFF",
            fg="black",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=10,
            pady=5,
        )
        start_btn.pack(pady=10)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # Secțiunea Rapoarte & Analiză
        report_lbl = tk.Label(
            self,
            text="Rapoarte & Analiză",
            font=("Segoe UI", 12, "bold"),
            bg="#111",
            fg="#00FFFF",
        )
        report_lbl.pack(pady=10)

        tk.Button(self, text="📈 Grafic progres", command=self.show_progress, width=20).pack(pady=3)
        tk.Button(self, text="🧾 Generează PDF", command=self.generate_pdf, width=20).pack(pady=3)
        tk.Button(self, text="📊 Statistici", command=self.show_stats, width=20).pack(pady=3)

    # === FUNCȚII === #

    def start_quiz(self):
        domain = self.domain_var.get()
        num = self.num_var.get()
        mode = self.mode_var.get()
        tlim = self.time_var.get()

        # Încarcă întrebările din fișierul JSON
        questions = load_questions(domain)
        if not questions:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul '{domain}'!")
            return

        questions = questions[:num]
        # Deschide fereastra quiz (sincronizată cu QuizWindow din quiz_logic)
        QuizWindow(self, questions, mode, tlim)

    def show_progress(self):
        try:
            generate_progress_chart()
        except Exception as e:
            messagebox.showinfo("Info", f"Funcția progress_chart lipsește momentan.\n\n{e}")

    def generate_pdf(self):
        try:
            generate_exam_report()
        except Exception as e:
            messagebox.showinfo("Info", f"Funcția export_pdf lipsește momentan.\n\n{e}")

    def show_stats(self):
        try:
            show_stats()
        except Exception as e:
            messagebox.showinfo("Info", f"Eroare la stats:\n{e}")


if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
