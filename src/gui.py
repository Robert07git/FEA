import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import json
import random
import winsound
from PIL import Image, ImageTk, ImageFilter
from stats import load_history, summarize_by_domain
from data_loader import load_questions
from export_pdf import main as export_pdf
from progress_chart import main as generate_chart
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


# ============ CONFIG ============
def save_config(domain, num, mode, time_limit, theme):
    cfg = {"domain": domain, "num_questions": num, "mode": mode, "time_limit": time_limit, "theme": theme}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"domain": "structural", "num_questions": 5, "mode": "train", "time_limit": 15, "theme": "dark"}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"domain": "structural", "num_questions": 5, "mode": "train", "time_limit": 15, "theme": "dark"}


# ============ SUNETE ============
def sound_correct():
    winsound.Beep(1200, 150)


def sound_wrong():
    winsound.Beep(400, 250)


def sound_finish():
    winsound.Beep(800, 120)
    winsound.Beep(1200, 150)
    winsound.Beep(1500, 180)


# ============ SPLASH SCREEN ============
class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry("400x250+600+300")
        self.configure(bg="#111")
        self.attributes("-topmost", True)

        tk.Label(self, text="FEA Quiz Trainer", fg="#00ffff", bg="#111", font=("Segoe UI", 16, "bold")).pack(pady=40)
        tk.Label(self, text="Se încarcă...", fg="white", bg="#111", font=("Segoe UI", 11, "italic")).pack(pady=10)
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=250)
        self.progress.pack(pady=20)
        self.progress.start(10)
        self.after(2000, self.destroy)


# ============ QUIZ WINDOW ============
class QuizWindow(tk.Toplevel):
    def __init__(self, parent, domain, num_questions, mode, time_limit, theme_colors):
        super().__init__(parent)
        self.title("FEA Quiz - Sesiune")
        self.geometry("600x700")
        self.configure(bg=theme_colors["bg"])
        self.theme = theme_colors

        self.domain = domain
        self.num_questions = num_questions
        self.mode = mode
        self.time_limit = time_limit

        self.questions = [q for q in load_questions() if q["domain"] == domain]
        random.shuffle(self.questions)
        self.questions = self.questions[:num_questions]

        self.current = 0
        self.score = 0
        self.var_choice = tk.IntVar(value=-1)
        self.remaining_time = time_limit
        self.timer_running = False

        self.build_ui()
        self.show_question()

    def build_ui(self):
        tk.Label(self, text=f"Domeniu: {self.domain}", bg=self.theme["bg"], fg=self.theme["accent"],
                 font=("Segoe UI", 11, "bold")).pack(pady=10)

        self.timer_lbl = tk.Label(self, text="", bg=self.theme["bg"], fg=self.theme["text"], font=("Segoe UI", 10))
        self.timer_lbl.pack()

        self.bar = ttk.Progressbar(self, orient="horizontal", length=350, mode="determinate")
        self.bar.pack(pady=5)

        self.lbl_q = tk.Label(self, text="", wraplength=500, bg=self.theme["bg"], fg=self.theme["text"],
                              justify="left", font=("Segoe UI", 10))
        self.lbl_q.pack(pady=20)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self, text="", variable=self.var_choice, value=i,
                                bg=self.theme["bg"], fg=self.theme["text"], selectcolor="#222")
            rb.pack(fill="x", padx=30, pady=3)
            self.radio_buttons.append(rb)

        self.feedback = tk.Label(self, text="", bg=self.theme["bg"], fg="#ffcccc", wraplength=500,
                                 font=("Segoe UI", 9, "italic"))
        self.feedback.pack(pady=5)

        self.submit_btn = self.make_hover_button("Răspunde", self.submit_answer)
        self.submit_btn.pack(pady=10)
        tk.Button(self, text="Închide", bg="#333", fg="white", command=self.destroy).pack(pady=5)

    def make_hover_button(self, text, cmd):
        b = tk.Button(self, text=text, bg="#00bfff", fg="white", font=("Segoe UI", 10, "bold"), command=cmd)

        def on_enter(e): b.config(bg="#00ffff")
        def on_leave(e): b.config(bg="#00bfff")
        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        return b

    def start_timer(self):
        if self.mode != "exam":
            return
        self.remaining_time = self.time_limit
        self.bar["value"] = 100
        self.timer_running = True
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def _timer_loop(self):
        while self.remaining_time > 0 and self.timer_running:
            time.sleep(1)
            self.remaining_time -= 1
            self.after(0, self.update_timer)
        if self.remaining_time <= 0 and self.timer_running:
            self.after(0, lambda: self.submit_answer(timeout=True))

    def update_timer(self):
        self.timer_lbl.config(text=f"Timp rămas: {self.remaining_time}s")
        pct = (self.remaining_time / self.time_limit) * 100
        self.bar["value"] = pct
        if self.remaining_time <= 5:
            self.timer_lbl.config(fg="#ff4040")

    def show_question(self):
        if self.current >= self.num_questions:
            self.show_result()
            return
        q = self.questions[self.current]
        self.lbl_q.config(text=f"Întrebarea {self.current + 1}/{self.num_questions}\n\n{q['question']}")
        for i, c in enumerate(q["choices"]):
            self.radio_buttons[i].config(text=c)
        self.var_choice.set(-1)
        self.feedback.config(text="")
        self.start_timer()

    def submit_answer(self, timeout=False):
        self.timer_running = False
        q = self.questions[self.current]
        correct = q["correct_index"]
        chosen = self.var_choice.get()
        explanation = q["explanation"]

        if timeout:
            self.feedback.config(text="⏰ Timp expirat!")
            sound_wrong()
        elif chosen == correct:
            self.score += 1
            sound_correct()
            self.feedback.config(text=f"✅ Corect!\n{explanation}")
        else:
            sound_wrong()
            self.feedback.config(text=f"❌ Greșit.\nRăspuns corect: {correct + 1}. {q['choices'][correct]}\n{explanation}")

        self.current += 1
        self.after(1500, self.show_question)

    def show_result(self):
        sound_finish()
        pct = (self.score / self.num_questions) * 100
        msg = f"=== REZULTAT FINAL ===\nScor: {self.score}/{self.num_questions}\nProcent: {pct:.1f}%"
        self.lbl_q.config(text=msg)
        for rb in self.radio_buttons:
            rb.pack_forget()
        self.submit_btn.pack_forget()
        self.feedback.config(text="Felicitări! Completează mai multe teste pentru progres.")


