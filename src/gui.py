import os
import tkinter as tk
from tkinter import ttk, messagebox
from quiz_logic import QuizWindow
from progress_chart import generate_progress_chart
from export_pdf import generate_exam_report
from stats import show_dashboard

class FEAQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("920x580")
        self.configure(bg="#111")
        self.resizable(False, False)

        # Splash animation
        self.after(300, self.show_splash)

    # ==========================
    # SPLASH SCREEN
    # ==========================
    def show_splash(self):
        splash = tk.Toplevel(self)
        splash.geometry("920x580")
        splash.overrideredirect(True)
        splash.configure(bg="#000")

        lbl = tk.Label(splash, text="FEA Quiz Trainer", fg="#00FFFF", bg="#000",
                       font=("Segoe UI", 32, "bold"))
        lbl.pack(expand=True)

        bar = ttk.Progressbar(splash, length=300, mode="determinate")
        bar.pack(pady=40)
        for i in range(0, 101, 5):
            splash.update_idletasks()
            bar['value'] = i
            self.after(25)
        splash.destroy()
        self.build_main_ui()

    # ==========================
    # MAIN INTERFACE
    # ==========================
    def build_main_ui(self):
        frm = tk.Frame(self, bg="#111")
        frm.pack(expand=True)

        title = tk.Label(frm, text="Setări sesiune", fg="#00FFFF", bg="#111",
                         font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        tk.Label(frm, text="Domeniu:", bg="#111", fg="white").grid(row=1, column=0, sticky="e")
        self.domain_var = tk.StringVar(value="structural")
        domain_menu = ttk.Combobox(frm, textvariable=self.domain_var,
                                   values=["structural", "crash", "moldflow", "CFD", "NVH"])
        domain_menu.grid(row=1, column=1, pady=5)

        tk.Label(frm, text="Număr întrebări:", bg="#111", fg="white").grid(row=2, column=0, sticky="e")
        self.num_var = tk.IntVar(value=5)
        tk.Spinbox(frm, from_=1, to=20, textvariable=self.num_var, width=5).grid(row=2, column=1)

        tk.Label(frm, text="Mod:", bg="#111", fg="white").grid(row=3, column=0, sticky="e")

        self.mode_var = tk.StringVar(value="train")
        tk.Radiobutton(frm, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train",
                       bg="#111", fg="white", selectcolor="#222").grid(row=3, column=1, sticky="w")
        tk.Radiobutton(frm, text="EXAM (limită timp, feedback final)", variable=self.mode_var, value="exam",
                       bg="#111", fg="white", selectcolor="#222").grid(row=4, column=1, sticky="w")

        tk.Label(frm, text="Timp per întrebare (secunde, doar EXAM):", bg="#111", fg="white").grid(row=5, column=0, sticky="e")
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(frm, from_=5, to=60, textvariable=self.time_var, width=5).grid(row=5, column=1)

        tk.Button(frm, text="▶ Start Quiz", command=self.start_quiz,
                  bg="#00FFFF", fg="#111", font=("Segoe UI", 11, "bold")).grid(row=6, column=0, columnspan=2, pady=15)

        ttk.Separator(frm, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)

        tk.Label(frm, text="Rapoarte & Analiză", fg="#00FFFF", bg="#111",
                 font=("Segoe UI", 12, "bold")).grid(row=8, column=0, columnspan=2)

        tk.Button(frm, text="📈 Grafic progres", command=self.show_chart,
                  bg="#222", fg="white").grid(row=9, column=0, columnspan=2, pady=4)
        tk.Button(frm, text="📄 Generează PDF", command=self.export_pdf,
                  bg="#222", fg="white").grid(row=10, column=0, columnspan=2, pady=4)
        tk.Button(frm, text="📊 Statistici", command=self.show_stats,
                  bg="#222", fg="white").grid(row=11, column=0, columnspan=2, pady=4)

    # ==========================
    # BUTTON FUNCTIONS
    # ==========================
    def start_quiz(self):
        domain = self.domain_var.get()
        num = self.num_var.get()
        mode = self.mode_var.get()
        tlim = self.time_var.get() if mode == "exam" else None

        self.withdraw()
        QuizWindow(self, domain, num, mode, tlim)

    def show_chart(self):
        try:
            generate_progress_chart()
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu pot genera graficul:\n{e}")

    def export_pdf(self):
        try:
            generate_exam_report()
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu pot genera PDF:\n{e}")

    def show_stats(self):
        show_dashboard()


if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
