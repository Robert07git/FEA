import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import platform
import os
import json

from data_loader import load_questions
from stats import show_dashboard as show_stats
from export_pdf import main as export_pdf
from progress_chart import main as generate_chart


# ===== CONFIG PATH =====
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


def save_config(domain, num, mode, time_limit):
    config = {
        "domain": domain,
        "num_questions": num,
        "mode": mode,
        "time_limit": time_limit
    }
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print("Eroare la salvarea config:", e)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"domain": "structural", "num_questions": 5, "mode": "train", "time_limit": 15}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"domain": "structural", "num_questions": 5, "mode": "train", "time_limit": 15}


# ===== Funcție cross-platform pentru beep =====
def beep():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 300)
        else:
            os.system("printf '\\a'")
    except Exception:
        pass


# ============================= QUIZ WINDOW =============================
class QuizWindow(tk.Toplevel):
    def __init__(self, parent, domain, num_questions, mode, time_limit):
        super().__init__(parent)
        self.title("FEA Quiz - Sesiune Quiz")
        self.geometry("550x650")
        self.configure(bg="#111")

        self.domain = domain
        self.num_questions = num_questions
        self.mode = mode
        self.time_limit = time_limit

        self.questions = [q for q in load_questions() if q["domain"] == domain]
        if len(self.questions) < num_questions:
            messagebox.showwarning("Atenție", f"Există doar {len(self.questions)} întrebări în domeniul ales.")
            self.num_questions = len(self.questions)

        self.current_index = 0
        self.score = 0
        self.results = []
        self.remaining_time = self.time_limit
        self.timer_running = False

        self.create_widgets()
        self.show_question()

    def create_widgets(self):
        self.lbl_title = tk.Label(self, text=f"Domeniu: {self.domain} | Mod: {self.mode.upper()}",
                                  font=("Segoe UI", 11, "bold"), fg="#00ffff", bg="#111")
        self.lbl_title.pack(pady=8)

        self.lbl_timer = tk.Label(self, text="", font=("Segoe UI", 10, "bold"), fg="#00ff88", bg="#111")
        self.lbl_timer.pack(pady=3)

        self.progress_var = tk.DoubleVar(value=100)
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=320,
                                            variable=self.progress_var, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.lbl_question = tk.Label(self, text="", wraplength=500, justify="left",
                                     font=("Segoe UI", 10), fg="white", bg="#111")
        self.lbl_question.pack(pady=20)

        self.var_choice = tk.IntVar(value=-1)
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self, text="", variable=self.var_choice, value=i,
                                font=("Segoe UI", 10), fg="white", bg="#111",
                                selectcolor="#222", anchor="w", justify="left")
            rb.pack(fill="x", padx=25, pady=2)
            self.radio_buttons.append(rb)

        self.btn_submit = tk.Button(self, text="Răspunde / Finalizează", bg="#00bfff", fg="white",
                                    font=("Segoe UI", 10, "bold"), command=self.submit_answer)
        self.btn_submit.pack(pady=15)

        self.lbl_feedback = tk.Label(self, text="", wraplength=480, justify="left",
                                     font=("Segoe UI", 9, "italic"), fg="#ffb3b3", bg="#111")
        self.lbl_feedback.pack(pady=5)

        self.btn_close = tk.Button(self, text="Închide", bg="#333", fg="white",
                                   font=("Segoe UI", 9), command=self.destroy)
        self.btn_close.pack(pady=10)

    # --------------------------- Timer ---------------------------
    def start_timer(self):
        if self.mode != "exam" or self.time_limit <= 0:
            return
        self.remaining_time = self.time_limit
        self.progress_var.set(100)
        self.timer_running = True
        self.update_timer_label()
        threading.Thread(target=self._countdown_thread, daemon=True).start()

    def _countdown_thread(self):
        while self.remaining_time > 0 and self.timer_running:
            time.sleep(1)
            self.remaining_time -= 1
            percent = (self.remaining_time / self.time_limit) * 100
            self.progress_var.set(percent)
            self.update_timer_label()

            if self.remaining_time == 5:
                beep()

        if self.remaining_time <= 0 and self.timer_running:
            self.timer_running = False
            self.after(100, lambda: self.submit_answer(timeout=True))

    def update_timer_label(self):
        self.lbl_timer.config(text=f"Timp rămas: {self.remaining_time}s")
        if self.remaining_time <= 5:
            self.lbl_timer.config(fg="#ff4040")
        elif self.remaining_time <= 10:
            self.lbl_timer.config(fg="#ffcc00")
        else:
            self.lbl_timer.config(fg="#00ff88")

    # --------------------------- Logică întrebări ---------------------------
    def show_question(self):
        if self.current_index >= self.num_questions:
            self.show_result()
            return

        q = self.questions[self.current_index]
        self.lbl_question.config(text=f"Întrebarea {self.current_index + 1}/{self.num_questions}\n\n{q['question']}")
        for i, choice in enumerate(q["choices"]):
            self.radio_buttons[i].config(text=choice)
        self.var_choice.set(-1)
        self.lbl_feedback.config(text="")

        if self.mode == "exam":
            self.start_timer()

    def submit_answer(self, timeout=False):
        self.timer_running = False
        q = self.questions[self.current_index]
        correct_index = q["correct_index"]
        explanation = q["explanation"]

        chosen = self.var_choice.get()
        is_correct = (chosen == correct_index)

        if timeout:
            self.results.append((q, None, False, True))
        else:
            self.results.append((q, chosen, is_correct, False))
            if is_correct:
                self.score += 1

        if self.mode == "train":
            if timeout:
                self.lbl_feedback.config(text="⏰ Timp expirat!")
            elif is_correct:
                self.lbl_feedback.config(text="✅ Corect!\n" + explanation)
            else:
                self.lbl_feedback.config(
                    text=f"❌ Greșit.\nRăspuns corect: {correct_index + 1}. {q['choices'][correct_index]}\nExplicație: {explanation}"
                )

        self.current_index += 1
        self.after(1500 if self.mode == "train" else 500, self.show_question)

    # --------------------------- Rezultat final ---------------------------
    def show_result(self):
        self.timer_running = False
        pct = (self.score / self.num_questions) * 100 if self.num_questions > 0 else 0
        summary = f"=== REZULTAT FINAL ===\nScor: {self.score}/{self.num_questions}\nProcent: {pct:.1f}%\nMod: {self.mode.upper()}\n"

        if pct < 50:
            summary += "\nNu-i panică. Reia teoria de bază. Asta se învață 📘"
        else:
            summary += "\nExcelent! Se vede progresul 🚀"

        if self.mode == "exam":
            summary += "\n\nÎntrebări pentru revizuit:\n"
            for (q, chosen, correct, timeout) in self.results:
                if not correct:
                    summary += f"- {q['question']}\n  Răspuns corect: {q['choices'][q['correct_index']]}\n  Explicație: {q['explanation']}\n\n"

        self.lbl_question.config(text=summary)
        for rb in self.radio_buttons:
            rb.pack_forget()
        self.lbl_feedback.pack_forget()
        self.lbl_timer.pack_forget()
        self.progress_bar.pack_forget()
        self.btn_submit.config(state="disabled")


