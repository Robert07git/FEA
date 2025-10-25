import tkinter as tk
import threading
import time
import os
from playsound import playsound


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
        self.running = False
        self.timer_thread = None
        self.time_left = 0
        self.selected_answer = tk.StringVar(value="")
        self.option_buttons = []

        self.create_widgets()
        self.show_question()

    # ----------------------------------------------------------
    def create_widgets(self):
        tk.Label(self, text="FEA Quiz",
                 font=("Segoe UI", 20, "bold"),
                 bg="#111", fg="#00FFFF").pack(pady=10)

        self.progress_label = tk.Label(self, text="Progres: 0%",
                                       font=("Segoe UI", 11, "bold"),
                                       bg="#111", fg="#00FFFF")
        self.progress_label.pack(pady=5)

        self.progress_questions_frame = tk.Frame(self, bg="#222", width=400, height=10)
        self.progress_questions_frame.pack(pady=5)
        self.progress_questions_frame.pack_propagate(False)
        self.progress_questions_bar = tk.Frame(self.progress_questions_frame, bg="#00FFFF", width=0, height=10)
        self.progress_questions_bar.pack(side="left", fill="y")

        self.label_qnum = tk.Label(self, text="", font=("Segoe UI", 12, "bold"),
                                   bg="#111", fg="white")
        self.label_qnum.pack(pady=5)

        self.label_question = tk.Label(self, text="", wraplength=800, justify="center",
                                       font=("Segoe UI", 13), bg="#111", fg="white")
        self.label_question.pack(pady=15)

        self.options_parent = tk.Frame(self, bg="#111")
        self.options_parent.pack(pady=10)
        self.options_frame = None

        self.feedback_label = tk.Label(self, text="", wraplength=750,
                                       font=("Segoe UI", 11, "italic"),
                                       bg="#111", fg="#AAAAAA", justify="center")
        self.feedback_label.pack(pady=10)

        self.timer_label = tk.Label(self, text="", font=("Segoe UI", 12, "bold"),
                                    bg="#111", fg="#00FFFF")
        self.timer_label.pack(pady=5)

        self.progress_frame = tk.Frame(self, bg="#222", width=400, height=20)
        self.progress_frame.pack(pady=5)
        self.progress_frame.pack_propagate(False)
        self.progress_bar = tk.Frame(self.progress_frame, bg="#00FFFF", width=0, height=20)
        self.progress_bar.pack(side="left", fill="y")

        self.next_button = tk.Button(self, text="Următoarea ➜",
                                     command=self.next_question,
                                     bg="#00FFFF", fg="black",
                                     font=("Segoe UI", 12, "bold"),
                                     relief="flat", padx=20, pady=6)
        self.next_button.pack(pady=20)

    # ----------------------------------------------------------
    def build_options_ui(self, q):
        if self.options_frame is not None and self.options_frame.winfo_exists():
            self.options_frame.destroy()

        self.options_frame = tk.Frame(self.options_parent, bg="#111")
        self.options_frame.pack()

        self.selected_answer = tk.StringVar(value="")
        self.option_buttons = []

        for option in q["choices"]:
            rb = tk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_answer,
                value=option,
                bg="#111", fg="white",
                activebackground="#111",
                activeforeground="#00FFFF",
                selectcolor="#111",
                font=("Segoe UI", 11),
                anchor="w", justify="left", wraplength=700,
                command=lambda opt=option: self.highlight_selected(opt)
            )
            rb.pack(fill="x", padx=20, pady=4)
            self.option_buttons.append(rb)

        # reset culori după creare
        self.after(10, lambda: [b.config(fg="white") for b in self.option_buttons])

    # ----------------------------------------------------------
    def show_question(self):
        if self.current >= len(self.questions):
            self.end_quiz()
            return

        # Oprire timer anterior dacă există
        self.running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=0.2)

        q = self.questions[self.current]
        total = len(self.questions)
        self.feedback_label.config(text="")
        self.progress_label.config(text=f"Progres: {int((self.current / total) * 100)}%")
        self.progress_questions_bar.config(width=int((self.current / total) * 400))
        self.label_qnum.config(text=f"Întrebarea {self.current + 1}/{total}:")
        self.label_question.config(text=q["question"])
        self.build_options_ui(q)

        if self.mode == "EXAM" and self.time_limit:
            self.time_left = self.time_limit
            self.running = True
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()
            self.update_timer_display()
        else:
            self.timer_label.config(text="")
            self.progress_bar.config(width=0)

    # ----------------------------------------------------------
    def highlight_selected(self, selected_option):
        for rb in self.option_buttons:
            rb.config(fg="#00FFFF" if rb["text"] == selected_option else "white")

    # ----------------------------------------------------------
    def countdown(self):
        """Rulează o singură dată per întrebare (thread separat)"""
        while self.running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
            self.update_timer_display()

            # avertizare sonoră la 5 secunde
            if self.time_left == 5:
                path = os.path.join(os.path.dirname(__file__), "alert.mp3")
                if os.path.exists(path):
                    try:
                        playsound(path, block=False)
                    except:
                        pass

        # când timpul s-a terminat
        if self.running and self.time_left <= 0:
            self.running = False
            self.after(0, lambda: self.timer_label.config(text="Timp expirat!", fg="#FF5555"))
            # adaugă o pauză vizuală de 1 sec înainte de întrebarea următoare
            self.after(1000, self.next_question)

    # ----------------------------------------------------------
    def update_timer_display(self):
        """actualizează bara și label-ul fără să repornească threadul"""
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}", fg="#00FFFF")
        if self.time_limit:
            width = int((self.time_left / self.time_limit) * 400)
            self.progress_bar.config(width=max(width, 0))

    # ----------------------------------------------------------
    def next_question(self):
        # Oprire timer curent dacă s-a apăsat manual pe "Următoarea"
        self.running = False

        q = self.questions[self.current]
        user_ans = self.selected_answer.get()
        correct_ans = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "")

        for rb in self.option_buttons:
            rb.config(fg="white")

        if user_ans == correct_ans:
            self.score += 1
            self.feedback_label.config(
                text=f"✅ Corect!\n{explanation}",
                fg="#00FFFF"
            )
        else:
            self.feedback_label.config(
                text=f"❌ Răspuns greșit!\nCorect era: {correct_ans}\n\n{explanation}",
                fg="#FF5555"
            )

        self.current += 1

        if self.mode == "TRAIN":
            # feedback + trece automat după 2.5s
            self.after(2500, self.show_question)
        elif self.mode == "EXAM":
            # trece la următoarea întrebare (după feedback 1s, dacă e manual)
            self.after(1000, self.show_question)

    # ----------------------------------------------------------
    def end_quiz(self):
        self.running = False
        for w in self.winfo_children():
            w.destroy()

        total = len(self.questions)
        pct = round((self.score / total) * 100, 2)
        tk.Label(self, text="Rezultate finale",
                 font=("Segoe UI", 18, "bold"),
                 bg="#111", fg="#00FFFF").pack(pady=20)
        tk.Label(self, text=f"{self.score} din {total} întrebări corecte\nScor final: {pct}%",
                 font=("Segoe UI", 13),
                 bg="#111", fg="white").pack(pady=10)
        tk.Button(self, text="Închide", command=self.destroy,
                  bg="#00FFFF", fg="black",
                  font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=20, pady=6).pack(pady=20)

        # scriem scorul în score_history.txt
        path = os.path.join(os.path.dirname(__file__), "score_history.txt")
        try:
            dom = self.questions[0].get("domain", "?")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"{dom},{self.mode},{total},{pct}\n")
        except:
            pass
