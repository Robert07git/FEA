import json
import os
import random
from stats_manager import LeaderboardManager


# ==========================================================
#  🧠 QuizEngine — Original + integrare Leaderboard (FEA 6.0)
# ==========================================================

class QuizEngine:
    def __init__(self, ui, questions, mode, domain):
        """
        Inițializează motorul de quiz.
        ui: interfața principală (UI handler)
        questions: lista de întrebări încărcate din JSON
        mode: mod de rulare ("train" / "exam")
        domain: categoria de întrebări (ex: "structural", "crash" etc.)
        """
        self.ui = ui
        self.questions = questions
        self.mode = mode
        self.domain = domain
        self.current_question = 0
        self.score = 0
        self.total_questions = len(questions)
        self.time_left = 0
        self.timer_running = False
        self.correct_answers = 0
        self.wrong_answers = 0

    # ----------------------------------------------------------
    def start(self):
        """Pornește quiz-ul de la prima întrebare."""
        self.current_question = 0
        self.score = 0
        random.shuffle(self.questions)
        self.show_question()

    # ----------------------------------------------------------
    def show_question(self):
        """Afișează întrebarea curentă în UI."""
        if self.current_question >= self.total_questions:
            self.end_quiz()
            return
        question = self.questions[self.current_question]
        self.ui.display_question(
            question,
            self.current_question + 1,
            self.total_questions
        )

    # ----------------------------------------------------------
    def check_answer(self, selected):
        """Verifică răspunsul selectat și actualizează scorul."""
        question = self.questions[self.current_question]
        correct = question["answer"]

        if selected == correct:
            self.score += 1
            self.correct_answers += 1
            self.ui.display_feedback(True, question)
        else:
            self.wrong_answers += 1
            self.ui.display_feedback(False, question)

    # ----------------------------------------------------------
    def next_question(self):
        """Trece la următoarea întrebare."""
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.show_question()
        else:
            self.end_quiz()

    # ----------------------------------------------------------
    def end_quiz(self):
        """Finalizează quiz-ul și afișează rezultatele."""
        if self.total_questions == 0:
            percentage = 0
        else:
            percentage = (self.score / self.total_questions) * 100

        # Trimite scorul către UI pentru afișare finală
        self.ui.display_final_result(percentage)

        # ----------------------------------------------------------
        # 🏆 NOU: Salvare automată scor în Leaderboard Local
        # ----------------------------------------------------------
        try:
            # Citim numele utilizatorului din settings.json (dacă există)
            settings_path = os.path.join("data", "settings.json")
            user_name = "Anonim"
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    user_name = settings.get("user_name", "Anonim")

            # Inițializăm și salvăm scorul în leaderboard
            leaderboard = LeaderboardManager()
            leaderboard.add_score(
                name=user_name,
                mode=self.mode,
                domain=self.domain,
                score=percentage
            )

        except Exception as e:
            print(f"[WARN] Eroare la salvarea scorului în Leaderboard: {e}")

        # Poate fi extins ulterior pentru leaderboard global
