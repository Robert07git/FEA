import tkinter as tk
from tkinter import messagebox
from quiz_logic import run_quiz
from progress_chart import generate_progress_chart
from export_pdf import generate_exam_report
from stats import show_dashboard

class FEAQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("600x650")
        self.configure(bg="#111")

        self.create_ui()

    def create_ui(self):
        title = tk.Label(self, text="Setări sesiune", font=("Segoe UI", 14, "bold"), fg="#00ffff", bg="#111")
        title.pack(pady=10)

        # Domenii
        self.domain_var = tk.StringVar(value="structural")
        tk.Label(self, text="Domeniu:", fg="white", bg="#111").pack()
        domains = ["structural", "crash", "moldflow", "CFD", "NVH"]
        self.domain_menu = tk.OptionMenu(self, self.domain_var, *domains)
        self.domain_menu.pack()

        # Număr întrebări
        tk.Label(self, text="Număr întrebări:", fg="white", bg="#111").pack(pady=(10, 0))
        self.num_q = tk.Spinbox(self, from_=1, to=50, width=5)
        self.num_q.pack()

        # Mod (TRAIN / EXAM)
        tk.Label(self, text="Mod:", fg="white", bg="#111").pack(pady=(10, 0))
        self.mode_var = tk.StringVar(value="train")
        tk.Radiobutton(self, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train", bg="#111", fg="white").pack()
        tk.Radiobutton(self, text="EXAM (timp limită, feedback final)", variable=self.mode_var, value="exam", bg="#111", fg="white").pack()

        # Timp per întrebare (doar pentru EXAM)
        tk.Label(self, text="Timp per întrebare (secunde, doar EXAM):", fg="white", bg="#111").pack(pady=(10, 0))
        self.time_limit = tk.Spinbox(self, from_=5, to=60, width=5)
        self.time_limit.pack()

        tk.Button(self, text="▶ Start Quiz", bg="#00ffff", fg="black", command=self.start_quiz).pack(pady=15)

        tk.Frame(self, height=2, bg="#00ffff").pack(fill="x", pady=10)

        # Secțiunea rapoarte
        tk.Label(self, text="Rapoarte & Analiză", font=("Segoe UI", 13, "bold"), fg="#00ffff", bg="#111").pack(pady=5)
        tk.Button(self, text="📈 Grafic progres", command=self.generate_chart).pack(pady=5)
        tk.Button(self, text="📄 Generează PDF", command=self.generate_pdf).pack(pady=5)
        tk.Button(self, text="📊 Statistici", command=self.show_stats).pack(pady=5)

    def start_quiz(self):
        domain = self.domain_var.get()
        num = int(self.num_q.get())
        mode = self.mode_var.get()
        tlim = int(self.time_limit.get()) if mode == "exam" else None

        messagebox.showinfo("Start Quiz", f"Quiz început:\nDomeniu: {domain}\nÎntrebări: {num}\nMod: {mode}")
        run_quiz(domain, num, mode, tlim)

    def generate_chart(self):
        try:
            generate_progress_chart()
            messagebox.showinfo("Succes", "Graficul a fost generat: progress_chart.png")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def generate_pdf(self):
        try:
            generate_exam_report()
            messagebox.showinfo("Succes", "Raport PDF generat cu succes.")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def show_stats(self):
        try:
            show_dashboard()
        except Exception as e:
            messagebox.showerror("Eroare", str(e))


if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