# ============================= FEREASTRĂ PRINCIPALĂ =============================
class FEAGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("950x700")
        self.configure(bg="#111")

        self.config_data = load_config()
        self.create_main_widgets()

    def create_main_widgets(self):
        title = tk.Label(self, text="Setări sesiune", font=("Segoe UI", 12, "bold"), fg="#00ffff", bg="#111")
        title.pack(pady=10)

        tk.Label(self, text="Domeniu:", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.domain_var = tk.StringVar(value=self.config_data.get("domain", "structural"))
        domain_box = ttk.Combobox(self, textvariable=self.domain_var, width=50,
                                  values=["structural", "crash", "moldflow", "cfd", "nvh", "mix"])
        domain_box.pack(pady=5)

        tk.Label(self, text="Număr întrebări:", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.num_var = tk.IntVar(value=self.config_data.get("num_questions", 5))
        tk.Spinbox(self, from_=1, to=50, textvariable=self.num_var, width=5).pack(pady=5)

        tk.Label(self, text="Mod:", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.mode_var = tk.StringVar(value=self.config_data.get("mode", "train"))
        tk.Radiobutton(self, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train",
                       bg="#111", fg="white", selectcolor="#222").pack()
        tk.Radiobutton(self, text="EXAM (limită timp, feedback la final)", variable=self.mode_var, value="exam",
                       bg="#111", fg="white", selectcolor="#222").pack()

        tk.Label(self, text="Timp per întrebare (secunde, doar EXAM):", font=("Segoe UI", 9, "bold"), fg="white", bg="#111").pack()
        self.time_var = tk.IntVar(value=self.config_data.get("time_limit", 15))
        tk.Spinbox(self, from_=5, to=120, textvariable=self.time_var, width=5).pack(pady=5)

        tk.Button(self, text="Start Quiz", bg="#00bfff", fg="white", font=("Segoe UI", 11, "bold"),
                  command=self.start_quiz).pack(pady=10)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        tk.Label(self, text="Rapoarte & Analiză", font=("Segoe UI", 11, "bold"), fg="#00ffff", bg="#111").pack(pady=5)
        tk.Button(self, text="Generează grafic progres (.png)", bg="#333", fg="white",
                  font=("Segoe UI", 10), command=self.run_chart).pack(pady=5)
        tk.Button(self, text="Generează PDF din ultimul EXAM", bg="#333", fg="white",
                  font=("Segoe UI", 10), command=self.run_pdf).pack(pady=5)
        tk.Button(self, text="Arată progres text (stats)", bg="#333", fg="white",
                  font=("Segoe UI", 10), command=self.run_stats).pack(pady=5)

    def start_quiz(self):
        domain = self.domain_var.get()
        num = self.num_var.get()
        mode = self.mode_var.get()
        time_per_q = self.time_var.get() if mode == "exam" else 0

        save_config(domain, num, mode, time_per_q)
        win = QuizWindow(self, domain, num, mode, time_per_q)
        win.grab_set()

    def run_chart(self):
        try:
            generate_chart()
            messagebox.showinfo("Succes", "Grafic generat cu succes! (progress_chart.png)")
        except Exception as e:
            messagebox.showerror("Eroare la grafic", str(e))

    def run_pdf(self):
        try:
            export_pdf()
            messagebox.showinfo("Succes", "PDF generat cu succes!")
        except Exception as e:
            messagebox.showerror("Eroare la PDF", str(e))

    def run_stats(self):
        try:
            show_stats()
        except Exception as e:
            messagebox.showerror("Eroare la statistici", str(e))


if __name__ == "__main__":
    app = FEAGui()
    app.mainloop()
