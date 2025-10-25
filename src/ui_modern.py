# ui_modern.py — FEA Quiz Trainer 5.0 VISUAL EDITION
# BAZAT PE versiunea ta 4.5, păstrat TOT, adăugat:
# - Learn Mode cu imagini (din data/docs/*.json + data/images/...)
# - Imagini în întrebări (quiz) + în feedback-ul din Train Mode

import customtkinter as ctk
import json
import os
from tkinter import messagebox
from tkinter import Frame, Canvas, Scrollbar
from PIL import Image  # <--- nou
from quiz_engine_modern import QuizManagerModern
from stats_manager import add_session, load_stats, get_summary, get_leaderboard
from pdf_exporter_modern import export_pdf_modern


class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 5.0 — Visual Edition")
        self.geometry("900x600")
        self.configure(fg_color="#202020")

        self.quiz_manager = None
        self.mode = None
        self.time_left = 0
        self.total_time = 0
        self.time_used = 0
        self.timer_running = False
        self.last_result = None

        # pentru imagini afișate în quiz / learn mode (ca să nu fie garbage collected)
        self.current_question_image = None
        self.current_learn_images = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#252525")
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.right_frame = ctk.CTkFrame(self, fg_color="#202020")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.create_main_menu()

    # ===================== HELPER IMAGINI =====================
    def load_ctk_image(self, rel_path, size=(500, 300)):
        """
        Încarcă o imagine din folderul data/... și o întoarce ca CTkImage.
        Dacă nu găsește sau nu poate încărca -> return None.
        """
        if not rel_path:
            return None
        img_path = os.path.join("data", rel_path)
        if not os.path.exists(img_path):
            return None

        try:
            pil_img = Image.open(img_path)
            pil_img = pil_img.convert("RGBA")
            # redimensionare păstrând raportul
            pil_img.thumbnail(size)
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        except Exception as e:
            print(f"[WARN] Nu pot încărca imaginea {img_path}: {e}")
            return None

    # ========== MENIU PRINCIPAL ==========
    def create_main_menu(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.left_frame,
            text="FEA QUIZ TRAINER",
            font=("Segoe UI", 22, "bold"),
            text_color="#00ffff"
        ).pack(pady=(30, 20))

        buttons = [
            ("🧠 TRAIN MODE", lambda: self.show_quiz_setup("train")),
            ("🧾 EXAM MODE", lambda: self.show_quiz_setup("exam")),
            ("📚 LEARN MODE", self.show_learn_mode),
            ("📊 STATISTICI", self.show_stats),
            ("🏆 LEADERBOARD", self.show_leaderboard),
            ("📄 EXPORTĂ PDF DIN NOU", self.manual_export_pdf),
        ]

        for text, cmd in buttons:
            ctk.CTkButton(
                self.left_frame,
                text=text,
                command=cmd,
                font=("Segoe UI", 14, "bold"),
                height=40,
                width=180,
                fg_color="#1E5BA6",
                hover_color="#297BE6"
            ).pack(pady=8)

        ctk.CTkButton(
            self.left_frame,
            text="⬅ Ieșire",
            command=self.quit,
            font=("Segoe UI", 14, "bold"),
            height=40,
            width=180,
            fg_color="#A60000",
            hover_color="#C30000"
        ).pack(side="bottom", pady=20)

        self.clear_right_frame()
        ctk.CTkLabel(
            self.right_frame,
            text="Bine ai venit în FEA Quiz Trainer 👋\nAlege un mod din stânga.",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
            justify="left"
        ).pack(pady=60)

    # ========== QUIZ SETUP ==========
    def show_quiz_setup(self, mode):
        setup = ctk.CTkToplevel(self)
        setup.title("Configurare Quiz")
        setup.geometry("400x350")
        setup.grab_set()

        ctk.CTkLabel(setup, text="Domeniu:", font=("Segoe UI", 14, "bold")).pack(pady=10)
        domain_var = ctk.StringVar(value="mix")
        ctk.CTkComboBox(
            setup,
            variable=domain_var,
            values=["mix", "structural", "crash", "cfd", "nvh"],
            width=200
        ).pack(pady=5)

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

        ctk.CTkButton(
            setup,
            text="Start Quiz",
            command=confirm,
            fg_color="#1E5BA6"
        ).pack(pady=20)

    # ========== START QUIZ ==========
    def start_quiz(self, mode, domain, num_questions, time_min):
        with open(os.path.join("data", "fea_questions.json"), "r", encoding="utf-8") as f:
            questions = json.load(f)

        self.quiz_manager = QuizManagerModern(questions, domain, num_questions)
        self.mode = mode
        self.time_left = time_min * 60
        self.total_time = self.time_left
        self.time_used = 0
        self.timer_running = True

        self.color_mode_name = "TRAIN MODE" if mode == "train" else "EXAM MODE"
        self.color_mode_fg = "#00ffff" if mode == "train" else "#ffcc00"
        self.color_progress = "#00ffff" if mode == "train" else "#ffaa00"

        self.load_quiz()
        self.update_timer()

    def load_quiz(self):
        self.clear_right_frame()
        self.create_timer()
        self.create_progress_bar()
        self.show_question()

    # ========== TIMER ==========
    def create_timer(self):
        header_text = f"{self.color_mode_name} | Timp rămas:"
        self.timer_header_label = ctk.CTkLabel(
            self.right_frame,
            text=header_text,
            font=("Segoe UI", 16, "bold"),
            text_color=self.color_mode_fg
        )
        self.timer_header_label.pack(pady=(10, 0))

        self.timer_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        )
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

    # ========== PROGRES ==========
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
        self.progress_label.configure(
            text=f"Întrebarea {current}/{total}",
            text_color=self.color_mode_fg
        )

    # ========== ÎNTREBARE ==========
    def show_question(self):
        q = self.quiz_manager.get_current_question()
        if not q:
            self.show_results()
            return

        self.clear_right_frame(keep_progress=True, keep_timer=True)
        self.update_progress()

        # întrebarea
        ctk.CTkLabel(
            self.right_frame,
            text=q["question"],
            wraplength=700,
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        ).pack(pady=(15, 10))

        # imagine întrebare (dacă există în JSON field "image": "images/...png")
        self.current_question_image = None
        img_obj = self.load_ctk_image(q.get("image", ""), size=(500, 300))
        if img_obj:
            self.current_question_image = img_obj  # păstrăm referința
            ctk.CTkLabel(
                self.right_frame,
                image=img_obj,
                text=""
            ).pack(pady=(5, 15))

        # opțiuni
        for i, opt in enumerate(q["choices"]):
            ctk.CTkButton(
                self.right_frame,
                text=opt,
                font=("Segoe UI", 14),
                fg_color="#1E5BA6",
                hover_color="#297BE6",
                width=600,
                command=lambda idx=i: self.handle_answer(idx)
            ).pack(pady=6)

    # ========== RĂSPUNS ==========
    def handle_answer(self, idx):
        correct, correct_text, explanation = self.quiz_manager.check_answer(idx)

        # în EXAM nu dăm feedback imediat
        if self.mode == "exam":
            self.next_question()
            return

        # TRAIN → feedback imediat
        self.clear_right_frame(keep_progress=True, keep_timer=True)

        msg = "✅ Corect!" if correct else "❌ Greșit!"
        color = "#00ff99" if correct else "#ff4444"

        ctk.CTkLabel(
            self.right_frame,
            text=msg,
            text_color=color,
            font=("Segoe UI", 22, "bold")
        ).pack(pady=15)

        ctk.CTkLabel(
            self.right_frame,
            text=f"Răspuns corect: {correct_text}",
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            self.right_frame,
            text=f"Explicație: {explanation}",
            text_color="#cccccc",
            wraplength=700
        ).pack(pady=10)

        # reafișăm imaginea întrebării și la feedback, dacă există
        current_q = self.quiz_manager.questions[self.quiz_manager.current_index]
        self.current_question_image = None
        img_obj = self.load_ctk_image(current_q.get("image", ""), size=(500, 300))
        if img_obj:
            self.current_question_image = img_obj
            ctk.CTkLabel(
                self.right_frame,
                image=img_obj,
                text=""
            ).pack(pady=(10, 15))

        if self.quiz_manager.current_index + 1 < self.quiz_manager.total_questions():
            ctk.CTkButton(
                self.right_frame,
                text="Continuă ➜",
                command=self.next_question,
                fg_color="#1E5BA6"
            ).pack(pady=15)
        else:
            ctk.CTkButton(
                self.right_frame,
                text="Finalizare ➜",
                command=self.show_results,
                fg_color="#1E5BA6"
            ).pack(pady=15)

    def next_question(self):
        if self.quiz_manager.advance():
            self.show_question()
        else:
            self.show_results()

    # ========== FINAL QUIZ ==========
    def show_results(self):
        self.timer_running = False

        result = self.quiz_manager.get_result_data(self.mode, self.time_used)
        self.last_result = result
        add_session(result)

        pdf_path = export_pdf_modern(
            result,
            self.quiz_manager.user_answers if self.mode == "train" else None
        )
        if pdf_path:
            messagebox.showinfo("Raport generat", f"Raportul PDF a fost salvat în:\n{pdf_path}")

        self.clear_right_frame()

        ctk.CTkLabel(
            self.right_frame,
            text=f"Rezultat final: {result['percent']}%",
            font=("Segoe UI", 24, "bold"),
            text_color="#00ffff"
        ).pack(pady=20)

        if self.mode == "train":
            self.show_train_finish()
        else:
            self.show_exam_review()

    def show_train_finish(self):
        ctk.CTkLabel(
            self.right_frame,
            text="🏁 Antrenamentul s-a încheiat!",
            text_color="#00ff99",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)

        ctk.CTkButton(
            self.right_frame,
            text="📄 Deschide PDF",
            fg_color="#1E5BA6",
            command=lambda: os.startfile("data/last_session_report.pdf")
        ).pack(pady=10)

        ctk.CTkButton(
            self.right_frame,
            text="⬅ Înapoi la meniu principal",
            fg_color="#1E5BA6",
            command=self.reset_to_menu
        ).pack(pady=20)

    # feedback cu scroll după EXAM
    def show_exam_review(self):
        ctk.CTkLabel(
            self.right_frame,
            text="📋 Revizuire examen",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffaa00"
        ).pack(pady=10)

        # container scroll
        container = Frame(self.right_frame, bg="#202020")
        canvas = Canvas(container, bg="#202020", highlightthickness=0)
        scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#202020")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, ans in enumerate(self.quiz_manager.user_answers):
            q = ans.get("question", "")
            correct = ans.get("correct", "")
            selected = ans.get("selected", "")
            expl = ans.get("explanation", "")
            is_correct = ans.get("is_correct", False)

            bg = "#003300" if is_correct else "#330000"
            fg = "#00ff99" if is_correct else "#ff6666"

            card = Frame(scrollable_frame, bg=bg, padx=10, pady=8)
            card.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(card, text=f"{i+1}. {q}",
                         font=("Segoe UI", 14, "bold"),
                         text_color="white",
                         wraplength=650).pack(anchor="w")

            ctk.CTkLabel(card, text=f"Răspuns ales: {selected}",
                         font=("Segoe UI", 13),
                         text_color=fg).pack(anchor="w")

            ctk.CTkLabel(card, text=f"Corect: {correct}",
                         font=("Segoe UI", 13),
                         text_color="#00ffff").pack(anchor="w")

            ctk.CTkLabel(card, text=f"Explicație: {expl}",
                         font=("Segoe UI", 12),
                         text_color="#cccccc",
                         wraplength=650).pack(anchor="w")

        ctk.CTkButton(
            self.right_frame,
            text="⬅ Înapoi la meniu principal",
            fg_color="#1E5BA6",
            command=self.reset_to_menu
        ).pack(pady=15)

    # ========== LEARN MODE ==========
    def show_learn_mode(self):
        self.clear_right_frame()

        ctk.CTkLabel(
            self.right_frame,
            text="📚 Learn Mode",
            font=("Segoe UI", 22, "bold"),
            text_color="#00ffff"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self.right_frame,
            text="Alege un domeniu pentru a citi teoria:",
            font=("Segoe UI", 16),
            text_color="#ffffff"
        ).pack(pady=(0, 20))

        # butoane domeniu
        domains = [
            ("STRUCTURAL", "structural"),
            ("CRASH & SAFETY", "crash"),
            ("CFD / FLUID", "cfd"),
            ("NVH / ACUSTICĂ", "nvh")
        ]

        btn_frame = ctk.CTkFrame(self.right_frame, fg_color="#2a2a2a", corner_radius=8)
        btn_frame.pack(pady=10)

        for label, key in domains:
            ctk.CTkButton(
                btn_frame,
                text=label,
                width=250,
                fg_color="#1E5BA6",
                hover_color="#297BE6",
                font=("Segoe UI", 14, "bold"),
                command=lambda k=key: self.open_doc(k)
            ).pack(pady=8, padx=20)

        ctk.CTkButton(
            self.right_frame,
            text="⬅ Înapoi la meniu principal",
            fg_color="#1E5BA6",
            command=self.reset_to_menu
        ).pack(pady=25)

    def open_doc(self, domain_key):
        """
        Încarcă fișierul JSON cu teoria (data/docs/<domain>.json)
        și îl afișează într-un frame derulabil.
        Fiecare secțiune poate avea text + imagine.
        """
        path = os.path.join("data", "docs", f"{domain_key}.json")
        if not os.path.exists(path):
            messagebox.showwarning("Lipsă conținut", f"Nu există încă material pentru '{domain_key}'.")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        title = data.get("title", domain_key.upper())
        sections = data.get("sections", [])

        self.clear_right_frame()

        # titlu pagină
        ctk.CTkLabel(
            self.right_frame,
            text=f"📘 {title}",
            font=("Segoe UI", 20, "bold"),
            text_color="#00ffff"
        ).pack(pady=(15, 10))

        # container scrollabil pentru lecție
        container = Frame(self.right_frame, bg="#202020")
        canvas = Canvas(container, bg="#202020", highlightthickness=0)
        scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#202020")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", _on_configure)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True, padx=5, pady=5)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # resetăm cache-ul de imagini pentru lecție
        self.current_learn_images = []

        # umplem cu secțiuni
        for sec in sections:
            sub = sec.get("subtitle", "")
            txt = sec.get("content", "")
            img_rel = sec.get("image", "")

            block = Frame(scrollable_frame, bg="#2a2a2a", padx=12, pady=10)
            block.pack(fill="x", padx=5, pady=8)

            if sub:
                ctk.CTkLabel(
                    block,
                    text=sub,
                    font=("Segoe UI", 15, "bold"),
                    text_color="#00ffff",
                    wraplength=650,
                    justify="left"
                ).pack(anchor="w")

            if txt:
                ctk.CTkLabel(
                    block,
                    text=txt,
                    font=("Segoe UI", 13),
                    text_color="#ffffff",
                    wraplength=650,
                    justify="left"
                ).pack(anchor="w", pady=(4, 8))

            # dacă secțiunea are imagine și ea există pe disc -> afișăm
            img_obj = self.load_ctk_image(img_rel, size=(800, 400))
            if img_obj:
                self.current_learn_images.append(img_obj)  # păstrăm referința
                ctk.CTkLabel(
                    block,
                    image=img_obj,
                    text=""
                ).pack(anchor="w", pady=(0, 8))

        # butoane back jos
        ctk.CTkButton(
            self.right_frame,
            text="⬅ Înapoi la domenii",
            fg_color="#1E5BA6",
            command=self.show_learn_mode
        ).pack(pady=15)

        ctk.CTkButton(
            self.right_frame,
            text="⬅ Înapoi la meniu principal",
            fg_color="#1E5BA6",
            command=self.reset_to_menu
        ).pack(pady=(0, 20))

    # ========== ALTE SECȚIUNI (stats / leaderboard / pdf export manual) ==========
    def manual_export_pdf(self):
        self.clear_right_frame()
        if not self.last_result:
            ctk.CTkLabel(
                self.right_frame,
                text="⚠️ Nu există o sesiune finalizată recent!",
                text_color="#ff6666",
                font=("Segoe UI", 18, "bold")
            ).pack(pady=20)
            return

        pdf_path = export_pdf_modern(self.last_result)
        if pdf_path:
            messagebox.showinfo("Raport generat", f"Raportul PDF a fost salvat în:\n{pdf_path}")

    def show_stats(self):
        stats = load_stats()
        summary = get_summary(stats)

        self.clear_right_frame()
        ctk.CTkLabel(
            self.right_frame,
            text="📊 STATISTICI GENERALE",
            font=("Segoe UI", 22, "bold"),
            text_color="#00ffff"
        ).pack(pady=20)

        if not stats:
            ctk.CTkLabel(
                self.right_frame,
                text="Nu există date încă.",
                font=("Segoe UI", 16),
                text_color="#ffffff"
            ).pack(pady=10)
            return

        txt = (
            f"Total sesiuni: {summary['total_sessions']}\n"
            f"Media scorurilor: {summary['avg_score']}%\n"
            f"Cel mai bun scor: {summary['best_score']}%\n"
        )

        ctk.CTkLabel(
            self.right_frame,
            text=txt,
            justify="left",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff"
        ).pack(pady=20)

    def show_leaderboard(self):
        stats = load_stats()
        leaders = get_leaderboard(stats)

        self.clear_right_frame()
        ctk.CTkLabel(
            self.right_frame,
            text="🏆 LEADERBOARD LOCAL",
            font=("Segoe UI", 22, "bold"),
            text_color="#00ffff"
        ).pack(pady=20)

        if not leaders:
            ctk.CTkLabel(
                self.right_frame,
                text="Nicio sesiune înregistrată încă.",
                font=("Segoe UI", 16),
                text_color="#ffffff"
            ).pack(pady=10)
            return

        for i, s in enumerate(leaders, 1):
            color = "#FFD700" if i == 1 else "#00ffff" if i == 2 else "#ff9933"
            ctk.CTkLabel(
                self.right_frame,
                text=f"{i}. {s['domain'].capitalize()} - {s['percent']}% ({s['mode']}, {s['date']})",
                text_color=color,
                font=("Segoe UI", 16, "bold")
            ).pack(pady=5)

    # ========== UTILITARE ==========
    def reset_to_menu(self):
        self.timer_running = False
        self.quiz_manager = None
        self.current_question_image = None
        self.current_learn_images = []
        self.clear_right_frame()
        self.create_main_menu()

    def clear_right_frame(self, keep_progress=False, keep_timer=False):
        for widget in self.right_frame.winfo_children():
            if keep_progress and widget in [
                getattr(self, "progress_bar", None),
                getattr(self, "progress_label", None)
            ]:
                continue
            if keep_timer and widget in [
                getattr(self, "timer_bar", None),
                getattr(self, "timer_label", None),
                getattr(self, "timer_header_label", None)
            ]:
                continue
            widget.destroy()


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
