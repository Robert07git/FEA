import tkinter as tk
from tkinter import messagebox
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

        self.questions = questions          # list[dict]
        self.mode = mode                    # "TRAIN" / "EXAM"
        self.time_limit = time_limit        # secunde per întrebare (EXAM)
        self.current = 0                    # index întrebare curentă
        self.score = 0                      # câte corecte
        self.running = True                 # timer running?
        self.timer_thread = None
        self.time_left = time_limit if time_limit else 0

        # variabile per întrebare
        self.selected_answer = tk.StringVar(value="")
        self.option_buttons = []

        # UI static
        self.create_widgets()

        # prima întrebare
        self.show_question()

    # ----------------------------------------------------------
    def create_widgets(self):
        tk.Label(
            self, text="FEA Quiz",
            font=("Segoe UI", 20, "bold"),
            bg="#111", fg="#00FFFF"
        ).pack(pady=10)

        # progres întrebări
        self.progress_label = tk.Label(
            self, text="Progres: 0%",
            font=("Segoe UI", 11, "bold"),
            bg="#111", fg="#00FFFF"
        )
        self.progress_label.pack(pady=5)

        self.progress_questions_frame = tk.Frame(
            self, bg="#222", width=400, height=10
        )
        self.progress_questions_frame.pack(pady=5)
        self.progress_questions_frame.pack_propagate(False)

        self.progress_questions_bar = tk.Frame(
            self.progress_questions_frame,
            bg="#00FFFF", width=0, height=10
        )
        self.progress_questions_bar.pack(side="left", fill="y")

        # nr întrebare
        self.label_qnum = tk.Label(
            self, text="",
            font=("Segoe UI", 12, "bold"),
            bg="#111", fg="white"
        )
        self.label_qnum.pack(pady=5)

        # text întrebare
        self.label_question = tk.Label(
            self, text="",
            wraplength=800, justify="center",
            font=("Segoe UI", 13),
            bg="#111", fg="white"
        )
        self.label_question.pack(pady=15)

        # container pentru opțiuni -> îl vom RECREA la fiecare întrebare
        self.options_parent = tk.Frame(self, bg="#111")
        self.options_parent.pack(pady=10)

        self.options_frame = None  # îl vom construi în show_question()

        # timer (EXAM)
        self.timer_label = tk.Label(
            self, text="",
            font=("Segoe UI", 12, "bold"),
            bg="#111", fg="#00FFFF"
        )
        self.timer_label.pack(pady=5)

        self.progress_frame = tk.Frame(
            self, bg="#222", width=400, height=20
        )
        self.progress_frame.pack(pady=5)
        self.progress_frame.pack_propagate(False)

        self.progress_bar = tk.Frame(
            self.progress_frame,
            bg="#00FFFF", width=0, height=20
        )
        self.progress_bar.pack(side="left", fill="y")

        # buton următoarea
        self.next_button = tk.Button(
            self,
            text="Următoarea ➜",
            command=self.next_question,
            bg="#00FFFF", fg="black",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=6
        )
        self.next_button.pack(pady=20)

    # ----------------------------------------------------------
    def build_options_ui(self, q):
        """recreează complet zona cu opțiuni pentru întrebarea q"""
        # ștergem orice frame vechi
        if self.options_frame is not None and self.options_frame.winfo_exists():
            self.options_frame.destroy()

        # recreăm frame-ul curat
        self.options_frame = tk.Frame(self.options_parent, bg="#111")
        self.options_frame.pack()

        # resetăm selecția pentru noua întrebare
        self.selected_answer = tk.StringVar(value="")
        self.option_buttons = []

        # construim radiobutton-urile
        for option in q["choices"]:
            rb = tk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_answer,
                value=option,
                bg="#111",
                fg="white",
                activebackground="#111",
                activeforeground="#00FFFF",
                indicatoron=True,
                selectcolor="#111",   # lasă background negru
                font=("Segoe UI", 11),
                anchor="w",
                justify="left",
                wraplength=700,
                command=lambda opt=option: self.highlight_selected(opt)
            )
            rb.pack(fill="x", padx=20, pady=4)
            self.option_buttons.append(rb)

        # mic hack vizual: după ce frame-ul e gata, forțăm o „curățare” de highlight
        def _reset_colors():
            for b in self.option_buttons:
                b.config(fg="white")
        self.after(10, _reset_colors)

    # ----------------------------------------------------------
    def show_question(self):
        """afișează întrebarea curentă"""

        if self.current >= len(self.questions):
            self.end_quiz()
            return

        q = self.questions[self.current]

        # progres întrebări
        total = len(self.questions)
        progress_percent = int((self.current / total) * 100)
        self.progress_label.config(text=f"Progres: {progress_percent}%")
        self.progress_questions_bar.config(
            width=int((self.current / total) * 400)
        )

        # setăm textele
        self.label_qnum.config(
            text=f"Întrebarea {self.current + 1}/{total}:"
        )
        self.label_question.config(text=q["question"])

        # reconstruim zona de opțiuni curată
        self.build_options_ui(q)

        # timer exam: reset pt fiecare întrebare
        if self.mode == "EXAM" and self.time_limit:
            self.time_left = self.time_limit

            # oprește timer vechi dacă există
            self.running = False
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join()

            self.running = True
            self.timer_thread = threading.Thread(
                target=self.countdown, daemon=True
            )
            self.timer_thread.start()
        else:
            self.timer_label.config(text="")
            self.progress_bar.config(width=0)

    # ----------------------------------------------------------
    def highlight_selected(self, selected_option):
        """colorează opțiunea aleasă în turcoaz"""
        for rb in self.option_buttons:
            if rb["text"] == selected_option:
                rb.config(fg="#00FFFF")
            else:
                rb.config(fg="white")

    # ----------------------------------------------------------
    def countdown(self):
        """timer pe întrebare pentru EXAM (+ sunet la 5 sec)"""
        while self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(
                text=f"Timp rămas: {mins:02d}:{secs:02d}",
                fg="#00FFFF"
            )

            bar_w = int((self.time_left / self.time_limit) * 400)
            self.progress_bar.config(width=bar_w)

            # avertizare sonoră la 5 secunde
            if self.time_left == 5:
                sound_path = os.path.join(
                    os.path.dirname(__file__), "alert.mp3"
                )
                if os.path.exists(sound_path):
                    try:
                        playsound(sound_path, block=False)
                    except Exception:
                        pass

            time.sleep(1)
            self.time_left -= 1

        # timp expirat pentru întrebarea curentă
        if self.running and self.time_left <= 0:
            self.timer_label.config(text="Timp expirat!", fg="cyan")
            self.progress_bar.config(width=0)
            # trecem automat mai departe după 1s
            self.after(1000, self.next_question)

    # ----------------------------------------------------------
    def next_question(self):
        """verifică răspunsul, dă feedback (TRAIN), avansează"""
        if not self.running:
            return
        self.running = False  # oprește timerul

        q = self.questions[self.current]
        user_ans = self.selected_answer.get()
        correct_ans = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "")

        if user_ans == correct_ans:
            self.score += 1
            if self.mode == "TRAIN":
                messagebox.showinfo(
                    "Corect ✅",
                    "Răspuns corect!\n\n" + explanation
                )
        else:
            if self.mode == "TRAIN":
                messagebox.showerror(
                    "Greșit ❌",
                    f"Răspuns greșit!\n"
                    f"Corect era: {correct_ans}\n\n{explanation}"
                )

        self.current += 1
        self.show_question()

    # ----------------------------------------------------------
    def end_quiz(self):
        """afișează rezultatele finale și salvează scorul în score_history.txt"""
        self.running = False

        for w in self.winfo_children():
            w.destroy()

        total_q = len(self.questions)
        pct = round((self.score / total_q) * 100.0, 2)

        tk.Label(
            self, text="Rezultate finale",
            font=("Segoe UI", 18, "bold"),
            bg="#111", fg="#00FFFF"
        ).pack(pady=20)

        rez_text = (
            f"Ai răspuns corect la {self.score} din {total_q} întrebări.\n"
            f"Scor final: {pct}%"
        )
        tk.Label(
            self, text=rez_text,
            font=("Segoe UI", 13),
            bg="#111", fg="white"
        ).pack(pady=15)

        tk.Button(
            self,
            text="Închide",
            command=self.destroy,
            bg="#00FFFF",
            fg="black",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=20,
            pady=6
        ).pack(pady=20)

        # scriem scorul în score_history.txt
        history_path = os.path.join(
            os.path.dirname(__file__), "score_history.txt"
        )
        try:
            dom = self.questions[0].get("domain", "?")
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(f"{dom},{self.mode},{total_q},{pct}\n")
        except Exception:
            pass
