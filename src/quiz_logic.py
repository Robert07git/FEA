import tkinter as tk
from tkinter import messagebox
import threading
import time
from playsound import playsound
import os


class QuizWindow(tk.Toplevel):
    def __init__(self, master, questions, mode, time_limit=None):
        super().__init__(master)
        self.title("FEA Quiz Session")
        self.geometry("900x600")
        self.configure(bg="#111")

        self.questions = questions
        self.mode = mode
        self.time_limit = time_limit
        self.current = 0
        self.score = 0
        self.selected_answer = tk.StringVar(value="")
        self.running = True
        self.timer_thread = None
        self.time_left = time_limit if time_limit else 0

        self.create_widgets()
        self.show_question()

    # ------------------------------------------------------------

    def create_widgets(self):
        """Creează interfața principală"""

        tk.Label(
            self, text="FEA Quiz", font=("Segoe UI", 20, "bold"),
            bg="#111", fg="#00FFFF"
        ).pack(pady=10)

        # Bara progres întrebări
        self.progress_label = tk.Label(
            self, text="Progres: 0%", font=("Segoe UI", 11, "bold"),
            bg="#111", fg="#00FFFF"
        )
        self.progress_label.pack(pady=5)

        self.progress_questions_frame = tk.Frame(self, bg="#222", width=400, height=10)
        self.progress_questions_frame.pack(pady=5)
        self.progress_questions_frame.pack_propagate(False)
        self.progress_questions_bar = tk.Frame(
            self.progress_questions_frame, bg="#00FFFF", width=0, height=10
        )
        self.progress_questions_bar.pack(side="left", fill="y")

        self.label_qnum = tk.Label(
            self, text="", font=("Segoe UI", 12, "bold"),
            bg="#111", fg="white"
        )
        self.label_qnum.pack(pady=5)

        self.label_question = tk.Label(
            self, text="", wraplength=800, justify="center",
            font=("Segoe UI", 13), bg="#111", fg="white"
        )
        self.label_question.pack(pady=15)

        self.options_frame = tk.Frame(self, bg="#111")
        self.options_frame.pack(pady=10)

        # Timer + bară progres timp
        self.timer_label = tk.Label(
            self, text="", font=("Segoe UI", 12, "bold"),
            bg="#111", fg="#00FFFF"
        )
        self.timer_label.pack(pady=5)

        self.progress_frame = tk.Frame(self, bg="#222", width=400, height=20)
        self.progress_frame.pack(pady=5)
        self.progress_frame.pack_propagate(False)
        self.progress_bar = tk.Frame(self.progress_frame, bg="#00FFFF", width=400, height=20)
        self.progress_bar.pack(side="left", fill="y")

        self.next_button = tk.Button(
            self, text="Următoarea ➜", command=self.next_question,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=6
        )
        self.next_button.pack(pady=20)

    # ------------------------------------------------------------

    def show_question(self):
        """Afișează întrebarea curentă"""
        if self.current >= len(self.questions):
            self.end_quiz()
            return

        q = self.questions[self.current]

        # Reset răspuns curent + refresh vizual
        self.selected_answer.set("")
        self.update_idletasks()

        # Actualizare progres întrebări
        total = len(self.questions)
        progress_percent = int(((self.current) / total) * 100)
        self.progress_label.config(text=f"Progres: {progress_percent}%")
        self.progress_questions_bar.config(width=int((self.current / total) * 400))

        self.label_qnum.config(
            text=f"Întrebarea {self.current + 1}/{len(self.questions)}:"
        )
        self.label_question.config(text=q["question"])

        # Curățăm opțiunile vechi
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Adăugăm opțiuni radio
        for i, option in enumerate(q["choices"]):
            rb = tk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_answer,
                value=option,
                bg="#111", fg="white",
                activebackground="#111", activeforeground="#00FFFF",
                indicatoron=True,
                selectcolor="#111",
                font=("Segoe UI", 11),
                anchor="w", justify="left", wraplength=700
            )
            rb.pack(fill="x", padx=20, pady=4)

        # Resetăm timerul pentru fiecare întrebare în EXAM
        if self.mode == "EXAM" and self.time_limit:
            self.time_left = self.time_limit
            if self.timer_thread and self.timer_thread.is_alive():
                self.running = False
                self.timer_thread.join()
            self.running = True
            self.timer_thread = threading.Thread(target=self.countdown)
            self.timer_thread.daemon = True
            self.timer_thread.start()
        else:
            self.timer_label.config(text="")
            self.progress_bar.config(width=0)

    # ------------------------------------------------------------

    def countdown(self):
        """Cronometru + bară progresivă"""
        while self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}")

            # Bara de progres timp
            bar_width = int((self.time_left / self.time_limit) * 400)
            self.progress_bar.config(width=bar_width)

            time.sleep(1)
            self.time_left -= 1

            # avertizare audio la 5 secunde
            if self.time_left == 5:
                sound_path = os.path.join(os.path.dirname(__file__), "alert.mp3")
                if os.path.exists(sound_path):
                    try:
                        playsound(sound_path, block=False)
                    except Exception:
                        pass

        if self.running and self.time_left <= 0:
            self.timer_label.config(text="Timp expirat!", fg="cyan")
            self.progress_bar.config(width=0)
            self.after(1000, self.next_question)

    # ------------------------------------------------------------

    def next_question(self):
        """Verifică răspunsul și trece la următoarea întrebare"""
        if not self.running:
            return
        self.running = False  # oprim timerul curent

        q = self.questions[self.current]
        ans = self.selected_answer.get()

        correct_answer = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "")

        if ans == correct_answer:
            self.score += 1
            if self.mode == "TRAIN":
                messagebox.showinfo("Corect ✅", "Răspuns corect!\n\n" + explanation)
        else:
            if self.mode == "TRAIN":
                messagebox.showerror("Greșit ❌", f"Răspuns greșit!\nCorect era: {correct_answer}\n\n{explanation}")

        self.current += 1
        self.show_question()

    # ------------------------------------------------------------

    def end_quiz(self):
        """Afișează rezultatul final"""
        self.running = False
        for widget in self.winfo_children():
            widget.destroy()

        # actualizare progres final complet
        self.progress_questions_bar.config(width=400)
        self.progress_label.config(text="Progres: 100%")

        score_percent = round((self.score / len(self.questions)) * 100, 2)
        tk.Label(
            self, text=f"Rezultate finale", font=("Segoe UI", 18, "bold"),
            bg="#111", fg="#00FFFF"
        ).pack(pady=20)
        tk.Label(
            self,
            text=f"Ai răspuns corect la {self.score} din {len(self.questions)} întrebări.\nScor final: {score_percent}%",
            font=("Segoe UI", 13), bg="#111", fg="white"
        ).pack(pady=15)

        tk.Button(
            self, text="Închide", command=self.destroy,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=6
        ).pack(pady=20)

        # Salvăm scorul în istoric
        history_file = os.path.join(os.path.dirname(__file__), "score_history.txt")
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(f"{self.questions[0]['domain']},{self.mode},{len(self.questions)},{score_percent}\n")
