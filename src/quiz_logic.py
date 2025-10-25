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

        self.questions = questions          # lista de întrebări selectate
        self.mode = mode                    # "TRAIN" sau "EXAM"
        self.time_limit = time_limit        # secunde per întrebare (doar EXAM)
        self.current = 0                    # index întrebare curentă
        self.score = 0                      # câte corecte
        self.running = True                 # control pentru timer thread
        self.timer_thread = None            # threadul de timer curent
        self.time_left = time_limit if time_limit else 0
        self.selected_answer = tk.StringVar(value="")  # răspuns ales la întrebarea curentă
        self.option_buttons = []            # referințe la butoanele radio pt highlight vizual

        self.create_widgets()
        self.show_question()

    # ----------------------------------------------------------
    def create_widgets(self):
        """Construiește UI-ul principal (static)"""

        # Titlu aplicație
        tk.Label(
            self, text="FEA Quiz", font=("Segoe UI", 20, "bold"),
            bg="#111", fg="#00FFFF"
        ).pack(pady=10)

        # Progres întrebări (text + bară mică)
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

        # Label cu numărul întrebării curente
        self.label_qnum = tk.Label(
            self, text="", font=("Segoe UI", 12, "bold"),
            bg="#111", fg="white"
        )
        self.label_qnum.pack(pady=5)

        # Textul întrebării
        self.label_question = tk.Label(
            self, text="", wraplength=800, justify="center",
            font=("Segoe UI", 13), bg="#111", fg="white"
        )
        self.label_question.pack(pady=15)

        # Zonă pentru opțiunile de răspuns
        self.options_frame = tk.Frame(self, bg="#111")
        self.options_frame.pack(pady=10)

        # Timer + bară progres timp (doar EXAM)
        self.timer_label = tk.Label(
            self, text="", font=("Segoe UI", 12, "bold"),
            bg="#111", fg="#00FFFF"
        )
        self.timer_label.pack(pady=5)

        self.progress_frame = tk.Frame(self, bg="#222", width=400, height=20)
        self.progress_frame.pack(pady=5)
        self.progress_frame.pack_propagate(False)

        self.progress_bar = tk.Frame(
            self.progress_frame, bg="#00FFFF", width=0, height=20
        )
        self.progress_bar.pack(side="left", fill="y")

        # Buton "Următoarea"
        self.next_button = tk.Button(
            self, text="Următoarea ➜", command=self.next_question,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=6
        )
        self.next_button.pack(pady=20)

    # ----------------------------------------------------------
    def show_question(self):
        """Afișează întrebarea curentă și pregătește selecția utilizatorului"""
        if self.current >= len(self.questions):
            self.end_quiz()
            return

        q = self.questions[self.current]

        # --- curățăm opțiunile vechi complet ---
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.update_idletasks()  # forțează refresh UI ca să nu rămână selecția vizuală veche

        # --- recreăm variabila de selecție pt întrebarea asta ---
        self.selected_answer = tk.StringVar(value="")
        self.option_buttons = []

        # --- progres întrebări ---
        total = len(self.questions)
        progress_percent = int((self.current / total) * 100)
        self.progress_label.config(text=f"Progres: {progress_percent}%")
        self.progress_questions_bar.config(width=int((self.current / total) * 400))

        # --- setăm textele întrebării curente ---
        self.label_qnum.config(
            text=f"Întrebarea {self.current + 1}/{len(self.questions)}:"
        )
        self.label_question.config(text=q["question"])

        # --- generăm opțiunile de răspuns (radiobutton) ---
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
                indicatoron=True,        # cerc clasic radio
                selectcolor="#111",      # păstrează background-ul dark
                font=("Segoe UI", 11),
                anchor="w",
                justify="left",
                wraplength=700,
                command=lambda opt=option: self.highlight_selected(opt)
            )
            rb.pack(fill="x", padx=20, pady=4)
            self.option_buttons.append(rb)

        # --- pornim / resetăm timerul pentru modul EXAM ---
        if self.mode == "EXAM" and self.time_limit:
            # resetăm timpul pentru întrebarea asta
            self.time_left = self.time_limit

            # dacă există deja un thread de timer care rulează, îl oprim în siguranță
            self.running = False
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join()

            # marcăm că timerul curent e activ
            self.running = True
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()
        else:
            # în TRAIN nu afișăm timer deloc
            self.timer_label.config(text="")
            self.progress_bar.config(width=0)

    # ----------------------------------------------------------
    def highlight_selected(self, selected_option):
        """Schimbă culoarea textului pentru opțiunea selectată"""
        for rb in self.option_buttons:
            if rb["text"] == selected_option:
                rb.config(fg="#00FFFF")  # turcoaz pentru varianta aleasă
            else:
                rb.config(fg="white")    # alb pentru restul

    # ----------------------------------------------------------
    def countdown(self):
        """Cronometru pe întrebare (doar EXAM) + bară de progres timp + sunet la 5s"""
        while self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"Timp rămas: {mins:02d}:{secs:02d}")

            # actualizăm bara de progres timp (scade de la 400px spre 0px)
            bar_width = int((self.time_left / self.time_limit) * 400)
            self.progress_bar.config(width=bar_width)

            time.sleep(1)
            self.time_left -= 1

            # sunet de avertizare la 5 secunde rămase
            if self.time_left == 5:
                sound_path = os.path.join(os.path.dirname(__file__), "alert.mp3")
                if os.path.exists(sound_path):
                    try:
                        playsound(sound_path, block=False)
                    except Exception:
                        # dacă sunetul dă eroare (codecul etc), nu blocăm aplicația
                        pass

        # dacă s-a terminat timpul pe întrebare
        if self.running and self.time_left <= 0:
            self.timer_label.config(text="Timp expirat!", fg="cyan")
            self.progress_bar.config(width=0)

            # după 1 secundă, trecem automat la următoarea întrebare
            self.after(1000, self.next_question)

    # ----------------------------------------------------------
    def next_question(self):
        """Verifică răspunsul curent, dă feedback (dacă TRAIN) și avansează"""
        if not self.running:
            return
        self.running = False  # oprește timerul pentru întrebarea curentă

        q = self.questions[self.current]
        user_ans = self.selected_answer.get()
        correct_ans = q["choices"][q["correct_index"]]
        explanation = q.get("explanation", "")

        # scor + feedback
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
                    f"Răspuns greșit!\nCorect era: {correct_ans}\n\n{explanation}"
                )

        # trecem la următoarea întrebare
        self.current += 1
        self.show_question()

    # ----------------------------------------------------------
    def end_quiz(self):
        """Afișează rezultatele finale și salvează scorul în istoric"""
        self.running = False  # oprește timerul definitiv

        # curățăm UI-ul complet
        for widget in self.winfo_children():
            widget.destroy()

        # calculăm scor
        total_q = len(self.questions)
        score_percent = round((self.score / total_q) * 100, 2)

        # UI cu rezultatul final
        tk.Label(
            self, text="Rezultate finale", font=("Segoe UI", 18, "bold"),
            bg="#111", fg="#00FFFF"
        ).pack(pady=20)

        tk.Label(
            self,
            text=f"Ai răspuns corect la {self.score} din {total_q} întrebări.\n"
                 f"Scor final: {score_percent}%",
            font=("Segoe UI", 13), bg="#111", fg="white"
        ).pack(pady=15)

        tk.Button(
            self, text="Închide", command=self.destroy,
            bg="#00FFFF", fg="black", font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=6
        ).pack(pady=20)

        # salvăm scorul într-un fișier local
        history_file = os.path.join(os.path.dirname(__file__), "score_history.txt")
        try:
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(f"{self.questions[0].get('domain','?')},"
                        f"{self.mode},"
                        f"{total_q},"
                        f"{score_percent}\n")
        except Exception:
            # dacă nu putem salva scorul nu blocăm aplicația
            pass
