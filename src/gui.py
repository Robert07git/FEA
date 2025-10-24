import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import platform
import os
import json
import random
import winsound
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_loader import load_questions
from stats import load_history, summarize_by_domain
from export_pdf import main as export_pdf
from progress_chart import main as generate_chart


# ==================== CONFIG ====================

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def save_config(domain, num, mode, time_limit):
    cfg = {"domain": domain, "num_questions": num, "mode": mode, "time_limit": time_limit}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"domain": "structural", "num_questions": 5, "mode": "train", "time_limit": 15}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"domain": "structural", "num_questions": 5, "mode": "train", "time_limit": 15}


# ==================== SUNETE ====================

def sound_correct():
    winsound.Beep(1200, 150)

def sound_wrong():
    winsound.Beep(400, 300)

def sound_finish():
    winsound.Beep(900, 150)
    winsound.Beep(1200, 150)
    winsound.Beep(1500, 200)


# ==================== QUIZ WINDOW ====================

class QuizWindow(tk.Toplevel):
    def __init__(self, parent, domain, num_questions, mode, time_limit):
        super().__init__(parent)
        self.title("FEA Quiz - Sesiune")
        self.geometry("600x700")
        self.configure(bg="#111")

        self.domain = domain
        self.num_questions = num_questions
        self.mode = mode
        self.time_limit = time_limit

        self.questions = [q for q in load_questions() if q["domain"] == domain]
        random.shuffle(self.questions)
        self.questions = self.questions[:num_questions]

        self.current = 0
        self.score = 0
        self.results = []
        self.remaining_time = self.time_limit
        self.timer_running = False

        self.var_choice = tk.IntVar(value=-1)

        self.build_ui()
        self.show_question()

    def build_ui(self):
        tk.Label(self, text=f"Domeniu: {self.domain}", bg="#111", fg="#00ffff", font=("Segoe UI", 11, "bold")).pack(pady=10)

        self.timer_lbl = tk.Label(self, text="", bg="#111", fg="#00ff99", font=("Segoe UI", 10, "bold"))
        self.timer_lbl.pack()

        self.bar = ttk.Progressbar(self, orient="horizontal", length=350, mode="determinate")
        self.bar.pack(pady=5)

        self.lbl_q = tk.Label(self, text="", wraplength=500, bg="#111", fg="white", justify="left", font=("Segoe UI", 10))
        self.lbl_q.pack(pady=20)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self, text="", variable=self.var_choice, value=i, bg="#111", fg="white",
                                selectcolor="#222", font=("Segoe UI", 10), anchor="w", justify="left")
            rb.pack(fill="x", padx=30, pady=2)
            self.radio_buttons.append(rb)

        self.feedback = tk.Label(self, text="", wraplength=500, bg="#111", fg="#ffcccc", font=("Segoe UI", 9, "italic"))
        self.feedback.pack(pady=5)

        self.submit_btn = tk.Button(self, text="Răspunde", bg="#00bfff", fg="white", font=("Segoe UI", 10, "bold"),
                                    command=self.submit_answer)
        self.submit_btn.pack(pady=10)
        self.close_btn = tk.Button(self, text="Închide", bg="#333", fg="white", command=self.destroy)
        self.close_btn.pack(pady=5)

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
            self.timer_running = False
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
        correct_index = q["correct_index"]
        explanation = q["explanation"]
        chosen = self.var_choice.get()

        if timeout:
            self.feedback.config(text="⏰ Timp expirat!")
            sound_wrong()
            self.results.append((q, None, False, True))
        else:
            correct = (chosen == correct_index)
            if correct:
                self.score += 1
                sound_correct()
                self.feedback.config(text=f"✅ Corect!\n{explanation}")
            else:
                sound_wrong()
                self.feedback.config(text=f"❌ Greșit.\nRăspuns corect: {correct_index+1}. {q['choices'][correct_index]}\n{explanation}")
            self.results.append((q, chosen, correct, False))

        self.current += 1
        self.after(1500, self.show_question)

    def show_result(self):
        sound_finish()
        pct = (self.score / self.num_questions) * 100
        msg = f"=== REZULTAT FINAL ===\nScor: {self.score}/{self.num_questions}\nProcent: {pct:.1f}%\nMod: {self.mode.upper()}"
        if pct < 50:
            msg += "\n📘 Reia teoria de bază. Se poate mai bine!"
        else:
            msg += "\n🚀 Excelent! Se vede progresul."
        self.lbl_q.config(text=msg)
        for rb in self.radio_buttons:
            rb.pack_forget()
        self.feedback.pack_forget()
        self.timer_lbl.pack_forget()
        self.bar.pack_forget()
        self.submit_btn.pack_forget()


# ==================== MAIN GUI ====================

class FEAGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("1000x700")

        # Background gradient (Pillow)
        width, height = 1920, 1080
        gradient = Image.new("RGB", (width, height), color=0)
        for y in range(height):
            level = int(25 + (y / height) * 60)
            for x in range(width):
                gradient.putpixel((x, y), (level, level, level))
        self.bg_image = ImageTk.PhotoImage(gradient)
        bg_label = tk.Label(self, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)

        self.main_frame = tk.Frame(self, bg="#111")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.config_data = load_config()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.main_frame, text="Setări sesiune", fg="#00ffff", bg="#111", font=("Segoe UI", 12, "bold")).pack(pady=10)

        tk.Label(self.main_frame, text="Domeniu:", bg="#111", fg="white").pack()
        self.domain_var = tk.StringVar(value=self.config_data["domain"])
        ttk.Combobox(self.main_frame, textvariable=self.domain_var, values=["structural","crash","cfd","nvh","moldflow","mix"], width=40).pack(pady=5)

        tk.Button(self.main_frame, text="🔍 Vezi câte întrebări există", bg="#333", fg="white",
                  command=self.preview_questions).pack(pady=5)

        tk.Label(self.main_frame, text="Număr întrebări:", bg="#111", fg="white").pack()
        self.num_var = tk.IntVar(value=self.config_data["num_questions"])
        tk.Spinbox(self.main_frame, from_=1, to=50, textvariable=self.num_var, width=5).pack(pady=5)

        tk.Label(self.main_frame, text="Mod:", bg="#111", fg="white").pack()
        self.mode_var = tk.StringVar(value=self.config_data["mode"])
        tk.Radiobutton(self.main_frame, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train", bg="#111", fg="white", selectcolor="#222").pack()
        tk.Radiobutton(self.main_frame, text="EXAM (limită timp)", variable=self.mode_var, value="exam", bg="#111", fg="white", selectcolor="#222").pack()

        tk.Label(self.main_frame, text="Timp per întrebare (secunde, doar EXAM):", bg="#111", fg="white").pack()
        self.time_var = tk.IntVar(value=self.config_data["time_limit"])
        tk.Spinbox(self.main_frame, from_=5, to=120, textvariable=self.time_var, width=5).pack(pady=5)

        tk.Button(self.main_frame, text="▶ Start Quiz", bg="#00bfff", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.start_quiz).pack(pady=10)

        ttk.Separator(self.main_frame, orient="horizontal").pack(fill="x", pady=10)
        tk.Label(self.main_frame, text="Rapoarte & Analiză", bg="#111", fg="#00ffff", font=("Segoe UI", 11, "bold")).pack()

        tk.Button(self.main_frame, text="📊 Grafic progres", bg="#333", fg="white", command=self.run_chart).pack(pady=5)
        tk.Button(self.main_frame, text="📄 Generează PDF", bg="#333", fg="white", command=self.run_pdf).pack(pady=5)
        tk.Button(self.main_frame, text="📈 Vizualizează statistici", bg="#333", fg="white", command=self.show_stats_panel).pack(pady=5)

    def preview_questions(self):
        all_q = load_questions()
        counts = {}
        for q in all_q:
            dom = q["domain"]
            counts[dom] = counts.get(dom, 0) + 1
        msg = "\n".join(f"{dom}: {cnt} întrebări" for dom, cnt in counts.items())
        messagebox.showinfo("Întrebări disponibile", msg)

    def show_stats_panel(self):
        entries = load_history()
        stats = summarize_by_domain(entries)
        if not stats:
            messagebox.showinfo("Statistici", "Nu există date salvate.")
            return

        win = tk.Toplevel(self)
        win.title("Statistici Vizuale")
        win.geometry("600x400")

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#111")
        doms = list(stats.keys())
        avgs = [v["avg_pct"] for v in stats.values()]
        bars = ax.bar(doms, avgs, color="#00ccff")
        ax.set_facecolor("#111")
        ax.set_title("Performanță pe domenii", color="white")
        ax.set_ylabel("Scor mediu (%)", color="white")
        ax.tick_params(colors="white")
        for b, v in zip(bars, avgs):
            ax.text(b.get_x()+b.get_width()/2, v+1, f"{v:.1f}%", ha="center", color="white")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def start_quiz(self):
        domain = self.domain_var.get()
        num = self.num_var.get()
        mode = self.mode_var.get()
        time_q = self.time_var.get() if mode == "exam" else 0
        save_config(domain, num, mode, time_q)
        QuizWindow(self, domain, num, mode, time_q).grab_set()

    def run_chart(self):
        generate_chart()
        messagebox.showinfo("Succes", "Grafic generat!")

    def run_pdf(self):
        export_pdf()
        messagebox.showinfo("Succes", "PDF generat!")


if __name__ == "__main__":
    app = FEAGui()
    app.mainloop()
