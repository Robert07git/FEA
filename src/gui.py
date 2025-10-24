import tkinter as tk
from tkinter import ttk, messagebox
import time
import os

# Importuri cu protecție (în caz că unele fișiere lipsesc)
try:
    from quiz_logic import run_quiz
except ImportError:
    run_quiz = None

try:
    from export_pdf import generate_exam_report
except ImportError:
    generate_exam_report = None

try:
    from progress_chart import generate_progress_chart
except ImportError:
    generate_progress_chart = None

try:
    from stats import show_dashboard
except ImportError:
    show_dashboard = None


# ================= SPLASH SCREEN =================
class SplashScreen(tk.Toplevel):
    """Ecranul animat de pornire (logo + text + fade)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry("400x300+600+300")
        self.configure(bg="#111")
        self.attributes("-topmost", True)

        # Canvas pentru animație circulară
        self.canvas = tk.Canvas(self, width=120, height=120, bg="#111", highlightthickness=0)
        self.canvas.pack(pady=25)

        self.arc = self.canvas.create_arc(
            10, 10, 110, 110,
            start=0, extent=300,
            style="arc",
            outline="#00ffff",
            width=4
        )

        tk.Label(
            self, text="FEA Quiz Trainer",
            fg="#00ffff", bg="#111",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        self.loading_label = tk.Label(
            self, text="Se încarcă", fg="white", bg="#111",
            font=("Segoe UI", 11, "italic")
        )
        self.loading_label.pack(pady=10)

        self.progress = ttk.Progressbar(self, mode="indeterminate", length=250)
        self.progress.pack(pady=15)
        self.progress.start(10)

        self.angle = 0
        self.dot_count = 0
        self.animate_logo()
        self.animate_text()
        self.after(2500, self.fade_and_close)

    def animate_logo(self):
        """Animație de rotire a arcului circular."""
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        self.after(50, self.animate_logo)

    def animate_text(self):
        """Text animat 'Se încarcă...'."""
        self.dot_count = (self.dot_count + 1) % 4
        self.loading_label.config(text="Se încarcă" + "." * self.dot_count)
        self.after(400, self.animate_text)

    def fade_and_close(self):
        """Efect fade înainte de dispariție."""
        try:
            for i in range(10, -1, -1):
                self.attributes("-alpha", i / 10)
                self.update()
                time.sleep(0.05)
        except Exception:
            pass
        self.destroy()


# ================= MAIN APP =================
class FEAQuizApp(tk.Tk):
    """Aplicația principală pentru FEA Quiz Trainer."""

    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("850x650")
        self.configure(bg="#111")

        # Afișează splash screen
        self.withdraw()
        splash = SplashScreen(self)
        self.after(2600, lambda: [splash.destroy(), self.deiconify()])

        self.create_widgets()

    # ---------------- UI ----------------
    def create_widgets(self):
        tk.Label(
            self, text="Setări sesiune",
            fg="#00ffff", bg="#111",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        frame = tk.Frame(self, bg="#111")
        frame.pack(pady=5)

        tk.Label(frame, text="Domeniu:", fg="white", bg="#111").grid(row=0, column=0, sticky="w")
        self.domain_var = tk.StringVar(value="structural")
        tk.OptionMenu(frame, self.domain_var, "structural", "crash", "materials", "general").grid(row=0, column=1)

        tk.Label(frame, text="Număr întrebări:", fg="white", bg="#111").grid(row=1, column=0, sticky="w", pady=5)
        self.num_var = tk.IntVar(value=5)
        tk.Spinbox(frame, from_=1, to=50, width=5, textvariable=self.num_var).grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Mod:", fg="white", bg="#111").grid(row=2, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="train")
        tk.Radiobutton(frame, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train",
                       fg="white", bg="#111", selectcolor="#222").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame, text="EXAM (feedback la final)", variable=self.mode_var, value="exam",
                       fg="white", bg="#111", selectcolor="#222").grid(row=3, column=1, sticky="w")

        tk.Label(frame, text="Timp pe întrebare (sec, doar EXAM):", fg="white", bg="#111").grid(row=4, column=0, sticky="w")
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(frame, from_=5, to=120, width=5, textvariable=self.time_var).grid(row=4, column=1, pady=5)

        tk.Button(
            self, text="▶ Start Quiz", fg="black", bg="#00ffff",
            font=("Segoe UI", 10, "bold"),
            command=self.start_quiz
        ).pack(pady=20)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=15)

        tk.Label(
            self, text="Rapoarte & Analiză",
            fg="#00ffff", bg="#111",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=5)

        btn_frame = tk.Frame(self, bg="#111")
        btn_frame.pack()

        tk.Button(btn_frame, text="📊 Grafic progres", command=self.gen_chart, width=25, bg="#222", fg="white").pack(pady=3)
        tk.Button(btn_frame, text="📄 Generează PDF", command=self.gen_pdf, width=25, bg="#222", fg="white").pack(pady=3)
        tk.Button(btn_frame, text="📈 Statistici", command=self.show_stats, width=25, bg="#222", fg="white").pack(pady=3)

    # ---------------- Funcții acțiuni ----------------
    def start_quiz(self):
        domain = self.domain_var.get()
        num_q = self.num_var.get()
        mode = self.mode_var.get()
        tlim = self.time_var.get() if mode == "exam" else None

        if run_quiz:
            messagebox.showinfo("Start Quiz", f"Quiz început:\nDomeniu: {domain}\nÎntrebări: {num_q}\nMod: {mode}")
            # run_quiz(domain, num_q, mode, tlim)  # activează dacă vrei rulare directă
        else:
            messagebox.showwarning("Info", "Funcția de quiz nu este încă disponibilă în acest build.")

    def gen_chart(self):
        if generate_progress_chart:
            try:
                generate_progress_chart()
                messagebox.showinfo("Grafic", "📊 Graficul de progres a fost generat cu succes!")
            except Exception as e:
                messagebox.showerror("Eroare", str(e))
        else:
            messagebox.showwarning("Info", "Funcția progress_chart lipsește momentan.")

    def gen_pdf(self):
        if generate_exam_report:
            try:
                generate_exam_report()
                messagebox.showinfo("PDF", "📄 Raportul PDF a fost generat cu succes!")
            except Exception as e:
                messagebox.showerror("Eroare", str(e))
        else:
            messagebox.showwarning("Info", "Funcția export_pdf lipsește momentan.")

    def show_stats(self):
        if show_dashboard:
            try:
                show_dashboard()
            except Exception as e:
                messagebox.showerror("Eroare", str(e))
        else:
            messagebox.showwarning("Info", "Modulul stats lipsește momentan.")


# ================= MAIN =================
if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
