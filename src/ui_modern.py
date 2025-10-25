import customtkinter as ctk
import json
import os
from quiz_engine_modern import QuizManagerModern


class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FEA Quiz Trainer 2.5")
        self.geometry("900x600")
        self.configure(fg_color="#202020")

        self.quiz_manager = None
        self.mode = None
        self.progress_bar = None
        self.progress_label = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#252525")
        self.left_frame.grid(row=0, column=0, sticky="nswe")

        self.right_frame = ctk.CTkFrame(self, fg_color="#202020")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.create_main_menu()

    # ------------------------------------------------------------
    #                     Meniu principal
    # ------------------------------------------------------------
    def create_main_menu(self):
        title = ctk.CTkLabel(
            self.left_frame,
            text="FEA QUIZ TRAINER",
            font=("Segoe UI", 22, "bold"),
            text_color="#00ffff"
        )
        title.pack(pady=(30, 20))

        buttons = [
            ("🧠 TRAIN MODE", lambda: self.show_quiz_setup("train")),
            ("🧾 EXAM MODE", lambda: self.show_quiz_setup("exam")),
            ("📊 STATISTICI", self.show_stats),
            ("📈 GRAFIC PROGRES", self.show_progress),
            ("📚 LEARN MODE", self.show_learn_mode),
            ("🏆 LEADERBOARD", self.show_leaderboard),
            ("⚙️ SETĂRI", self.show_settings)
        ]

        for text, cmd in buttons:
            btn = ctk.CTkButton(
                self.left_frame,
                text=text,
                command=cmd,
                font=("Segoe UI", 14, "bold"),
                height=40,
                width=180,
                fg_color="#1E5BA6",
                hover_color="#297BE6"
            )
            btn.pack(pady=8)

        exit_btn = ctk.CTkButton(
            self.left_frame,
            text="⬅ Ieșire",
            command=self.quit,
            font=("Segoe UI", 14, "bold"),
            height=40,
            width=180,
            fg_color="#A60000",
            hover_color="#C30000"
        )
        exit_btn.pack(side="bottom", pady=20)

    # ------------------------------------------------------------
    #          Popup: selectare domeniu și număr întrebări
    # ------------------------------------------------------------
    def show_quiz_setup(self, mode):
        setup_win = ctk.CTkToplevel(self)
        setup_win.title("Configurare Quiz")
        setup_win.geometry("400x300")
        setup_win.grab_set()

        ctk.CTkLabel(setup_win, text="Alege domeniul:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        domain_var = ctk.StringVar(value="mix")
        domain_box = ctk.CTkComboBox(setup_win, variable=domain_var,
                                     values=["mix", "structural", "crash", "cfd", "nvh"],
                                     width=200)
        domain_box.pack(pady=5)

        ctk.CTkLabel(setup_win, text="Număr întrebări:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        num_var = ctk.StringVar(value="10")
        num_entry = ctk.CTkEntry(setup_win, textvariable=num_var, width=100, justify="center")
        num_entry.pack(pady=5)

        def confirm():
            domain = domain_var.get()
            try:
                num = int(num_var.get())
            except ValueError:
                num = None
            setup_win.destroy()
            self.start_quiz(mode, domain, num)

        start_btn = ctk.CTkButton(setup_win, text="Start Quiz", command=confirm, fg_color="#1E5BA6")
        start_btn.pack(pady=20)

    # ------------------------------------------------------------
    #                     Începerea quizului
    # ------------------------------------------------------------
    def start_quiz(self, mode, domain, num_questions):
        self.clear_right_frame()

        data_path = os.path.join("data", "fea_questions.json")
        with open(data_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        self.quiz_manager = QuizManagerModern(questions, domain=domain, num_questions=num_questions)
        self.mode = mode
        self.load_quiz()

    def load_quiz(self):
        self.clear_right_frame()
        self.create_progress_bar()
        self.show_question()

    # ------------------------------------------------------------
    #              Bară de progres + afișare întrebare
    # ------------------------------------------------------------
    def create_progress_bar(self):
        self.progress_label = ctk.CTkLabel(self.right_frame, text="", font=("Segoe UI", 14))
        self.progress_label.pack(pady=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(self.right_frame, width=400)
        self.progress_bar.pack(pady=(5, 20))
        self.progress_bar.set(0)

    def update_progress(self):
        total = self.quiz_manager.total_questions()
        current = self.quiz_manager.current_index + 1
        progress = current / total
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"Întrebarea {current}/{total}")

    def show_question(self):
        q = self.quiz_manager.get_current_question()
        if not q:
            self.show_results()
            return

        self.clear_right_frame(keep_progress=True)
        self.update_progress()

        question_label = ctk.CTkLabel(
            self.right_frame,
            text=q["question"],
            font=("Segoe UI", 18, "bold"),
            wraplength=700,
            justify="left",
            text_color="white"
        )
        question_label.pack(pady=(10, 20))

        options = q.get("choices", [])
        for i, opt in enumerate(options):
            btn = ctk.CTkButton(
                self.right_frame,
                text=opt,
                command=lambda idx=i: self.handle_answer(idx),
                width=600,
                height=35,
                fg_color="#1E5BA6",
                hover_color="#297BE6",
                font=("Segoe UI", 14)
            )
            btn.pack(pady=8)

    # ------------------------------------------------------------
    #                     Răspunsuri și rezultate
    # ------------------------------------------------------------
    def handle_answer(self, idx):
        correct, correct_text, explanation = self.quiz_manager.check_answer(idx)
        if self.mode == "exam":
            # fără feedback imediat
            self.next_question()
            return

        # feedback instant (train mode)
        self.clear_right_frame(keep_progress=True)
        self.update_progress()

        result_text = "✅ Corect!" if correct else "❌ Greșit!"
        color = "#00ff99" if correct else "#ff4444"

        ctk.CTkLabel(self.right_frame, text=result_text, text_color=color, font=("Segoe UI", 22, "bold")).pack(pady=20)
        ctk.CTkLabel(self.right_frame, text=f"Răspuns corect: {correct_text}", text_color="white").pack(pady=5)
        ctk.CTkLabel(self.right_frame, text=f"Explicație: {explanation}", text_color="#cccccc", wraplength=700).pack(pady=10)

        ctk.CTkButton(self.right_frame, text="Continuă ➜", command=self.next_question,
                      font=("Segoe UI", 14, "bold"), fg_color="#1E5BA6").pack(pady=20)

    def next_question(self):
        if self.quiz_manager.advance():
            self.show_question()
        else:
            self.show_results()

    def show_results(self):
        self.clear_right_frame()
        total = self.quiz_manager.total_questions()
        score = self.quiz_manager.score
        percent = round(score / total * 100, 1)

        ctk.CTkLabel(self.right_frame,
                     text=f"Rezultat final: {score}/{total}  ({percent}%)",
                     font=("Segoe UI", 22, "bold"), text_color="#00ffff").pack(pady=(40, 20))

        if self.mode == "exam":
            for ans in self.quiz_manager.user_answers:
                color = "#00ff99" if ans["is_correct"] else "#ff4444"
                ctk.CTkLabel(self.right_frame,
                             text=ans["question"], font=("Segoe UI", 14, "bold"),
                             wraplength=700, justify="left", text_color=color).pack(pady=(5, 0))
                ctk.CTkLabel(self.right_frame,
                             text=f"Corect: {ans['correct_answer']}\nExplicație: {ans['explanation']}",
                             font=("Segoe UI", 13), wraplength=700, text_color="#cccccc").pack(pady=(0, 10))

        ctk.CTkButton(self.right_frame, text="⬅ Înapoi la meniu", command=self.clear_right_frame,
                      font=("Segoe UI", 14), fg_color="#1E5BA6").pack(pady=20)

    # ------------------------------------------------------------
    #                   Utility
    # ------------------------------------------------------------
    def clear_right_frame(self, keep_progress=False):
        if keep_progress:
            for widget in self.right_frame.winfo_children():
                if widget not in [self.progress_bar, self.progress_label]:
                    widget.destroy()
        else:
            for widget in self.right_frame.winfo_children():
                widget.destroy()

    # ------------------------------------------------------------
    #                 Placeholder pentru alte secțiuni
    # ------------------------------------------------------------
    def show_stats(self): self.simple_placeholder("📊 Statistici — în dezvoltare")
    def show_progress(self): self.simple_placeholder("📈 Grafic progres — în dezvoltare")
    def show_learn_mode(self): self.simple_placeholder("📚 Learn Mode — în dezvoltare")
    def show_leaderboard(self): self.simple_placeholder("🏆 Leaderboard — în dezvoltare")
    def show_settings(self): self.simple_placeholder("⚙️ Setări — în dezvoltare")

    def simple_placeholder(self, text):
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text=text, font=("Segoe UI", 20, "bold")).pack(pady=40)


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
