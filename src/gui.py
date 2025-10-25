import tkinter as tk
from tkinter import ttk, messagebox
from quiz_logic import QuizSession
from data_loader import load_questions
from datetime import datetime
import time


class FEAGui:
    def __init__(self, root):
        self.root = root
        self.root.title("FEA QUIZ App")
        self.root.geometry("750x520")
        self.root.configure(bg="#1e1e1e")

        self.session = None
        self.selected_answer = tk.IntVar(value=-1)

        self.loading_screen()

    # ================================
    #          INTRO SCREEN
    # ================================
    def loading_screen(self):
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(expand=True, fill="both")

        title = tk.Label(
            frame,
            text="FEA QUIZ",
            font=("Segoe UI", 32, "bold"),
            fg="#00FFAA",
            bg="#1e1e1e"
        )
        title.pack(pady=60)

        sub = tk.Label(
            frame,
            text="Simulare · Analiză · Cunoaștere",
            font=("Segoe UI", 14),
            fg="white",
            bg="#1e1e1e"
        )
        sub.pack(pady=10)

        progress = ttk.Progressbar(frame, mode="determinate", length=300)
        progress.pack(pady=40)

        def load_app():
            for i in range(0, 101, 5):
                progress["value"] = i
                frame.update_idletasks()
                time.sleep(0.05)
            frame.destroy()
            self.setup_menu()

        self.root.after(300, load_app)

    # ================================
    #          MENU SCREEN
    # ================================
    def setup_menu(self):
        self.menu_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.menu_frame.pack(expand=True, fill="both")

        tk.Label(
            self.menu_frame,
            text="Selectează domeniul",
            font=("Segoe UI", 16, "bold"),
            fg="#00FFAA",
            bg="#1e1e1e"
        ).pack(pady=10)

        self.domain_var = tk.StringVar(value="structural")
        domains = ["structural", "crash", "moldflow", "cfd", "nvh"]
        for d in domains:
            ttk.Radiobutton(
                self.menu_frame, text=d.capitalize(),
                variable=self.domain_var, value=d
            ).pack(anchor="w", padx=260)

        ttk.Separator(self.menu_frame, orient="horizontal").pack(fill="x", pady=10)

        tk.Label(
            self.menu_frame,
            text="Mod de testare",
            font=("Segoe UI", 16, "bold"),
            fg="#00FFAA",
            bg="#1e1e1e"
        ).pack(pady=10)

        self.mode_var = tk.StringVar(value="train")
        ttk.Radiobutton(
            self.menu_frame, text="Train (explicații după fiecare întrebare)",
            variable=self.mode_var, value="train"
        ).pack(anchor="w", padx=260)
        ttk.Radiobutton(
            self.menu_frame, text="Exam (timp limitat / feedback la final)",
            variable=self.mode_var, value="exam"
        ).pack(anchor="w", padx=260)

        ttk.Button(
            self.menu_frame, text="Start Quiz", command=self.start_quiz
        ).pack(pady=25)

    # ================================
    #          START QUIZ
    # ================================
    def start_quiz(self):
        domeniu = self.domain_var.get()
        mode = self.mode_var.get()
        questions = load_questions(domeniu)
        if not questions:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul {domeniu}.")
            return

        time_limit = 15 if mode == "exam" else None
        self.session = QuizSession(
            questions,
            num_questions=10,
            mode=mode,
            time_limit_sec=time_limit,
            update_ui_callback=self.update_timer
        )

        self.menu_frame.destroy()
        self.setup_quiz_frame()
        self.display_question()
        if mode == "exam":
            self.session.start_timer()

    # ================================
    #          QUIZ FRAME
    # ================================
    def setup_quiz_frame(self):
        self.quiz_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.quiz_frame.pack(expand=True, fill="both", padx=25, pady=25)

        self.question_label = tk.Label(
            self.quiz_frame, text="", wraplength=650,
            font=("Segoe UI", 14, "bold"),
            fg="white", bg="#1e1e1e", justify="left"
        )
        self.question_label.pack(pady=10, anchor="w")

        self.choice_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(
                self.quiz_frame, text="", variable=self.selected_answer, value=i
            )
            rb.pack(anchor="w", padx=30, pady=4)
            self.choice_buttons.append(rb)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.quiz_frame, variable=self.progress_var, length=400, mode="determinate"
        )
        self.progress_bar.pack(pady=15)

        self.timer_label = tk.Label(
            self.quiz_frame, text="", font=("Segoe UI", 12),
            fg="#00FFAA", bg="#1e1e1e"
        )
        self.timer_label.pack()

        self.feedback_label = tk.Label(
            self.quiz_frame, text="", wraplength=650, justify="left",
            font=("Segoe UI", 12), fg="#FFD700", bg="#1e1e1e"
        )
        self.feedback_label.pack(pady=10)

        ttk.Button(
            self.quiz_frame, text="Confirmă", command=self.submit_answer
        ).pack(pady=10)

    # ================================
    #          AFIȘARE ÎNTREBARE
    # ================================
    def display_question(self):
        q = self.session.get_current_question()
        if not q:
            self.finish_quiz()
            return

        self.selected_answer.set(-1)
        self.feedback_label.config(text="")

        self.question_label.config(text=f"Q{self.session.current_index + 1}. {q['question']}")
        for i, c in enumerate(q["choices"]):
            self.choice_buttons[i].config(text=c)

        pct = (self.session.current_index / len(self.session.questions)) * 100
        self.progress_var.set(pct)
        self.update_timer()

    # ================================
    #          TIMER UPDATE
    # ================================
    def update_timer(self, timeout=False):
        if not self.session or self.session.mode != "exam":
            return

        if timeout:
            self.feedback_label.config(text="⏰ Timp expirat! Trecem la următoarea întrebare.")
            self.root.after(1000, self.next_question)
            return

        self.timer_label.config(text=f"Timp rămas: {self.session.time_left}s")

    # ================================
    #          CONFIRMĂ RĂSPUNS
    # ================================
    def submit_answer(self):
        sel = self.selected_answer.get()
        if sel == -1:
            messagebox.showwarning("Atenție", "Selectează un răspuns.")
            return

        self.session.stop_timer()
        is_correct, feedback = self.session.answer_question(sel)
        if self.session.mode == "train":
            self.feedback_label.config(text=feedback)
            self.root.after(2500, self.next_question)
        else:
            self.next_question()

    # ================================
    #          URMĂTOAREA ÎNTREBARE
    # ================================
    def next_question(self):
        if self.session.has_next():
            self.display_question()
            if self.session.mode == "exam":
                self.session.start_timer()
        else:
            self.finish_quiz()

    # ================================
    #          FINAL QUIZ
    # ================================
    def finish_quiz(self):
        score, total, pct = self.session.get_score_summary()
        self.quiz_frame.destroy()

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame,
            text=f"Scor final: {score}/{total} ({pct:.1f}%)",
            font=("Segoe UI", 20, "bold"),
            fg="#00FFAA", bg="#1e1e1e"
        ).pack(pady=40)

        ttk.Button(frame, text="Înapoi la meniu", command=lambda: [frame.destroy(), self.setup_menu()]).pack(pady=20)
        ttk.Button(frame, text="Ieșire", command=self.root.quit).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = FEAGui(root)
    root.mainloop()
