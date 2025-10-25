import customtkinter as ctk
from tkinter import messagebox
from quiz_engine_modern import QuizManagerModern
import json
import os


class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurații generale ---
        self.title("FEA Quiz Trainer 2.0")
        self.geometry("900x600")
        self.configure(fg_color="#202020")

        # --- Variabile interne ---
        self.quiz_manager = None

        # --- Layout principal (stânga + dreapta) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # frame stânga (meniul)
        self.left_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#252525")
        self.left_frame.grid(row=0, column=0, sticky="nswe")

        # frame dreapta (conținut dinamic)
        self.right_frame = ctk.CTkFrame(self, fg_color="#202020")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        # --- Meniu principal ---
        self.create_main_menu()

    # ------------------------------------------------------------
    #                   Meniul principal
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
            ("🧠 TRAIN MODE", lambda: self.start_quiz("train")),
            ("🧾 EXAM MODE", lambda: self.start_quiz("exam")),
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
    #                   Încărcare quiz
    # ------------------------------------------------------------
    def start_quiz(self, mode):
        self.clear_right_frame()

        label = ctk.CTkLabel(
            self.right_frame,
            text=f"Se încarcă modul: {mode.upper()}...",
            font=("Segoe UI", 20, "bold"),
            text_color="#00ffff"
        )
        label.pack(pady=30)

        # Încarcă întrebările din fișierul JSON
        data_path = os.path.join("data", "fea_questions.json")
        with open(data_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        # inițializează motorul de quiz
        self.quiz_manager = QuizManagerModern(questions)
        self.mode = mode

        # încarcă prima întrebare
        self.load_quiz()

    def load_quiz(self):
        self.clear_right_frame()
        self.show_question()

    # ------------------------------------------------------------
    #                   Afișare întrebare
    # ------------------------------------------------------------
    def show_question(self):
        q = self.quiz_manager.get_current_question()
        if not q:
            self.show_results()
            return

        self.clear_right_frame()

        # obține lista de variante din cheile compatibile
        options = q.get("choices") or q.get("options") or []

        # titlul întrebării
        question_label = ctk.CTkLabel(
            self.right_frame,
            text=q["question"],
            font=("Segoe UI", 18, "bold"),
            wraplength=700,
            justify="left",
            text_color="white"
        )
        question_label.pack(pady=(30, 20))

        # butoanele pentru răspunsuri
        for i, option in enumerate(options):
            btn = ctk.CTkButton(
                self.right_frame,
                text=option,
                command=lambda idx=i: self.handle_answer(idx),
                width=600,
                height=35,
                fg_color="#1E5BA6",
                hover_color="#297BE6",
                font=("Segoe UI", 14)
            )
            btn.pack(pady=8)

    # ------------------------------------------------------------
    #                   Verificare răspuns
    # ------------------------------------------------------------
    def handle_answer(self, idx):
        correct, correct_text, explanation = self.quiz_manager.check_answer(idx)

        self.clear_right_frame()

        result_text = "✅ Corect!" if correct else "❌ Greșit!"
        color = "#00ff99" if correct else "#ff4444"

        result_label = ctk.CTkLabel(
            self.right_frame,
            text=result_text,
            text_color=color,
            font=("Segoe UI", 22, "bold")
        )
        result_label.pack(pady=20)

        correct_label = ctk.CTkLabel(
            self.right_frame,
            text=f"Răspuns corect: {correct_text}",
            text_color="white",
            font=("Segoe UI", 16),
            wraplength=700
        )
        correct_label.pack(pady=(10, 5))

        expl_label = ctk.CTkLabel(
            self.right_frame,
            text=f"Explicație: {explanation}",
            text_color="#cccccc",
            font=("Segoe UI", 14),
            wraplength=700,
            justify="left"
        )
        expl_label.pack(pady=10)

        next_btn = ctk.CTkButton(
            self.right_frame,
            text="Continuă ➜",
            command=self.next_question,
            font=("Segoe UI", 14, "bold"),
            fg_color="#1E5BA6",
            hover_color="#297BE6",
            width=150
        )
        next_btn.pack(pady=20)

    # ------------------------------------------------------------
    #                   Următoarea întrebare
    # ------------------------------------------------------------
    def next_question(self):
        if self.quiz_manager.advance():
            self.show_question()
        else:
            self.show_results()

    # ------------------------------------------------------------
    #                   Rezultate finale
    # ------------------------------------------------------------
    def show_results(self):
        self.clear_right_frame()

        total = self.quiz_manager.total_questions()
        score = self.quiz_manager.score
        percent = round(score / total * 100, 1)

        result_label = ctk.CTkLabel(
            self.right_frame,
            text=f"Rezultat final: {score}/{total}  ({percent}%)",
            font=("Segoe UI", 22, "bold"),
            text_color="#00ffff"
        )
        result_label.pack(pady=(60, 10))

        back_btn = ctk.CTkButton(
            self.right_frame,
            text="⬅ Înapoi la meniu",
            command=self.clear_right_frame,
            font=("Segoe UI", 14),
            width=180,
            fg_color="#1E5BA6",
            hover_color="#297BE6"
        )
        back_btn.pack(pady=20)

    # ------------------------------------------------------------
    #                   Alte secțiuni (placeholder)
    # ------------------------------------------------------------
    def show_stats(self):
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="📊 Statistici — în dezvoltare", font=("Segoe UI", 20, "bold")).pack(pady=40)

    def show_progress(self):
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="📈 Grafic progres — în dezvoltare", font=("Segoe UI", 20, "bold")).pack(pady=40)

    def show_learn_mode(self):
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="📚 Learn Mode — în dezvoltare", font=("Segoe UI", 20, "bold")).pack(pady=40)

    def show_leaderboard(self):
        self.clear_right_frame()
        ctk.CTkLabel(self.right_frame, text="🏆 Le_
