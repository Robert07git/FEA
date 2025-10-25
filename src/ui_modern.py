# ui_modern.py
import customtkinter as ctk
from tkinter import messagebox
from data_loader import load_questions
from quiz_engine_modern import QuizManagerModern


# === Setări generale de interfață ===
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

        # container pentru toate frame-urile
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainMenuFrame, QuizFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuFrame")

    def show_frame(self, frame_name):
        """Afișează un frame (ecran) după nume."""
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

        title = ctk.CTkLabel(
            main_container,
            text="FEA QUIZ TRAINER",
            font=("Poppins", 32, "bold"),
            text_color="#00E6E6"
        )
        title.pack(pady=(10, 30))

        button_style = {
            "width": 260,
            "height": 45,
            "corner_radius": 12,
            "font": ("Poppins", 16, "bold")
        }

        # butoanele principale
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

        # buton de ieșire
        ctk.CTkButton(
            main_container,
            text="⏻ IEȘIRE",
            fg_color="#CC0000",
            hover_color="#990000",
            command=self.controller.destroy,
            width=180,
            height=40,
            font=("Poppins", 14, "bold")
        ).pack(pady=(35, 10))

    def start_quiz(self, mode):
        """Deschide ecranul de quiz (TRAIN sau EXAM)."""
        frame = self.controller.frames["QuizFrame"]
        frame.load_quiz(mode)
        self.controller.show_frame("QuizFrame")

    # funcții temporare (pentru alte secțiuni)
    def open_stats(self): messagebox.showinfo("Statistici", "Secțiune în dezvoltare.")
    def open_chart(self): messagebox.showinfo("Grafic progres", "Secțiune în dezvoltare.")
    def learn_mode(self): messagebox.showinfo("Learn Mode", "Secțiune în dezvoltare.")
    def leaderboard(self): messagebox.showinfo("Leaderboard", "Secțiune în dezvoltare.")
    def open_settings(self): messagebox.showinfo("Setări", "Secțiune în dezvoltare.")


# ==============================================================
#                      ECRAN QUIZ (TRAIN / EXAM)
# ==============================================================

class QuizFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.quiz = None
        self.mode = None  # "train" sau "exam"

        # Titlu / întrebare
        self.question_label = ctk.CTkLabel(
            self,
            text="",
            font=("Poppins", 20, "bold"),
            wraplength=800,
            justify="left"
        )
        self.question_label.pack(pady=(40, 20))

        # Butoane pentru răspunsuri
        self.option_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(
                self,
                text="",
                width=500,
                height=40,
                font=("Poppins", 14),
                command=lambda i=i: self.check_answer(i)
            )
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        # Status (scor / progres)
        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=("Poppins", 14)
        )
        self.progress_label.pack(pady=15)

        # Buton "Următoarea"
        self.next_button = ctk.CTkButton(
            self,
            text="Următoarea ➜",
            command=self.next_question,
            width=180,
            height=40,
            font=("Poppins", 14, "bold")
        )
        self.next_button.pack(pady=(10, 20))

        # Buton "Înapoi la meniu"
        self.back_button = ctk.CTkButton(
            self,
            text="⟵ Înapoi la meniu",
            fg_color="#444",
            hover_color="#666",
            command=self.go_back,
            width=180,
            height=40,
            font=("Poppins", 14, "bold")
        )
        self.back_button.pack(pady=(10, 20))


    def load_quiz(self, mode):
        """Se apelează când utilizatorul apasă TRAIN/EXAM din meniu."""
        self.mode = mode
        questions = load_questions("mix")  # Domeniu implicit (deocamdată)
        self.quiz = QuizManagerModern(questions)
        self.show_question()


    def show_question(self):
        """Afișează întrebarea curentă și opțiunile."""
        q = self.quiz.get_current_question()
        if q is None:
            self.finish_quiz()
            return

        idx_curent = self.quiz.current_index + 1
        total = self.quiz.total_questions()
        self.question_label.configure(
            text=f"Întrebarea {idx_curent}/{total}:\n\n{q['question']}"
        )

        for i, btn in enumerate(self.option_buttons):
            if i < len(q["options"]):
                btn.configure(text=q["options"][i], state="normal")
                btn.pack(pady=5)
            else:
                btn.pack_forget()

        self.progress_label.configure(text=f"Scor curent: {self.quiz.score}")
        self.next_button.configure(state="disabled")


    def check_answer(self, selected_index):
        """Verifică răspunsul selectat."""
        is_correct, correct_text, explanation = self.quiz.check_answer(selected_index)

        # dezactivăm butoanele după alegere
        for btn in self.option_buttons:
            btn.configure(state="disabled")

        if self.mode == "train":
            # feedback imediat
            feedback_msg = "✔ Corect!\n\n" if is_correct else "✘ Greșit.\n\n"
            feedback_msg += f"Răspuns corect: {correct_text}"
            if explanation:
                feedback_msg += f"\nExplicație: {explanation}"
            messagebox.showinfo("Feedback", feedback_msg)

        # activăm butonul "Următoarea"
        self.next_button.configure(state="normal")


    def next_question(self):
        """Trece la următoarea întrebare."""
        more = self.quiz.advance()
        if more:
            self.show_question()
        else:
            self.finish_quiz()


    def finish_quiz(self):
        """Afișează scorul final."""
        total = self.quiz.total_questions()
        score = self.quiz.score
        percent = (score / total) * 100 if total > 0 else 0
        messagebox.showinfo("Quiz terminat 🎯", f"Scor final: {score}/{total} ({percent:.1f}%)")
        self.go_back()


    def go_back(self):
        """Revenire la meniu."""
        self.controller.show_frame("MainMenuFrame")


# ==============================================================
#                      RULARE APLICAȚIE
# ==============================================================

if __name__ == "__main__":
    app = FEAQuizApp()
    app.mainloop()
