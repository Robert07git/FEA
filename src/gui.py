import tkinter as tk
from tkinter import ttk
from data_loader import load_questions, get_domains
from quiz_logic import QuizSession
from progress_chart import show_progress_chart
from export_pdf import export_quiz_pdf
from stats import show_dashboard
import time


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FEA Quiz Trainer")
        self.root.geometry("1000x750")
        self.root.configure(bg="#111")
        self.root.resizable(False, False)

        self.domains = get_domains() or ["structural", "crash", "moldflow", "cfd", "nvh", "mix"]

        self.session = None
        self.time_left = 0
        self.timer_running = False

        self.create_main_menu()

    # ===================== PAGINA PRINCIPALĂ =====================
    def create_main_menu(self):
        self.frame_main = tk.Frame(self.root, bg="#111")
        self.frame_main.pack(fill="both", expand=True)

        tk.Label(
            self.frame_main, text="FEA QUIZ TRAINER",
            font=("Arial", 26, "bold"), fg="#00ffff", bg="#111"
        ).pack(pady=30)

        tk.Label(self.frame_main, text="Alege domeniul:", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.domain_var = tk.StringVar(value=self.domains[0])
        ttk.Combobox(
            self.frame_main, textvariable=self.domain_var, values=self.domains, state="readonly", width=20
        ).pack(pady=10)

        tk.Label(self.frame_main, text="Număr întrebări:", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.num_questions_var = tk.IntVar(value=5)
        tk.Spinbox(self.frame_main, from_=1, to=50, textvariable=self.num_questions_var, width=5).pack(pady=10)

        tk.Label(self.frame_main, text="Mod de testare:", bg="#111", fg="white", font=("Arial", 12)).pack(pady=5)
        self.mode_var = tk.StringVar(value="train")
        frame_modes = tk.Frame(self.frame_main, bg="#111")
        frame_modes.pack()

        tk.Radiobutton(frame_modes, text="TRAIN", variable=self.mode_var, value="train",
                       bg="#00aaaa", fg="white", indicatoron=0, width=10,
                       font=("Arial", 11, "bold"), selectcolor="#00cccc").pack(side="left", padx=5)
        tk.Radiobutton(frame_modes, text="EXAM", variable=self.mode_var, value="exam",
                       bg="#cc4444", fg="white", indicatoron=0, width=10,
                       font=("Arial", 11, "bold"), selectcolor="#ff5555").pack(side="left", padx=5)

        tk.Label(self.frame_main, text="Timp per întrebare (secunde):", bg="#111", fg="white", font=("Arial", 12)).pack(pady=5)
        self.time_var = tk.IntVar(value=15)
        tk.Spinbox(self.frame_main, from_=5, to=120, textvariable=self.time_var, width=5).pack(pady=10)

        tk.Button(self.frame_main, text="Start Quiz", command=self.start_quiz,
                  font=("Arial", 12, "bold"), bg="#00cccc", fg="#000", width=12).pack(pady=15)

        frame_tools = tk.Frame(self.frame_main, bg="#111")
        frame_tools.pack(pady=10)

        tk.Button(frame_tools, text="📊 Grafic progres", command=show_progress_chart,
                  font=("Arial", 10), bg="#333", fg="white", width=14).pack(side="left", padx=5)
        tk.Button(frame_tools, text="📝 Export PDF", command=export_quiz_pdf,
                  font=("Arial", 10), bg="#333", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(frame_tools, text="📈 Statistici", command=show_dashboard,
                  font=("Arial", 10), bg="#333", fg="white", width=12).pack(side="left", padx=5)

    # ===================== PORNIRE QUIZ =====================
    def start_quiz(self):
        domain = self.domain_var.get()
        num_q = self.num_questions_var.get()
        mode = self.mode_var.get()
        time_limit = self.time_var.get() if mode == "exam" else None

        questions = load_questions(domain)
        if not questions:
            return

        self.frame_main.pack_forget()
        self.session = QuizSession(self, questions[:num_q], mode, time_limit)
        self.create_quiz_frame()

    # ===================== FRAME QUIZ =====================
    def create_quiz_frame(self):
        self.frame_quiz = tk.Frame(self.root, bg="#111")
        self.frame_quiz.pack(fill="both", expand=True)

        # Scroll pentru întrebări lungi
        frame_scroll = tk.Frame(self.frame_quiz, bg="#111")
        frame_scroll.pack(pady=20)

        self.text_question = tk.Text(frame_scroll, height=5, width=95,
                                     wrap="word", font=("Arial", 14, "bold"),
                                     bg="#111", fg="white", relief="flat")
        scroll = tk.Scrollbar(frame_scroll, command=self.text_question.yview)
        self.text_question.configure(yscrollcommand=scroll.set)
        self.text_question.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Timer și progres
        self.progress_bar = ttk.Progressbar(self.frame_quiz, length=500, mode="determinate")
        self.timer_label = tk.Label(self.frame_quiz, text="", bg="#111", fg="#00ffff", font=("Arial", 11, "bold"))

        # Răspunsuri
        self.options_var = tk.IntVar(value=-1)
        self.option_buttons = []
        for i in range(4):
            btn = tk.Radiobutton(
                self.frame_quiz, variable=self.options_var, value=i, text="",
                font=("Arial", 12), bg="#111", fg="white",
                activebackground="#222", selectcolor="#111",
                wraplength=850, justify="left", indicatoron=1, anchor="w"
            )
            btn.pack(fill="x", padx=100, pady=3)
            self.option_buttons.append(btn)

        self.lbl_feedback = tk.Label(self.frame_quiz, text="", font=("Arial", 12),
                                     bg="#111", fg="white", wraplength=850, justify="center")
        self.lbl_feedback.pack(pady=15)

        self.btn_next = tk.Button(self.frame_quiz, text="Următoarea ➜", command=self.submit_answer,
                                  font=("Arial", 12, "bold"), bg="#00cccc", fg="#000")
        self.btn_next.pack(pady=10)

        self.btn_back = tk.Button(self.frame_quiz, text="⟵ Înapoi la meniu", command=self.show_main_menu,
                                  font=("Arial", 10), bg="#333", fg="white")
        self.btn_back.pack(side="bottom", pady=10)

        self.show_question()

    def show_question(self):
        question = self.session.current_question()
        if not question:
            return

        self.lbl_feedback.config(text="")
        self.options_var.set(-1)
        for btn in self.option_buttons:
            btn.deselect()

        self.text_question.config(state="normal")
        self.text_question.delete("1.0", "end")
        self.text_question.insert("end", f"Întrebarea {self.session.index + 1}/{len(self.session.questions)}:\n\n{question['question']}")
        self.text_question.config(state="disabled")

        for i, choice in enumerate(question["choices"]):
            self.option_buttons[i].config(text=choice)

        self.btn_next.config(text="Următoarea ➜", command=self.submit_answer)

        if self.session.mode == "exam" and self.session.time_limit:
            self.progress_bar.pack(pady=5)
            self.timer_label.pack()
            self.start_timer(self.session.time_limit)
        else:
            self.progress_bar.pack_forget()
            self.timer_label.pack_forget()

    # ===================== TIMER =====================
    def start_timer(self, seconds):
        self.time_left = seconds
        self.progress_bar["maximum"] = seconds
        self.progress_bar["value"] = seconds
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        if self.time_left <= 0:
            self.timer_running = False
            self.session.next_question()
            return
        self.timer_label.config(text=f"Timp rămas: {self.time_left}s")
        self.progress_bar["value"] = self.time_left
        self.time_left -= 1
        self.root.after(1000, self.update_timer)

    # ===================== TRAIN FEEDBACK =====================
    def submit_answer(self):
        selected = self.options_var.get()
        if selected == -1:
            return
        self.session.answer(selected)

    def show_train_feedback(self, correct, correct_answer, explanation):
        if correct:
            text = f"✅ Corect!\n{explanation}"
            color = "#00ff88"
        else:
            text = f"❌ Greșit!\nRăspuns corect: {correct_answer}\n{explanation}"
            color = "#ff4444"

        self.lbl_feedback.config(text=text, fg=color)
        self.btn_next.config(text="Continuă ➜", command=self.session.next_question)

    # ===================== FINAL EXAM =====================
    def show_exam_summary(self, results, score, total, pct, duration):
        self.frame_quiz.pack_forget()
        frame_summary = tk.Frame(self.root, bg="#111")
        frame_summary.pack(fill="both", expand=True)

        tk.Label(frame_summary, text="Rezultate EXAM", font=("Arial", 20, "bold"),
                 fg="#00ffff", bg="#111").pack(pady=20)

        tk.Label(frame_summary, text=f"Scor final: {score}/{total} ({pct:.1f}%)\nTimp total: {duration:.1f}s",
                 font=("Arial", 13), fg="white", bg="#111").pack(pady=10)

        wrong = [r for r in results if not r["correct"]]
        if not wrong:
            tk.Label(frame_summary, text="Ai răspuns corect la toate întrebările! 🎉",
                     font=("Arial", 12), fg="#00ff88", bg="#111").pack(pady=10)
        else:
            tk.Label(frame_summary, text="Întrebări greșite:", font=("Arial", 14, "bold"),
                     fg="#ff6666", bg="#111").pack(pady=5)
            text_box = tk.Text(frame_summary, height=15, width=100, bg="#222", fg="white", wrap="word")
            text_box.pack(pady=10)
            for r in wrong:
                text_box.insert("end", f"- {r['question']}\nRăspuns corect: {r['choices'][r['correct_index']]}\nExplicație: {r['explanation']}\n\n")
            text_box.config(state="disabled")

        tk.Button(frame_summary, text="⟵ Înapoi la meniu", command=self.show_main_menu,
                  font=("Arial", 12), bg="#00cccc", fg="black").pack(pady=20)

    # ===================== MENIU =====================
    def show_main_menu(self):
        self.timer_running = False
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_menu()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
