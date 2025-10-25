# ui_modern.py
import customtkinter as ctk
from tkinter import messagebox
import time
from data_loader import load_questions  # <- importăm din fișierul existent
from quiz_logic import QuizManager       # <- clasa care gestionează quiz-ul


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ==============================================================
#                      APLICAȚIA PRINCIPALĂ
# ==============================================================

class FEAQuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer 2.0")
        self.geometry("950x650")
        self.resizable(False, False)

        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainMenuFrame, QuizFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuFrame")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()


# ==============================================================
#                        MENIU PRINCIPAL
# ==============================================================

class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_container = ctk.CTkFrame(self)
        main_container.pack(expand=True)

        title = ctk.CTkLabel(main_container, text="FEA QUIZ TRAINER",
                             font=("Poppins", 32, "bold"), text_color="#00E6E6")
        title.pack(pady=(10, 30))

        button_style = {
            "width": 260, "height": 45, "corner_radius": 12,
            "font": ("Poppins", 16, "bold")
        }

        buttons = [
            ("🎯 TRAIN MODE", lambda: self.start_quiz("train")),
            ("🧾 EXAM MODE", lambda: self.start_quiz("exam")),
            ("📈 STATISTICI", self.open_stats),
            ("📊 GRAFIC PROGRES", self.open_chart),
            ("📚 LEARN MODE", self.learn_mode),
            ("🏆 LEADERBOARD", self.leaderboard),
            ("⚙️ SETĂRI", self.open_settings),
        ]

        for text, command in buttons:
            ctk.CTkButton(main_container, text=text, command=command, **button_style).pack(pady=8)

        ctk.CTkButton(main_container, text="⏻ IEȘIRE", fg_color="#CC0000",
                      hover_color="#990000", command=self.controller.destroy,
                      width=180, height=40, font=("Poppins", 14, "bold")).pack(pady=(35, 10))

    def start_quiz(self, mode):
        """Deschide quiz-ul real."""
        frame = self.controller.frames["QuizFrame"]
        frame.load_quiz(mode)
        self.controller.show_frame("QuizFrame")

    # Funcții temporare
    def open_stats(self): messagebox.showinfo("Statistici", "Secțiune în dezvoltare.")
    def open_chart(self): messagebox.showinfo("Grafic progres", "Secțiune în dezvoltare.")
    def learn_mode(self): messagebox.showinfo("Learn Mode", "Secțiune în dezvoltare.")
    def leaderboard(self): messagebox.showinfo("Leaderboard", "Secțiune în dezvoltare.")
    def open_settings(self): messagebox.showinfo("Setări", "Secțiune în dezvoltare.")


# ==============================================================
#                       ECRAN QUIZ (TRAIN / EXAM)
# ==============================================================

class QuizFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.quiz = None
        self.mode = None
        self.current_question = 0

        self.question_label = ctk.CTkLabel(self, text="", font=("Poppins", 20, "bold"), wraplength=800)
        self.question_label.pack(pady=(40, 20))

        self.option_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(self, text="", width=400, height=40,
                                font=("Poppins", 14), command=lambda i=i: self.check_answer(i))
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        self.progress_label = ctk.CTkLabel(self, text="", font=("Poppins", 14))
        self.progress_label.pack(pady=10)

        self.next_button = ctk.CTkButton(self, text="Următoarea ➜", command=self.next_question,
                                         width=180, height=40, font=("Poppins", 14, "bold"))
        self.next_button.pack(pady=20)

        self.back_button = ctk.CTkButton(self, text="⟵ Înapoi la meniu", command=self.go_back,
                                         fg_color="#444", hover_color="#666",
                                         width=180, height=40, font=("Poppins", 14, "bold"))
        self.back_button.pack(pady=10)

    def load_quiz(self, mode):
        """Încarcă întrebările și inițializează quiz-ul."""
        self.mode = mode
        questions = load_questions("mix")  # poți schimba domeniul default
        self.quiz = QuizManager(questions)
        self.current_question = 0
        self.show_question()

    def show_question(self):
        """Afișează întrebarea curentă."""
        q = self.quiz.questions[self.current_question]
        self.question_label.configure(text=f"{self.current_question + 1}/{len(self.quiz.questions)}: {q['question']}")

        for i, opt in enumerate(q['options']):
            self.option_buttons[i].configure(text=opt, state="normal")

        self.progress_label.configure(text=f"Scor curent: {self.quiz.score}")

    def check_answer(self, index):
        """Verifică răspunsul selectat."""
        q = self.quiz.questions[self.current_question]
        correct = q["answer_index"] == index

        if correct:
            self.quiz.score += 1
            messagebox.showinfo("Corect ✅", "Bravo! Răspuns corect.")
        else:
            messagebox.showerror("Greșit ❌", f"Răspuns greșit.\nCorect: {q['options'][q['answer_index']]}")

        for btn in self.option_buttons:
            btn.configure(state="disabled")

    def next_question(self):
        """Trece la următoarea întrebare."""
        if self.current_question < len(self.quiz.questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            messagebox.showinfo("Quiz terminat 🎯",
                                f"Scor final: {self.quiz.score}/{len(self.quiz.questions)}")
            self.go_back()

    def go_back(self):
        """Revenire la meniu."""
        self.controller.show_frame("MainMenuFrame")


# ==============================================================
#                     RULARE APLICAȚIE
# ==============================================================

if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
