# ui_modern.py — FEA Quiz Trainer 4.3 FINAL (PDF + popup + stabilitate)
import customtkinter as ctk
import json
import os
from tkinter import messagebox
from quiz_engine_modern import QuizManagerModern
from stats_manager import add_session, load_stats, get_summary, get_leaderboard
from pdf_exporter_modern import export_pdf_modern


class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 4.3 — PDF + Popup + Stabilitate")
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

    # ===== MENIU PRINCIPAL =====
    def create_main_menu(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.left_frame, text="FEA QUIZ TRAINER", font=("Segoe UI", 22, "bold"), text_color="#00ffff").pack(pady=(30, 20))

        buttons = [
            ("🧠 TRAIN MODE", lambda: self.show_quiz_setup("train")),
            ("🧾 EXAM MODE",  lambda: self.show_quiz_setup("exam")),
            ("📊 STATISTICI", self.show_stats),
            ("🏆 LEADERBOARD", self.show_leaderboard),
            ("📄 EXPORTĂ PDF DIN NOU", self.manual_export_pdf),
        ]

        for text, cmd in buttons:
            ctk.CTkButton(self.left_frame, text=text, command=cmd, font=("Segoe UI", 14, "bold"),
                          height=40, width=180, fg_color="#1E5BA6", hover_color="#297BE6").pack(pady=8)

        ctk.CTkButton(self.left_frame, text="⬅ Ieșire", command=self.quit, font=("Segoe UI", 14, "bold"),
                      height=40, width=180, fg_color="#A60000", hover_color="#C30000").pack(side="bottom", pady=20)

        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame,
                     text="Bine ai venit în FEA Quiz Trainer 👋\nAlege un mod din stânga.",
                     font=("Segoe UI", 18, "bold"), text_color="#ffffff", justify="left").pack(pady=60)

    # ===== CONFIGURARE QUIZ =====
    def show_quiz_setup(self, mode):
        setup = ctk.CTkToplevel(self)
        setup.title("Configurare Quiz")
        setup.geometry("400x350")
        setup.grab_set()

        ctk.CTkLabel(setup, text="Domeniu:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        domain_var = ctk.StringVar(value="mix")
        ctk.CTkComboBox(setup, variable=domain_var,
                        values=["mix", "structural", "crash", "cfd", "nvh"], width=200).pack(pady=5)

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

        ctk.CTkButton(setup, text="Start Quiz", command=confirm, fg_color="#1E5BA6").pack(pady=20)

    # ===== START QUIZ =====
    def start_quiz(self, mode, domain, num_questions, time_min):
        with open(os.path.join("data", "fea_questions.json"), "r", encoding="utf-8") as f:
            questions = json.load(f)

        self.quiz_manager = QuizManagerModern(questions, domain, num_questions)
        self.mode = mode
        self.time_left = time_min * 60
        self.total_time = self.time_left
        self.time_used = 0
        self.timer_running = True

        # Stil vizual diferit pentru moduri
        if self.mode == "train":
            self.color_mode_name = "TRAIN MODE"
            self.color_mode_fg = "#00ffff"
            self.color_progress = "#00ffff"
        else:
            self.color_mode_name = "EXAM MODE"
            self.color_mode_fg = "#ffcc00"
            self.color_progress = "#ffaa00"

        self.load_quiz()
        self.update_timer()

    # ===== ÎNCĂRCARE QUIZ =====
    def load_quiz(self):
        self.clear_right_frame()
        self.create_timer()
        self.create_progress_bar()
        self.show_question()

    # ===== TIMER =====
    def create_timer(self):
        header_text = f"{self.color_mode_name} | Timp rămas:"
        self.timer_header_label = ctk.CTkLabel(self.right_frame, text=header_text, font=("Segoe UI", 16, "bold"),
                                               text_color=self.color_mode_fg)
        self.timer_header_label.pack(pady=(10, 0))

        self.timer_label = ctk.CTkLabel(self.right_frame, text="", font=("Segoe UI", 16, "bold"), text_color="#ffffff")
        self.timer_label.pack(pady=(2, 0))

        self.timer_bar = ctk.CTkProgressBar(self.right_frame, width=400)
        self.timer_bar.pack(pady=5)
        self.timer_bar.set(1)
        self.timer_bar.configure(progress_color=self.color_progress)

    def update_timer(self):
        if not self.timer_running:
            return
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.configure(text=f"{mins:02}:{secs:02}")
        self.timer_bar.set(self.time_left / self.total_time if self.total_time else 0)

        if self.time_left <= 0:
            self.show_results()
            return

        self.time_left -= 1
        self.time_used += 1
        self.after(1000, self.update_timer)

    # ===== PROGRES =====
    def create_progress_bar(self):
        self.progress_label = ctk.CTkLabel(self.right_frame, text="", font=("Segoe UI", 14))
        self.progress_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self.right_frame, width=400)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=self.color_progress)

    def update_progress(self):
        current = self.quiz_manager.current_index + 1
        total = self.quiz_manager.total_questions()
        pct = (current / total) if total else 0
        self.progress_bar.set(pct)
        self.progress_label.configure(text=f"Întrebarea {current}/{total}", text_color=self.color_mode_fg)

    # ===== ÎNTREBĂRI =====
    def show_question(self):
        q = self.quiz_manager.get_current_question()
        if not q:
            self.show_results()
            return

        self.clear_right_frame(keep_progress=True, keep_timer=True)
        self.update_progress()

        domain = q.get("domain", "General").capitalize()
        domain_color = {"Structural": "#00ffaa", "Crash": "#ff4444", "Cfd": "#44aaff", "Nvh": "#ffcc00"}.get(domain, "#cccccc")
        ctk.CTkLabel(self.right_frame, text=f"🏷 Domeniu: {domain}", font=("Segoe UI", 14, "bold"),
                     text_color=domain_color).pack(pady=(10, 0))

        ctk.CTkLabel(self.right_frame, text=q["question"], wraplength=700, font=("Segoe UI", 18, "bold"),
                     text_color="white").pack(pady=20)

        for i, opt in enumerate(q["choices"]):
            ctk.CTkButton(self.right_frame, text=opt, font=("Segoe UI", 14),
                          fg_color="#1E5BA6", hover_color="#297BE6", width=600,
                          command=lambda idx=i: self.handle_answer(idx)).pack(pady=6)

    # ===== RĂSPUNSURI =====
    def handle_answer(self, idx):
        correct, correct_text, explanation = self.quiz_manager.check_answer(idx)
        if self.mode == "exam":
            self.next_question()
            return

        self.clear_right_frame(keep_progress=True, keep_timer=True)
        msg = "✅ Corect!" if correct else "❌ Greșit!"
        color = "#00ff99" if correct else "#ff4444"
        ctk.CTkLabel(self.right_frame, text=msg, text_color=color, font=("Segoe UI", 22, "bold")).pack(pady=15)
        ctk.CTkLabel(self.right_frame, text=f"Răspuns corect: {correct_text}", text_color="white").pack(pady=5)
        ctk.CTkLabel(self.right_frame, text=f"Explicație: {explanation}", text_color="#cccccc", wraplength=700).pack(pady=10)

        if self.quiz_manager.current_index + 1 < self.quiz_manager.total_questions():
            ctk.CTkButton(self.right_frame, text="Continuă ➜", command=self.next_question, fg_color="#1E5BA6").pack(pady=15)
        else:
            ctk.CTkButton(self.right_frame, text="Finalizare antrenament ➜", command=self.show_results, fg_color="#1E5BA6").pack(pady=15)

    def next_question(self):
        if self.quiz_manager.advance():
            self.show_question()
        else:
            self.show_results()

    # ===== REZULTATE =====
    def show_results(self):
        self.timer_running = False
        result = self.quiz_manager.get_result_data(self.mode, self.time_used)
        self.last_result = result
        add_session(result)

        pdf_path = export_pdf_modern(result, self.quiz_manager.user_answers if self.mode == "train" else None)
        if pdf_path:
            messagebox.showinfo("Raport generat", f"Raportul PDF a fost salvat în:\n{pdf_path}")

        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text=f"Rezultat final: {result['percent']}%", font=("Segoe UI", 24, "bold"),
                     text_color="#00ffff").pack(pady=20)
        if self.mode == "train":
            self.show_train_finish(result)
        else:
            self.show_exam_summary(result)

    def show_train_finish(self, result):
        ctk.CTkLabel(self.right_frame, text="🏁 Antrenamentul s-a încheiat!", text_color="#00ff99",
                     font=("Segoe UI", 20, "bold")).pack(pady=10)
        ctk.CTkButton(self.right_frame, text="📄 Deschide PDF", fg_color="#1E5BA6",
                      command=lambda: os.startfile("data/last_session_report.pdf")).pack(pady=10)
        ctk.CTkButton(self.right_frame, text="⬅ Înapoi la meniu principal", fg_color="#1E5BA6",
                      command=self.reset_to_menu).pack(pady=20)

    def show_exam_summary(self, result):
        ctk.CTkLabel(self.right_frame, text=f"Întrebări corecte: {result['correct']}/{result['total']}  "
                                            f"Scor: {result['percent']}%", text_color="white",
                     font=("Segoe UI", 18, "bold")).pack(pady=15)
        ctk.CTkButton(self.right_frame, text="📄 Deschide PDF", fg_color="#1E5BA6",
                      command=lambda: os.startfile("data/last_session_report.pdf")).pack(pady=10)
        ctk.CTkButton(self.right_frame, text="⬅ Înapoi la meniu principal", fg_color="#1E5BA6",
                      command=self.reset_to_menu).pack(pady=20)

    # ===== DIVERSE =====
    def manual_export_pdf(self):
        self.clear_right_frame()
        if not self.last_result:
            ctk.CTkLabel(self.right_frame, text="⚠️ Nu există o sesiune finalizată recent!",
                         text_color="#ff6666", font=("Segoe UI", 18, "bold")).pack(pady=20)
            return
        pdf_path = export_pdf_modern(self.last_result)
        if pdf_path:
            messagebox.showinfo("Raport generat", f"Raportul PDF a fost salvat în:\n{pdf_path}")

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
        txt = (f"Total sesiuni: {summary['total_sessions']}\n"
               f"Media scorurilor: {summary['avg_score']}%\n"
               f"Cel mai bun scor: {summary['best_score']}%\n")
        ctk.CTkLabel(self.right_frame, text=txt, justify="left",
                     font=("Segoe UI", 18, "bold"), text_color="#ffffff").pack(pady=20)

    def show_leaderboard(self):
        stats = load_stats()
        leaders = get_leaderboard(stats)
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="🏆 LEADERBOARD LOCAL",
                     font=("Segoe UI", 22, "bold"), text_color="#00ffff").pack(pady=20)
        if not leaders:
            ctk.CTkLabel(self.right_frame, text="Nicio sesiune înregistrată încă.",
                         font=("Segoe UI", 16), text_color="#ffffff").pack(pady=10)
            return
        for i, s in enumerate(leaders, 1):
            color = "#FFD700" if i == 1 else "#00ffff" if i == 2 else "#ff9933"
            ctk.CTkLabel(self.right_frame,
                         text=f"{i}. {s['domain'].capitalize()} - {s['percent']}% ({s['mode']}, {s['date']})",
                         text_color=color, font=("Segoe UI", 16, "bold")).pack(pady=5)

    def reset_to_menu(self):
        self.timer_running = False
        self.quiz_manager = None
        self.clear_right_frame()
        self.create_main_menu()

    def clear_right_frame(self, keep_progress=False, keep_timer=False):
        for widget in self.right_frame.winfo_children():
            if keep_progress and widget in [getattr(self, "progress_bar", None),
                                            getattr(self, "progress_label", None)]:
                continue
            if keep_timer and widget in [getattr(self, "timer_bar", None),
                                         getattr(self, "timer_label", None),
                                         getattr(self, "timer_header_label", None)]:
                continue
            widget.destroy()


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
