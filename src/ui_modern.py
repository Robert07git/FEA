# ui_modern.py
import customtkinter as ctk
import json
import os
from quiz_engine_modern import QuizManagerModern
from stats_manager import add_session, load_stats, get_summary, get_leaderboard
from pdf_exporter_modern import export_pdf_modern


class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 3.9 — PDF, Feedback & Unicode Fix")
        self.geometry("900x600")
        self.configure(fg_color="#202020")

        self.quiz_manager = None
        self.mode = None
        self.time_left = 0
        self.total_time = 0
        self.time_used = 0
        self.timer_running = False
        self.last_result = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.left_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#252525")
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.right_frame = ctk.CTkFrame(self, fg_color="#202020")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.create_main_menu()

    # === Meniu principal ===
    def create_main_menu(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.left_frame, text="FEA QUIZ TRAINER",
                             font=("Segoe UI", 22, "bold"), text_color="#00ffff")
        title.pack(pady=(30, 20))

        buttons = [
            ("🧠 TRAIN MODE", lambda: self.show_quiz_setup("train")),
            ("🧾 EXAM MODE", lambda: self.show_quiz_setup("exam")),
            ("📊 STATISTICI", self.show_stats),
            ("🏆 LEADERBOARD", self.show_leaderboard),
            ("📄 EXPORTĂ PDF DIN NOU", self.manual_export_pdf),
        ]

        for text, cmd in buttons:
            ctk.CTkButton(self.left_frame, text=text, command=cmd,
                          font=("Segoe UI", 14, "bold"), height=40, width=180,
                          fg_color="#1E5BA6", hover_color="#297BE6").pack(pady=8)

        ctk.CTkButton(self.left_frame, text="⬅ Ieșire", command=self.quit,
                      font=("Segoe UI", 14, "bold"), height=40, width=180,
                      fg_color="#A60000", hover_color="#C30000").pack(side="bottom", pady=20)

    # === Setup Quiz ===
    def show_quiz_setup(self, mode):
        setup = ctk.CTkToplevel(self)
        setup.title("Configurare Quiz")
        setup.geometry("400x350")
        setup.grab_set()

        ctk.CTkLabel(setup, text="Domeniu:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        domain_var = ctk.StringVar(value="mix")
        ctk.CTkComboBox(setup, variable=domain_var,
                        values=["mix", "structural", "crash", "cfd", "nvh"],
                        width=200).pack(pady=5)

        ctk.CTkLabel(setup, text="Număr întrebări:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        num_var = ctk.StringVar(value="10")
        ctk.CTkEntry(setup, textvariable=num_var, width=100, justify="center").pack(pady=5)

        ctk.CTkLabel(setup, text="Timp (minute):", font=("Segoe UI", 14, "bold")).pack(pady=10)
        time_var = ctk.StringVar(value="2")
        ctk.CTkEntry(setup, textvariable=time_var, width=100, justify="center").pack(pady=5)

        def confirm():
            domain = domain_var.get()
            num = int(num_var.get()) if num_var.get().isdigit() else 10
            time_min = int(time_var.get()) if time_var.get().isdigit() else 2
            setup.destroy()
            self.start_quiz(mode, domain, num, time_min)

        ctk.CTkButton(setup, text="Start Quiz", command=confirm,
                      fg_color="#1E5BA6").pack(pady=20)

    # === Start Quiz ===
    def start_quiz(self, mode, domain, num_questions, time_min):
        with open(os.path.join("data", "fea_questions.json"), "r", encoding="utf-8") as f:
            questions = json.load(f)
        self.quiz_manager = QuizManagerModern(questions, domain, num_questions)
        self.mode = mode
        self.time_left = time_min * 60
        self.total_time = self.time_left
        self.time_used = 0
        self.timer_running = True
        self.load_quiz()
        self.update_timer()

    def load_quiz(self):
        self.clear_right_frame()
        self.create_timer()
        self.create_progress_bar()
        self.show_question()

    # === Timer ===
    def create_timer(self):
        self.timer_label = ctk.CTkLabel(self.right_frame, text="", font=("Segoe UI", 16, "bold"), text_color="#00ffff")
        self.timer_label.pack(pady=(10, 0))
        self.timer_bar = ctk.CTkProgressBar(self.right_frame, width=400)
        self.timer_bar.pack(pady=5)
        self.timer_bar.set(1)

    def update_timer(self):
        if not self.timer_running:
            return
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.configure(text=f"Timp rămas: {mins:02}:{secs:02}")
        self.timer_bar.set(self.time_left / self.total_time)
        if self.time_left <= 0:
            self.show_results()
            return
        self.time_left -= 1
        self.time_used += 1
        self.after(1000, self.update_timer)

    # === Progress Bar ===
    def create_progress_bar(self):
        self.progress_label = ctk.CTkLabel(self.right_frame, text="", font=("Segoe UI", 14))
        self.progress_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self.right_frame, width=400)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

    def update_progress(self):
        current = self.quiz_manager.current_index + 1
        total = self.quiz_manager.total_questions()
        self.progress_bar.set(current / total)
        self.progress_label.configure(text=f"Întrebarea {current}/{total}")

    # === Afișare întrebare ===
    def show_question(self):
        q = self.quiz_manager.get_current_question()
        if not q:
            self.show_results()
            return
        self.clear_right_frame(keep_progress=True, keep_timer=True)
        self.update_progress()

        ctk.CTkLabel(self.right_frame, text=q["question"], wraplength=700,
                     font=("Segoe UI", 18, "bold"), text_color="white").pack(pady=20)
        for i, opt in enumerate(q["choices"]):
            ctk.CTkButton(self.right_frame, text=opt, font=("Segoe UI", 14),
                          fg_color="#1E5BA6", hover_color="#297BE6",
                          width=600, command=lambda idx=i: self.handle_answer(idx)).pack(pady=6)

    def handle_answer(self, idx):
        correct, correct_text, explanation = self.quiz_manager.check_answer(idx)
        if self.mode == "exam":
            self.next_question()
            return
        self.clear_right_frame(keep_progress=True, keep_timer=True)
        result = "✅ Corect!" if correct else "❌ Greșit!"
        color = "#00ff99" if correct else "#ff4444"
        ctk.CTkLabel(self.right_frame, text=result, text_color=color, font=("Segoe UI", 22, "bold")).pack(pady=15)
        ctk.CTkLabel(self.right_frame, text=f"Răspuns corect: {correct_text}", text_color="white").pack(pady=5)
        ctk.CTkLabel(self.right_frame, text=f"Explicație: {explanation}", text_color="#cccccc", wraplength=700).pack(pady=10)

        if self.quiz_manager.current_index + 1 < self.quiz_manager.total_questions():
            ctk.CTkButton(self.right_frame, text="Continuă ➜", command=self.next_question, fg_color="#1E5BA6").pack(pady=15)
        else:
            self.show_train_finish(None)

    def next_question(self):
        if self.quiz_manager.advance():
            self.show_question()
        else:
            self.show_results()

    # === Rezultate ===
    def show_results(self):
        self.timer_running = False
        self.clear_right_frame()
        result = self.quiz_manager.get_result_data(self.mode, self.time_used)
        self.last_result = result
        add_session(result)
        export_pdf_modern(result, self.quiz_manager.user_answers if self.mode == "train" else None)

        ctk.CTkLabel(self.right_frame, text=f"Rezultat final: {result['percent']}%",
                     font=("Segoe UI", 24, "bold"), text_color="#00ffff").pack(pady=20)
        if self.mode == "train":
            self.show_train_finish(result)
        else:
            self.show_exam_summary(result)

    def show_train_finish(self, _):
        ctk.CTkLabel(self.right_frame, text="🏁 Antrenamentul s-a încheiat!",
                     text_color="#00ff99", font=("Segoe UI", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(self.right_frame, text="Toate întrebările au fost parcurse.\nPoți reveni la meniu pentru o nouă sesiune.",
                     text_color="white", font=("Segoe UI", 14)).pack(pady=10)
        ctk.CTkButton(self.right_frame, text="⬅ Înapoi la meniu principal",
                      fg_color="#1E5BA6", command=self.create_main_menu).pack(pady=20)

    def show_exam_summary(self, result):
        ctk.CTkLabel(self.right_frame, text="Rezumat sesiune exam:",
                     font=("Segoe UI", 18, "bold"), text_color="#ffffff").pack(pady=10)
        details = (
            f"Întrebări totale: {result['total']}\n"
            f"Răspunsuri corecte: {result['correct']}\n"
            f"Răspunsuri greșite: {result['incorrect']}\n"
            f"Scor final: {result['percent']}%\n"
            f"Timp total: {result['time_used']} secunde"
        )
        ctk.CTkLabel(self.right_frame, text=details, justify="left",
                     font=("Segoe UI", 14), text_color="#cccccc").pack(pady=10)
        ctk.CTkLabel(self.right_frame, text="Raport PDF generat automat ✅",
                     text_color="#00ff99", font=("Segoe UI", 14)).pack(pady=10)
        ctk.CTkButton(self.right_frame, text="📄 Deschide raportul PDF",
                      command=lambda: os.startfile("data/last_session_report.pdf"),
                      fg_color="#1E5BA6").pack(pady=10)
        ctk.CTkButton(self.right_frame, text="⬅ Înapoi la meniu principal",
                      fg_color="#1E5BA6", command=self.create_main_menu).pack(pady=20)

    # === Export PDF manual ===
    def manual_export_pdf(self):
        if not self.last_result:
            self.clear_right_frame()
            ctk.CTkLabel(self.right_frame, text="⚠️ Nu există o sesiune finalizată recent!",
                         text_color="#ff6666", font=("Segoe UI", 18, "bold")).pack(pady=20)
            return
        export_pdf_modern(self.last_result)
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="📄 Raport PDF reexportat cu succes!",
                     text_color="#00ff99", font=("Segoe UI", 18, "bold")).pack(pady=30)

    # === Statistici ===
    def show_stats(self):
        stats = load_stats()
        summary = get_summary(stats)
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="📊 STATISTICI GENERALE",
                     font=("Segoe UI", 22, "bold"), text_color="#00ffff").pack(pady=20)
        if not stats:
            ctk.CTkLabel(self.right_frame, text="Nu există date încă.", font=("Segoe UI", 16),
                         text_color="#ffffff").pack(pady=10)
            return
        text = (
            f"Total sesiuni: {summary['total_sessions']}\n"
            f"Media scorurilor: {summary['avg_score']}%\n"
            f"Cel mai bun scor: {summary['best_score']}%\n"
        )
        ctk.CTkLabel(self.right_frame, text=text, justify="left", font=("Segoe UI", 18, "bold"),
                     text_color="#ffffff").pack(pady=20)

    # === Leaderboard ===
    def show_leaderboard(self):
        stats = load_stats()
        leaders = get_leaderboard(stats)
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="🏆 LEADERBOARD LOCAL", font=("Segoe UI", 22, "bold"),
                     text_color="#00ffff").pack(pady=20)
        if not leaders:
            ctk.CTkLabel(self.right_frame, text="Nicio sesiune înregistrată încă.", font=("Segoe UI", 16),
                         text_color="#ffffff").pack(pady=10)
            return
        for i, s in enumerate(leaders, 1):
            color = "#FFD700" if i == 1 else "#00ffff" if i == 2 else "#ff9933"
            ctk.CTkLabel(self.right_frame,
                         text=f"{i}. {s['domain'].capitalize()} - {s['percent']}% ({s['mode']}, {s['date']})",
                         text_color=color, font=("Segoe UI", 16, "bold")).pack(pady=5)

    # === Utilitare ===
    def clear_right_frame(self, keep_progress=False, keep_timer=False):
        for widget in self.right_frame.winfo_children():
            if keep_progress and widget in [getattr(self, "progress_bar", None),
                                            getattr(self, "progress_label", None)]:
                continue
            if keep_timer and widget in [getattr(self, "timer_bar", None),
                                         getattr(self, "timer_label", None)]:
                continue
            widget.destroy()


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
