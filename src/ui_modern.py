# =============================================================
#  FEA Quiz Trainer — ui_modern.py (Moment 0 + Leaderboard Local)
#  Versiune: 6.0 Evolution Edition
#  Data: 2025-10-26
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from stats_manager import LeaderboardManager


class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FEA Quiz Trainer 6.0 — Evolution Edition")
        self.root.geometry("1200x720")
        self.root.configure(bg="#1e1e1e")

        # Sidebar principal
        self.sidebar = tk.Frame(self.root, bg="#222", width=220)
        self.sidebar.pack(side="left", fill="y")

        # Zona principală
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(side="right", expand=True, fill="both")

        # Construim bara laterală
        self.add_sidebar_buttons()

        # Starea aplicației
        self.current_mode = None
        self.quiz_engine = None
        self.active_question = None

    # =============================================================
    # 🧩 Funcții generale
    # =============================================================

    def clear_main_frame(self):
        """Șterge toate elementele din fereastra principală."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def add_sidebar_buttons(self):
        """Adaugă butoanele în bara laterală."""
        buttons = [
            ("📘 LEARN MODE", self.show_learn),
            ("🏋️ TRAIN MODE", self.show_train),
            ("🧠 EXAM MODE", self.show_exam),
            ("📊 STATISTICI", self.show_stats),
            ("📄 EXPORTĂ PDF", self.export_pdf),
            ("🏆 LEADERBOARD LOCAL", self.show_leaderboard)
        ]
        for text, cmd in buttons:
            b = tk.Button(self.sidebar, text=text, command=cmd,
                          font=("Segoe UI", 10, "bold"),
                          bg="#0a57d1", fg="white",
                          relief="flat", padx=10, pady=10, cursor="hand2")
            b.pack(fill="x", pady=4, padx=8)

        # Buton de ieșire
        tk.Button(self.sidebar, text="❌ Ieșire", command=self.root.quit,
                  bg="red", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2").pack(fill="x", pady=8, padx=8, side="bottom")

    # =============================================================
    # 📘 LEARN MODE
    # =============================================================

    def show_learn(self):
        self.clear_main_frame()

        title = tk.Label(self.main_frame, text="📘 LEARN MODE",
                         font=("Segoe UI", 18, "bold"),
                         fg="#00ffff", bg="#1e1e1e")
        title.pack(pady=20)

        info = tk.Label(self.main_frame,
                        text="În acest mod poți învăța conceptele FEA prin întrebări și explicații detaliate.",
                        wraplength=800, justify="center",
                        fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        info.pack(pady=10)

        tk.Button(self.main_frame, text="Începe sesiunea de învățare",
                  bg="#0a57d1", fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2").pack(pady=30)

    # =============================================================
    # 🏋️ TRAIN MODE
    # =============================================================

    def show_train(self):
        self.clear_main_frame()

        title = tk.Label(self.main_frame, text="🏋️ TRAIN MODE",
                         font=("Segoe UI", 18, "bold"),
                         fg="#00ffff", bg="#1e1e1e")
        title.pack(pady=20)

        info = tk.Label(self.main_frame,
                        text="Alege un set de întrebări pentru antrenament.",
                        fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        info.pack(pady=10)

        tk.Button(self.main_frame, text="Start Training",
                  bg="#0a57d1", fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2").pack(pady=30)

    # =============================================================
    # 🧠 EXAM MODE
    # =============================================================

    def show_exam(self):
        self.clear_main_frame()

        title = tk.Label(self.main_frame, text="🧠 EXAM MODE",
                         font=("Segoe UI", 18, "bold"),
                         fg="#00ffff", bg="#1e1e1e")
        title.pack(pady=20)

        info = tk.Label(self.main_frame,
                        text="Completează un test complet FEA pentru evaluare finală.",
                        fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        info.pack(pady=10)

        tk.Button(self.main_frame, text="Începe examenul",
                  bg="#0a57d1", fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2").pack(pady=30)

    # =============================================================
    # 📊 STATISTICI
    # =============================================================

    def show_stats(self):
        self.clear_main_frame()

        title = tk.Label(self.main_frame, text="📊 STATISTICI",
                         font=("Segoe UI", 18, "bold"),
                         fg="#00ffff", bg="#1e1e1e")
        title.pack(pady=20)

        stats_info = tk.Label(self.main_frame,
                              text="Aici se vor afișa performanțele tale, progresul și scorurile medii.",
                              fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        stats_info.pack(pady=10)

        tk.Label(self.main_frame, text="(Această secțiune va include grafice și scoruri medii.)",
                 font=("Segoe UI", 10, "italic"),
                 fg="#888", bg="#1e1e1e").pack(pady=10)

    # =============================================================
    # 📄 EXPORT PDF
    # =============================================================

    def export_pdf(self):
        self.clear_main_frame()

        title = tk.Label(self.main_frame, text="📄 EXPORTĂ PDF DIN NOU",
                         font=("Segoe UI", 18, "bold"),
                         fg="#00ffff", bg="#1e1e1e")
        title.pack(pady=20)

        info = tk.Label(self.main_frame,
                        text="Această funcție generează din nou un raport PDF cu rezultatele anterioare.",
                        fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
        info.pack(pady=10)

        tk.Button(self.main_frame, text="Generează PDF",
                  bg="#0a57d1", fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2").pack(pady=30)

    # =============================================================
    # 🏁 REZULTATE / FEEDBACK FINAL
    # =============================================================

    def display_final_result(self, percentage):
        self.clear_main_frame()

        msg = f"Scor final: {percentage:.1f}%"
        color = "#00ff00" if percentage >= 70 else "#ff3333"

        tk.Label(self.main_frame, text=msg,
                 font=("Segoe UI", 18, "bold"),
                 fg=color, bg="#1e1e1e").pack(pady=40)

        tk.Label(self.main_frame, text="(Scorul tău a fost adăugat în Leaderboard 🏆)",
                 font=("Segoe UI", 10, "italic"),
                 fg="#00ffff", bg="#1e1e1e").pack(pady=10)

        tk.Button(self.main_frame, text="Înapoi la meniu",
                  command=self.clear_main_frame,
                  bg="#444", fg="white",
                  font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2").pack(pady=30)
    # =============================================================
    # 🏆 LEADERBOARD LOCAL — NOU (FEA Trainer 6.0)
    # =============================================================
    def show_leaderboard(self):
        """Afișează leaderboard-ul local (Top 10 scoruri salvate)."""
        self.clear_main_frame()

        title = tk.Label(
            self.main_frame,
            text="🏆 LEADERBOARD LOCAL",
            font=("Segoe UI", 18, "bold"),
            fg="#00ffff",
            bg="#1e1e1e"
        )
        title.pack(pady=20)

        leaderboard = LeaderboardManager()
        scores = leaderboard.get_top_scores()

        if not scores:
            tk.Label(
                self.main_frame,
                text="Nu există scoruri salvate momentan.",
                font=("Segoe UI", 12),
                fg="white",
                bg="#1e1e1e"
            ).pack(pady=30)
            return

        # 🏅 Afișare scoruri top 10
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # aur, argint, bronz
        header = tk.Label(
            self.main_frame,
            text=f"{'Nr.':<5}{'Nume':<20}{'Domeniu':<15}{'Mod':<10}{'Scor (%)':<10}{'Data':<15}",
            font=("Consolas", 11, "bold"),
            fg="#00ffff",
            bg="#1e1e1e",
            justify="left"
        )
        header.pack(pady=5)

        for i, entry in enumerate(scores, start=1):
            color = colors[i - 1] if i <= 3 else "#00ffff"
            text = f"{i:<5}{entry['name']:<20}{entry['domain']:<15}{entry['mode']:<10}{entry['score']:<10}{entry['date']:<15}"
            tk.Label(
                self.main_frame,
                text=text,
                font=("Consolas", 10),
                fg=color,
                bg="#1e1e1e",
                justify="left"
            ).pack(anchor="w", padx=40)

        # Linie separatoare
        tk.Label(self.main_frame, text="─" * 80, bg="#1e1e1e", fg="#444").pack(pady=15)

        # Buton de ștergere leaderboard
        def clear_lb():
            confirm = messagebox.askyesno("Confirmare", "Sigur vrei să ștergi toate scorurile?")
            if confirm:
                leaderboard.clear_leaderboard()
                self.show_leaderboard()

        tk.Button(
            self.main_frame,
            text="🗑 Șterge toate scorurile",
            command=clear_lb,
            bg="#444",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(pady=20)

        # Înapoi la meniu
        tk.Button(
            self.main_frame,
            text="⬅ Înapoi la meniu",
            command=self.clear_main_frame,
            bg="#0a57d1",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(pady=10)

    # =============================================================
    # 🔧 Helperi adiționali (design, actualizări, refresh)
    # =============================================================

    def refresh_ui(self):
        """Reîmprospătează complet UI-ul principal."""
        self.clear_main_frame()
        self.add_sidebar_buttons()

    def show_message(self, text, color="#00ffff"):
        """Mesaj rapid în partea centrală."""
        self.clear_main_frame()
        tk.Label(self.main_frame, text=text, fg=color, bg="#1e1e1e",
                 font=("Segoe UI", 14, "bold")).pack(pady=30)

    def display_question(self, question, index, total):
        """Simulare placeholder pentru afișarea unei întrebări."""
        self.clear_main_frame()
        tk.Label(self.main_frame,
                 text=f"Întrebarea {index}/{total}",
                 fg="#00ffff", bg="#1e1e1e",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(self.main_frame,
                 text=question["question"],
                 fg="white", bg="#1e1e1e",
                 font=("Segoe UI", 12),
                 wraplength=800, justify="center").pack(pady=20)
        for option in question["options"]:
            tk.Button(self.main_frame, text=option,
                      bg="#333", fg="white",
                      font=("Segoe UI", 11),
                      relief="flat", cursor="hand2",
                      command=lambda opt=option: self.check_answer(opt)).pack(pady=5)

    def display_feedback(self, correct, question):
        """Feedback vizual pentru răspuns."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        if correct:
            msg = "✔ Răspuns corect!"
            color = "#00ff00"
        else:
            msg = f"✘ Răspuns greșit! Răspunsul corect era: {question['answer']}"
            color = "#ff3333"
        tk.Label(self.main_frame, text=msg,
                 fg=color, bg="#1e1e1e",
                 font=("Segoe UI", 14, "bold")).pack(pady=30)
        tk.Button(self.main_frame, text="Următoarea întrebare",
                  bg="#0a57d1", fg="white",
                  font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2",
                  command=self.next_question_placeholder).pack(pady=15)

    def next_question_placeholder(self):
        """Placeholder pentru logica de următoare întrebare (legată de quiz_engine)."""
        self.show_message("Următoarea întrebare (simulare).")

# =============================================================
#  🏁 MAIN APP ENTRY
# =============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = MainUI(root)
    root.mainloop()
