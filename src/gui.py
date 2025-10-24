import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
from quiz_logic import run_quiz
from export_pdf import generate_exam_report
from progress_chart import generate_progress_chart
from stats import show_dashboard


# ================= SPLASH SCREEN (animated + loading text) =================
import math

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry("400x300+600+300")
        self.configure(bg="#111")
        self.attributes("-topmost", True)

        # Canvas pentru logo-ul rotativ
        self.canvas = tk.Canvas(self, width=120, height=120, bg="#111", highlightthickness=0)
        self.canvas.pack(pady=25)

        self.arc = self.canvas.create_arc(
            10, 10, 110, 110,
            start=0, extent=300,
            style="arc",
            outline="#00ffff",
            width=4
        )

        # Titlu aplicație
        tk.Label(
            self, text="FEA Quiz Trainer",
            fg="#00ffff", bg="#111",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        # Text animat "Se încarcă..."
        self.loading_label = tk.Label(
            self, text="Se încarcă", fg="white", bg="#111",
            font=("Segoe UI", 11, "italic")
        )
        self.loading_label.pack(pady=10)

        # Progressbar
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=250)
        self.progress.pack(pady=15)
        self.progress.start(10)

        # Inițializare animații
        self.angle = 0
        self.dot_count = 0
        self.animate_logo()
        self.animate_text()

        # Auto-close after 2.5s
        self.after(2500, self.fade_and_close)

    def animate_logo(self):
        """Animare rotire logo (arc circular)."""
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        self.after(50, self.animate_logo)

    def animate_text(self):
        """Animare text „Se încarcă...” cu puncte care se adaugă."""
        self.dot_count = (self.dot_count + 1) % 4
        self.loading_label.config(text="Se încarcă" + "." * self.dot_count)
        self.after(400, self.animate_text)

    def fade_and_close(self):
        """Dispariție lină cu efect fade."""
        try:
            for i in range(10, -1, -1):
                self.attributes("-alpha", i / 10)
                self.update()
                time.sleep(0.05)
        except Exception:
            pass
        self.destroy()


# ==================== MAIN APPLICATION ====================

class FEAQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("850x650")
        self.configure(bg="#111")

        # Pornim splash screen
        self.withdraw()
        splash = SplashScreen(self)
        self.after(2600, lambda: [splash.destroy(), self.deiconify()])

        # Elemente UI
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self, text="Setări sesiune",
            fg="#00ffff", bg="#111",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)

        # Domeniu
        frame = tk.Frame(self, bg="#111")
        frame.pack(pady=5)

        tk.Label(frame, text="Domeniu:", fg="white", bg="#111").grid(row=0, column=0, sticky="w")
        self.domain_var = tk.StringVar(value="structural")
        tk.OptionMenu(frame, self.domain_var, "structural", "crash", "materials", "general").grid(row=0, column=1)

        # Număr întrebări
        tk.Label(frame, text="Număr întrebări:", fg="white", bg="#111").grid(row=1, column=0, sticky="w", pady=5)
        self.num_var = tk.IntVar(value=5)
        tk.Spinbox(frame, from_=1, to=50, width=5, textvariable=self.num_var).grid(row=1, column=1, pady=5)

        # Mod
        tk.Label(frame, text="Mod:", fg="white", bg="#111").grid(row=2, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="train")
        tk.Radiobutton(frame, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train",
                       fg="white", bg="#111", selectcolor="#222").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame, text="EXAM (feedback la final)", variable=self.mode_var, value="exam",
                       fg="white", bg="#111", selectcolor="#222").grid(row=3, column=1, sticky="w")

        # Timp per întrebare
        tk.Label(frame, text="Timp pe întrebare (sec, doar EXAM):", fg="white", bg="#111").grid(row=4, column=0, sticky="w")
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(frame, from_=5, to=120, width=5, textvariable=self.time_var).grid(row=4, column=1, pady=5)

        # Buton start
        tk.Button(
            self, text="▶ Start Quiz", fg="black", bg="#00ffff",
            font=("Segoe UI", 10, "bold"),
            command=self.start_quiz
        ).pack(pady=20)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=15)

        # Secțiunea de rapoarte
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

    # ---------------- Actions -----------------
    def start_quiz(self):
        domain = self.domain_var.get()
        num_q = self.num_var.get()
        mode = self.mode_var.get()
        tlim = self.time_var.get() if mode == "exam" else None

        messagebox.showinfo("Start Quiz", f"Quiz început:\nDomeniu: {domain}\nÎntrebări: {num_q}\nMod: {mode}")
        # Aici poți integra logica din quiz_logic.run_quiz dacă vrei rulare directă

    def gen_chart(self):
        try:
            generate_progress_chart()
            messagebox.showinfo("Grafic", "Graficul de progres a fost generat cu succes!")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def gen_pdf(self):
        try:
            generate_exam_report()
            messagebox.showinfo("PDF", "Raportul PDF a fost generat!")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def show_stats(self):
        try:
            show_dashboard()
        except Exception as e:
            messagebox.showerror("Eroare", str(e))


# ==================== MAIN ====================
if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
