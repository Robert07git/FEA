import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from data_loader import load_questions, get_domains
from quiz_logic import QuizSession
from progress_chart import show_progress_chart
from export_pdf import export_quiz_pdf
from stats import show_dashboard


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FEA Quiz Trainer")
        self.root.geometry("850x650")
        self.root.configure(bg="#111")
        self.root.resizable(False, False)

        self.domains = get_domains()
        if not self.domains:
            self.domains = ["structural", "crash", "moldflow", "cfd", "nvh", "mix"]

        self.questions = []
        self.session = None
        self.time_remaining = 0
        self.timer_job = None
        self.timer_label = None  # ✅ prevenim AttributeError

        self.create_main_menu()

    # ===================== MENIU PRINCIPAL =====================
    def create_main_menu(self):
        self.clear_window()
        tk.Label(
            self.root, text="FEA QUIZ TRAINER",
            font=("Arial", 22, "bold"), bg="#111", fg="#00ffff"
        ).pack(pady=25)

        # Domeniu
        tk.Label(self.root, text="Alege domeniul:", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.domain_var = tk.StringVar(value="mix")
        ttk.Combobox(
            self.root, textvariable=self.domain_var, values=self.domains, state="readonly", width=20
        ).pack(pady=10)

        # Număr întrebări
        tk.Label(self.root, text="Număr întrebări:", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.num_questions_var = tk.IntVar(value=5)
        tk.Spinbox(self.root, from_=1, to=50, textvariable=self.num_questions_var, width=6).pack(pady=5)

        # Timp per întrebare
        tk.Label(self.root, text="Timp per întrebare (secunde):", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.time_limit_var = tk.IntVar(value=10)
        tk.Spinbox(self.root, from_=5, to=120, textvariable=self.time_limit_var, width=6).pack(pady=5)

        # Moduri
        tk.Label(self.root, text="Mod de testare:", bg="#111", fg="white", font=("Arial", 12)).pack(pady=(10, 0))
        self.mode_var = tk.StringVar(value="train")
        mode_frame = tk.Frame(self.root, bg="#111")
        mode_frame.pack()
        tk.Radiobutton(mode_frame, text="TRAIN (feedback imediat)", variable=self.mode_var, value="train",
                       bg="#111", fg="cyan", selectcolor="#111").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="EXAM (feedback final)", variable=self.mode_var, value="exam",
                       bg="#111", fg="orange", selectcolor="#111").pack(side=tk.LEFT, padx=10)

        # Start
        tk.Button(self.root, text="Start Quiz", command=self.start_quiz,
                  font=("Arial", 13, "bold"), bg="#00cccc", fg="black").pack(pady=25)

        # Alte butoane
        btn_frame = tk.Frame(self.root, bg="#111")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="📊 Grafic progres", command=show_progress_chart, bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📈 Statistici", command=show_dashboard, bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📄 Export PDF", command=export_quiz_pdf, bg="#222", fg="white").pack(side=tk.LEFT, padx=5)

    # ===================== START QUIZ =====================
    def start_quiz(self):
        domain = self.domain_var.get()
        mode = self.mode_var.get()
        num_q = self.num_questions_var.get()
        time_limit = self.time_limit_var.get()

        questions = load_questions(domain)
        if not questions:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul '{domain}'.")
            return

        random.shuffle(questions)
        questions = questions[:num_q]

        self.session = QuizSession(self, questions, mode, time_limit)
        self.session.run()

    # ===================== ARATĂ ÎNTREBARE =====================
    def show_question(self):
        self.clear_window()
        q = self.session.current_question()
        idx = self.session.index + 1
        total = len(self.session.questions)

        tk.Label(self.root, text=f"Întrebarea {idx}/{total}:", bg="#111", fg="white", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        tk.Label(self.root, text=q["question"], bg="#111", fg="#00ffff", font=("Arial", 13, "bold"), wraplength=780, justify="center").pack(pady=10)

        self.answer_var = tk.IntVar(value=-1)
        for i, choice in enumerate(q["choices"]):
            tk.Radiobutton(
                self.root, text=choice, variable=self.answer_var, value=i,
                bg="#111", fg="white", selectcolor="#111", activebackground="#222",
                font=("Arial", 11), anchor="w", justify="left", wraplength=780
            ).pack(pady=2, anchor="w", padx=40)

        # Progres bar
        progress_frame = tk.Frame(self.root, bg="#111")
        progress_frame.pack(pady=10)
        pct = (idx - 1) / total
        progress = ttk.Progressbar(progress_frame, length=600, mode="determinate")
        progress["value"] = pct * 100
        progress.pack()
        tk.Label(progress_frame, text=f"Progres: {pct * 100:.0f}%", bg="#111", fg="white", font=("Arial", 10)).pack()

        # Timer
        self.timer_label = tk.Label(self.root, text="", bg="#111", fg="cyan", font=("Arial", 11, "bold"))
        self.timer_label.pack(pady=(5, 0))
        self.start_timer(self.session.time_limit)

        # Buton "Următoarea"
        tk.Button(self.root, text="Următoarea ➜", command=self.submit_answer,
                  font=("Arial", 12, "bold"), bg="#00cccc", fg="black").pack(pady=10)

    # ===================== TIMER =====================
    def start_timer(self, seconds):
        self.stop_timer()
        self.time_remaining = seconds
        if not self.timer_label or not hasattr(self.timer_label, "config"):
            self.timer_label = tk.Label(self.root, text="", bg="#111", fg="cyan", font=("Arial", 11, "bold"))
            self.timer_label.pack(pady=(5, 0))
        self.session.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.session or not self.session.timer_running:
            return
        if not hasattr(self, "timer_label") or not self.timer_label.winfo_exists():
            return  # dacă widgetul a fost distrus, ieșim

        self.timer_label.config(text=f"Timp rămas: {self.time_remaining}s")
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_job = self.root.after(1000, self.update_timer)
        else:
            self.submit_answer(timeout=True)

    def stop_timer(self):
        if self.timer_job:
            try:
                self.root.after_cancel(self.timer_job)
            except Exception:
                pass
        self.timer_job = None

    # ===================== RĂSPUNS =====================
    def submit_answer(self, timeout=False):
        answer = self.answer_var.get()
        if answer == -1 and not timeout:
            messagebox.showinfo("Info", "Selectează un răspuns înainte de a continua.")
            return

        self.session.timer_running = False
        if timeout:
            self.session.answer(-1)
        else:
            self.session.answer(answer)

    # ===================== FEEDBACK TRAIN =====================
    def show_train_feedback(self, correct, msg):
        self.clear_window()
        color = "lime" if correct else "red"
        tk.Label(self.root, text="Feedback:", bg="#111", fg="white", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Message(self.root, text=msg, bg="#111", fg=color, font=("Arial", 12), width=700, justify="left").pack(pady=10)
        tk.Button(self.root, text="Continuă ➜", command=self.session.next_question,
                  bg="#00cccc", fg="black", font=("Arial", 12, "bold")).pack(pady=10)

    # ===================== FEEDBACK EXAM =====================
    def show_exam_summary(self, results, correct_count, total, pct, duration):
        self.clear_window()
        tk.Label(self.root, text="Rezultate EXAM", bg="#111", fg="#00ffff", font=("Arial", 22, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Scor final: {correct_count}/{total} ({pct:.1f}%)", bg="#111", fg="white", font=("Arial", 13)).pack()
        tk.Label(self.root, text=f"Timp total: {duration:.1f}s", bg="#111", fg="white", font=("Arial", 12)).pack(pady=(0, 10))

        wrong = [r for r in results if not r["correct"]]
        if wrong:
            tk.Label(self.root, text="Întrebări greșite:", bg="#111", fg="red", font=("Arial", 14, "bold")).pack(pady=10)
            text_box = tk.Text(self.root, wrap="word", bg="#111", fg="white", font=("Arial", 11), width=95, height=15)
            text_box.pack(padx=10, pady=5)
            for r in wrong:
                text_box.insert("end", f"- {r['question']}\nRăspuns corect: {r['choices'][r['correct_index']]}\nExplicație: {r['explanation']}\n\n")
            text_box.config(state="disabled")

        tk.Button(self.root, text="⬅ Înapoi la meniu", command=self.show_main_menu,
                  bg="#00cccc", fg="black", font=("Arial", 12, "bold")).pack(pady=15)

    # ===================== CLEAR WINDOW =====================
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ===================== ÎNAPOI LA MENIU =====================
    def show_main_menu(self):
        self.stop_timer()
        self.create_main_menu()


# ===================== RUN APP =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