# ============ MAIN GUI ============
class FEAGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.config_data = load_config()
        self.theme = self.load_theme()

        # FIX — creăm background după inițializare completă
        self.after(50, self.make_background)
        self.after(100, self.build_ui)

    def load_theme(self):
        if self.config_data.get("theme", "dark") == "light":
            return {"bg": "#f2f2f2", "text": "#111", "accent": "#007acc"}
        else:
            return {"bg": "#111", "text": "white", "accent": "#00ffff"}

    def make_background(self):
        width, height = 1000, 700
        gradient = Image.new("RGBA", (width, height))
        for y in range(height):
            c = int(20 + (y / height) * 40)
            for x in range(width):
                gradient.putpixel((x, y), (0, c, c + 20, 255))
        blurred = gradient.filter(ImageFilter.GaussianBlur(3))
        self.bg_img = ImageTk.PhotoImage(blurred)
        bg_lbl = tk.Label(self, image=self.bg_img)
        bg_lbl.place(relwidth=1, relheight=1)

    def build_ui(self):
        f = tk.Frame(self, bg=self.theme["bg"])
        f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f, text="Setări sesiune", bg=self.theme["bg"], fg=self.theme["accent"], font=("Segoe UI", 12, "bold")).pack(pady=10)

        tk.Label(f, text="Domeniu:", bg=self.theme["bg"], fg=self.theme["text"]).pack()
        self.domain_var = tk.StringVar(value=self.config_data["domain"])
        ttk.Combobox(f, textvariable=self.domain_var, values=["structural", "crash", "nvh", "cfd", "moldflow", "mix"], width=40).pack(pady=5)

        tk.Label(f, text="Număr întrebări:", bg=self.theme["bg"], fg=self.theme["text"]).pack()
        self.num_var = tk.IntVar(value=self.config_data["num_questions"])
        tk.Spinbox(f, from_=1, to=50, textvariable=self.num_var, width=5).pack(pady=5)

        tk.Label(f, text="Mod:", bg=self.theme["bg"], fg=self.theme["text"]).pack()
        self.mode_var = tk.StringVar(value=self.config_data["mode"])
        tk.Radiobutton(f, text="TRAIN", variable=self.mode_var, value="train", bg=self.theme["bg"], fg=self.theme["text"], selectcolor="#222").pack()
        tk.Radiobutton(f, text="EXAM", variable=self.mode_var, value="exam", bg=self.theme["bg"], fg=self.theme["text"], selectcolor="#222").pack()

        tk.Label(f, text="Timp pe întrebare (secunde, doar EXAM):", bg=self.theme["bg"], fg=self.theme["text"]).pack()
        self.time_var = tk.IntVar(value=self.config_data["time_limit"])
        tk.Spinbox(f, from_=5, to=120, textvariable=self.time_var, width=5).pack(pady=5)

        self.make_hover_button(f, "▶ Start Quiz", self.start_quiz, "#00bfff").pack(pady=10)
        ttk.Separator(f, orient="horizontal").pack(fill="x", pady=10)

        tk.Button(f, text="📊 Grafic progres", bg="#333", fg="white", command=self.run_chart).pack(pady=3)
        tk.Button(f, text="📄 Generează PDF", bg="#333", fg="white", command=self.run_pdf).pack(pady=3)
        tk.Button(f, text="📈 Statistici", bg="#333", fg="white", command=self.show_stats_panel).pack(pady=3)

        tk.Button(f, text=f"🌗 Schimbă temă ({self.config_data.get('theme','dark').capitalize()})", bg="#222", fg="white", command=self.toggle_theme).pack(pady=8)

    def make_hover_button(self, parent, text, cmd, color):
        b = tk.Button(parent, text=text, bg=color, fg="white", font=("Segoe UI", 10, "bold"), command=cmd)
        def on_enter(e): b.config(bg="#00ffff")
        def on_leave(e): b.config(bg=color)
        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        return b

    def toggle_theme(self):
        new_theme = "light" if self.config_data.get("theme", "dark") == "dark" else "dark"
        self.config_data["theme"] = new_theme
        save_config(self.domain_var.get(), self.num_var.get(), self.mode_var.get(), self.time_var.get(), new_theme)
        messagebox.showinfo("Temă schimbată", f"A fost selectată tema: {new_theme.capitalize()}\nRepornește aplicația pentru efect complet.")

    def start_quiz(self):
        domain = self.domain_var.get()
        num = self.num_var.get()
        mode = self.mode_var.get()
        t = self.time_var.get() if mode == "exam" else 0
        save_config(domain, num, mode, t, self.config_data["theme"])
        QuizWindow(self, domain, num, mode, t, self.theme).grab_set()

    def show_stats_panel(self):
        entries = load_history()
        stats = summarize_by_domain(entries)
        if not stats:
            messagebox.showinfo("Statistici", "Nu există date.")
            return
        win = tk.Toplevel(self)
        win.title("Statistici")
        win.geometry("600x400")
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=self.theme["bg"])
        doms = list(stats.keys())
        avgs = [v["avg_pct"] for v in stats.values()]
        bars = ax.bar(doms, avgs, color=self.theme["accent"])
        ax.set_facecolor(self.theme["bg"])
        ax.tick_params(colors=self.theme["text"])
        ax.set_title("Performanță pe domenii", color=self.theme["accent"])
        for b, v in zip(bars, avgs):
            ax.text(b.get_x()+b.get_width()/2, v+1, f"{v:.1f}%", ha="center", color=self.theme["text"])
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def run_chart(self):
        generate_chart()
        messagebox.showinfo("Succes", "Grafic generat!")

    def run_pdf(self):
        export_pdf()
        messagebox.showinfo("Succes", "PDF generat!")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    splash = SplashScreen(root)
    splash.wait_window()
    root.deiconify()
    app = FEAGui()
    app.mainloop()
