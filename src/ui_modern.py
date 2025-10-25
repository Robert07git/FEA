# ui_modern.py
import customtkinter as ctk
import json
import os
from fpdf import FPDF
from quiz_engine_modern import QuizManagerModern
from stats_manager import add_session, load_stats, get_summary, get_leaderboard


class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 3.6 — Stats & Leaderboard")
        self.geometry("900x600")
        self.configure(fg_color="#202020")

        self.quiz_manager = None
        self.mode = None
        self.time_left = 0
        self.total_time = 0
        self.time_used = 0
        self.timer_running = False

        # Frames principale
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.left_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#252525")
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.right_frame = ctk.CTkFrame(self, fg_color="#202020")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.create_main_menu()

    # ========== MENIU PRINCIPAL ==========
    def create_main_menu(self):
        title = ctk.CTkLabel(self.left_frame, text="FEA QUIZ TRAINER", font=("Segoe UI", 22, "bold"), text_color="#00ffff")
        title.pack(pady=(30, 20))
        buttons = [
            ("🧠 TRAIN MODE", lambda: self.show_quiz_setup("train")),
            ("🧾 EXAM MODE", lambda: self.show_quiz_setup("exam")),
            ("📊 STATISTICI", self.show_stats),
            ("🏆 LEADERBOARD", self.show_leaderboard),
        ]
        for text, cmd in buttons:
            ctk.CTkButton(self.left_frame, text=text, command=cmd, font=("Segoe UI", 14, "bold"),
                          height=40, width=180, fg_color="#1E5BA6", hover_color="#297BE6").pack(pady=8)
        ctk.CTkButton(self.left_frame, text="⬅ Ieșire", command=self.quit, font=("Segoe UI", 14, "bold"),
                      height=40, width=180, fg_color="#A60000", hover_color="#C30000").pack(side="bottom", pady=20)

    # ========== CONFIGURARE QUIZ ==========
    def show_quiz_setup(self, mode):
        setup = ctk.CTkToplevel(self)
        setup.title("Configurare Quiz")
        setup.geometry("400x350")
        setup.grab_set()

        ctk.CTkLabel(setup, text="Alege domeniul:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        domain_var = ctk.StringVar(value="mix")
        ctk.CTkComboBox(setup, variable=domain_var, values=["mix", "structural", "crash", "cfd", "nvh"], width=200).pack(pady=5)
        ctk.CTkLabel(setup, text="Număr întrebări:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        num_var = ctk.StringVar(value="10")
        ctk.CTkEntry(setup, textvariable=num_var, width=100, justify="center").pack(pady=5)
        ctk.CTkLabel(setup, text="Timp total (minute):", font=("Segoe UI", 14, "bold")).pack(pady=10)
        time_var = ctk.StringVar(value="2")
        ctk.CTkEntry(setup, textvariable=time_var, width=100, justify="center").pack(pady=5)

        def confirm():
            domain = domain_var.get()
            num = int(num_var.get()) if num_var.get().isdigit() else None
            time_min = int(time_var.get()) if time_var.get().isdigit() else 1
            setup.destroy()
            self.start_quiz(mode, domain, num, time_min)

        ctk.CTkButton(setup, text="Start Quiz", command=confirm, fg_color="#1E5BA6").pack(pady=20)

    # ========== FLUX QUIZ ==========
    def start_quiz(self, mode, domain, num_questions, time_min):
        with open(os.path.join("data", "fea_questions.json"), "r", encoding="utf-8") as f:
            questions = json.load(f)
        self.quiz_manager = QuizManagerModern(questions, domain=domain, num_questions=num_questions)
        self.mode = mode
        self.time_left = time_min * 60
        self.total_time = self.time_left
        self.time_used = 0
        self.timer_running = True
        self.load_quiz()
        self.update_timer()

    def load_quiz(self):
        self.clear_right_frame()
        self.create_timer_section()
        self.create_progress_bar()
        self.show_question()

    # ========== TIMER ==========
    def create_timer_section(self):
        self.timer_label = ctk.CTkLabel(self.right_frame, text="", font=("Segoe UI", 16, "bold"), text_color="#00ffff")
        self.timer_label.pack(pady=(10, 0))
        self.timer_bar = ctk.CTkProgressBar(self.right_frame, width=400, height=10)
        self.timer_bar.pack(pady=(5, 10))
        self.timer_bar.set(1.0)

    def update_timer(self):
        if not self.timer_running:
            return
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.configure(text=f"Timp rămas: {mins:02d}:{secs:02d}")
        progress = self.time_left / self.total_time if self.total_time else 0
        self.timer_bar.set(progress)
        if self.time_left <= 0:
            self.timer_running = False
            self.show_results()
            return
        self.time_left -= 1
        self.time_used += 1
        self.after(1000, self.update_timer)

    # ========== PROGRES ==========
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

    # ========== ÎNTREBĂRI ==========
    def show_question(self):
        q = self.quiz_manager.get_current_question()
        if not q:
            self.show_results()
            return
        self.clear_right_frame(keep_progress=True, keep_timer=True)
        self.update_progress()
        ctk.CTkLabel(self.right_frame, text=q["question"], font=("Segoe UI", 18, "bold"),
                     wraplength=700, justify="left", text_color="white").pack(pady=(10, 20))
        for i, opt in enumerate(q.get("choices", [])):
            ctk.CTkButton(self.right_frame, text=opt, command=lambda idx=i: self.handle_answer(idx),
                          width=600, height=35, fg_color="#1E5BA6", hover_color="#297BE6",
                          font=("Segoe UI", 14)).pack(pady=8)

    def handle_answer(self, idx):
        correct, correct_text, explanation = self.quiz_manager.check_answer(idx)
        if self.mode == "exam":
            self.next_question()
            return
        self.clear_right_frame(keep_progress=True, keep_timer=True)
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

    # ========== REZULTATE ==========
    def show_results(self):
        self.timer_running = False
        self.clear_right_frame()
        result = self.quiz_manager.get_result_data(self.mode, self.time_used)
        add_session(result)
        self.export_pdf_report(result)
        total = result["total"]
        score = result["score"]
        percent = result["percent"]
        ctk.CTkLabel(self.right_frame, text=f"Rezultat final: {score}/{total} ({percent}%)",
                     font=("Segoe UI", 22, "bold"), text_color="#00ffff").pack(pady=20)
        ctk.CTkLabel(self.right_frame, text="Rezultatul a fost salvat în statistici ✅",
                     text_color="#00ff99", font=("Segoe UI", 14)).pack(pady=10)

    # ========== STATISTICI ==========
    def show_stats(self):
        stats = load_stats()
        summary = get_summary(stats)
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="📊 STATISTICI GENERALE", font=("Segoe UI", 22, "bold")).pack(pady=20)
        if not stats:
            ctk.CTkLabel(self.right_frame, text="Nu există date încă.", font=("Segoe UI", 14)).pack()
            return
        text = f"""
Total sesiuni: {summary['total_sessions']}
Media scorurilor: {summary['avg_score']}%
Cel mai bun scor: {summary['best_score']}%
"""
        ctk.CTkLabel(self.right_frame, text=text, justify="left", font=("Segoe UI", 16)).pack(pady=10)

    # ========== LEADERBOARD ==========
    def show_leaderboard(self):
        stats = load_stats()
        leaders = get_leaderboard(stats)
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="🏆 LEADERBOARD LOCAL", font=("Segoe UI", 22, "bold")).pack(pady=20)
        if not leaders:
            ctk.CTkLabel(self.right_frame, text="Nu există rezultate salvate încă.", font=("Segoe UI", 16)).pack(pady=20)
            return
        for i, entry in enumerate(leaders, 1):
            color = "#FFD700" if i == 1 else "#C0C0C0" if i == 2 else "#CD7F32" if i == 3 else "#00ffff"
            text = f"{i}. {entry['domain'].capitalize()} - {entry['percent']}% ({entry['mode']}, {entry['date']})"
            ctk.CTkLabel(self.right_frame, text=text, text_color=color, font=("Segoe UI", 16, "bold")).pack(pady=4)

    # ========== PDF EXPORT ==========
    def export_pdf_report(self, result):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FEA Quiz Trainer - Raport Sesiune", new_y="NEXT", align="C")
        pdf.set_font("Arial", "", 12)
        for key, val in result.items():
            pdf.cell(0, 10, f"{key.capitalize()}: {val}", new_y="NEXT")
        os.makedirs("data", exist_ok=True)
        pdf.output(os.path.join("data", "last_session_report.pdf"))

    # ========== CLEAR FRAME ==========
    def clear_right_frame(self, keep_progress=False, keep_timer=False):
        for widget in self.right_frame.winfo_children():
            if keep_progress and widget in [getattr(self, "progress_bar", None), getattr(self, "progress_label", None)]:
                continue
            if keep_timer and widget in [getattr(self, "timer_label", None), getattr(self, "timer_bar", None)]:
                continue
            if widget:
                widget.destroy()


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
