import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
from quiz_core import load_questions
import random


class QuizWindow(tk.Toplevel):
    def __init__(self, master, domeniu, mode, num_questions, time_per_q):
        super().__init__(master)
        self.title("FEA Quiz - Sesiune Quiz")
        self.geometry("520x580")
        self.configure(bg="#0d0d0d")
        self.resizable(False, False)

        self.domeniu = domeniu
        self.mode = mode
        self.num_questions = num_questions
        self.time_per_q = time_per_q
        self.questions = random.sample(load_questions(domeniu), num_questions)
        self.current_index = 0
        self.correct_count = 0
        self.asked_count = 0
        self.timer_thread = None
        self.timer_running = False
        self.time_left = self.time_per_q
        self.gresite = []

        # Titlu domeniu + mod
        self.lbl_title = tk.Label(
            self,
            text=f"Domeniu: {domeniu} | Mod: {mode.upper()}",
            bg="#0d0d0d",
            fg="#00bfff",
            font=("Segoe UI", 11, "bold")
        )
        self.lbl_title.pack(pady=10)

        # Numărul întrebării curente
        self.lbl_qcount = tk.Label(
            self, text="", bg="#0d0d0d", fg="white", font=("Segoe UI", 10)
        )
        self.lbl_qcount.pack(pady=(0, 5))

        # Text întrebare
        self.lbl_question = tk.Label(
            self,
            text="",
            wraplength=470,
            justify="left",
            bg="#0d0d0d",
            fg="white",
            font=("Segoe UI", 10)
        )
        self.lbl_question.pack(pady=10)

        # Opțiuni (radiobuttons)
        self.answer_var = tk.IntVar()
        self.options = []
        for i in range(4):
            rb = tk.Radiobutton(
                self,
                text="",
                variable=self.answer_var,
                value=i,
                bg="#0d0d0d",
                fg="white",
                font=("Segoe UI", 9),
                anchor="w",
                selectcolor="#1a1a1a",
                activebackground="#0d0d0d",
                activeforeground="#00bfff"
            )
            rb.pack(fill="x", padx=40, pady=3)
            self.options.append(rb)

        # Feedback label
        self.lbl_feedback = tk.Label(
            self,
            text="",
            wraplength=470,
            justify="left",
            bg="#0d0d0d",
            fg="#00ffcc",
            font=("Segoe UI", 9, "italic")
        )
        self.lbl_feedback.pack(pady=(8, 10))

        # Buton principal
        self.btn_next = tk.Button(
            self,
            text="Răspunde / Finalizează",
            command=self.submit_and_advance,
            bg="#00bfff",
            fg="black",
            font=("Segoe UI", 10, "bold"),
            activebackground="#00e6e6",
            activeforeground="black",
            relief="flat",
            width=30
        )
        self.btn_next.pack(pady=10)

        # Timer (EXAM)
        self.lbl_timer = tk.Label(
            self,
            text="",
            bg="#0d0d0d",
            fg="#ff6666",
            font=("Consolas", 10, "bold")
        )
        self.lbl_timer.pack(pady=(5, 5))

        # Buton închidere
        self.btn_close = tk.Button(
            self,
            text="Închide",
            command=self.destroy,
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            width=10
        )
        self.btn_close.pack(pady=(5, 10))

        # Pornim prima întrebare
        self.show_current_question(start_new=True)

    # ===============================
    # LOGICA PRINCIPALĂ QUIZ
    # ===============================
    def show_current_question(self, start_new=False):
        if self.current_index >= len(self.questions):
            self.end_quiz()
            return

        qdata = self.questions[self.current_index]
        self.lbl_qcount.config(
            text=f"Întrebarea {self.current_index + 1}/{self.num_questions}"
        )
        self.lbl_question.config(text=qdata["question"])
        self.answer_var.set(-1)

        for i, opt in enumerate(qdata["choices"]):
            self.options[i].config(text=f"{i + 1}. {opt}")

        self.lbl_feedback.config(text="")

        if self.mode == "exam" and start_new:
            self.time_left = self.time_per_q
            self.start_timer()

    def start_timer(self):
        self.timer_running = True

        def run_timer():
            while self.time_left > 0 and self.timer_running:
                self.lbl_timer.config(text=f"Timp rămas: {self.time_left}s")
                time.sleep(1)
                self.time_left -= 1
            if self.timer_running and self.time_left <= 0:
                self.lbl_timer.config(text="Timp expirat ⏱️")
                self.submit_and_advance(timeout=True)

        self.timer_thread = threading.Thread(target=run_timer, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        self.timer_running = False

    # ===============================
    # NOUA VARIANTĂ - FEEDBACK ÎN TRAIN
    # ===============================
    def submit_and_advance(self, timeout=False):
        self.stop_timer()

        if self.current_index >= len(self.questions):
            self.end_quiz()
            return

        qdata = self.questions[self.current_index]
        correct_idx = qdata["correct_index"]
        explanation = qdata["explanation"]
        domeniu_q = qdata.get("domain", self.domeniu)

        selected = self.answer_var.get()
        self.asked_count += 1

        corect = (selected == correct_idx)
        if corect:
            self.correct_count += 1
        else:
            self.gresite.append({
                "idx": self.current_index + 1,
                "domain": domeniu_q,
                "question": qdata["question"],
                "choices": qdata["choices"],
                "correct_index": qdata["correct_index"],
                "explanation": qdata["explanation"],
                "timeout": timeout
            })

        # -----------------------------
        # FEEDBACK IMEDIAT (TRAIN)
        # -----------------------------
        if self.mode == "train":
            if corect:
                fb = "✅ Corect!\n"
            else:
                if timeout:
                    fb = "⏱️ Timp expirat.\n"
                else:
                    fb = "❌ Greșit.\n"
                fb += (
                    f"Răspuns corect: {correct_idx + 1}. "
                    f"{qdata['choices'][correct_idx]}\n"
                )
            fb += f"Explicație: {explanation}"
            self.lbl_feedback.config(text=fb)

            self.btn_next.config(
                text="Următoarea întrebare ▶️",
                command=self.next_after_feedback
            )
            return

        # -----------------------------
        # EXAM - doar înregistrează
        # -----------------------------
        if self.mode == "exam":
            if timeout:
                self.lbl_feedback.config(text="Timp expirat ❌")
            else:
                self.lbl_feedback.config(text="Răspuns înregistrat ✅")

        self.current_index += 1
        if self.current_index >= len(self.questions):
            self.end_quiz()
        else:
            self.show_current_question(start_new=True)

    def next_after_feedback(self):
        """Afișează următoarea întrebare după feedback (TRAIN mode)."""
        self.current_index += 1
        if self.current_index >= len(self.questions):
            self.end_quiz()
        else:
            self.show_current_question(start_new=True)

    # ===============================
    # FINAL QUIZ
    # ===============================
    def end_quiz(self):
        self.stop_timer()
        percent = (self.correct_count / self.num_questions) * 100
        msg = (
            f"=== REZULTAT FINAL ===\n"
            f"Scor: {self.correct_count}/{self.num_questions}\n"
            f"Procent: {percent:.1f}%\n"
            f"Mod: {self.mode.upper()}\n\n"
            "Nu-i panică. Reia teoria de bază. Asta se învață 💪\n"
        )

        # REVIEW doar pentru EXAM
        if self.mode == "exam" and self.gresite:
            msg += "\nÎntrebări pentru revizuit:\n"
            for q in self.gresite:
                msg += (
                    f"\n- Q{q['idx']} ({q['domain']})"
                    f"{' (timp expirat)' if q['timeout'] else ''}"
                    f" -> {q['question']}\n"
                    f"  Răspuns corect: {q['choices'][q['correct_index']]}\n"
                    f"  Explicație: {q['explanation']}\n"
                )

        self.lbl_question.config(text=msg)
        for rb in self.options:
            rb.pack_forget()
        self.lbl_feedback.config(text="")
        self.lbl_timer.config(text="")
        self.btn_next.pack_forget()


# ===============================
# FEREASTRA PRINCIPALĂ
# ===============================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("1000x500")
        self.configure(bg="#0d0d0d")
        self.resizable(False, False)

        # Titlu
        lbl_header = tk.Label(
            self,
            text="Setări sesiune",
            bg="#0d0d0d",
            fg="#00bfff",
            font=("Segoe UI", 12, "bold")
        )
        lbl_header.pack(pady=10)

        # Domeniu
        lbl_d = tk.Label(self, text="Domeniu:", bg="#0d0d0d", fg="white", anchor="w")
        lbl_d.pack(fill="x", padx=25)
        self.cmb_domain = ttk.Combobox(
            self,
            values=[
                "Structural (tensiuni / mesh / BC)",
                "Crash / Impact",
                "Moldflow",
                "CFD",
                "NVH",
                "MIX (toate domeniile)"
            ],
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.cmb_domain.current(0)
        self.cmb_domain.pack(fill="x", padx=25, pady=(0, 10))

        # Număr întrebări
        lbl_q = tk.Label(
            self, text="Număr întrebări:", bg="#0d0d0d", fg="white", anchor="w"
        )
        lbl_q.pack(fill="x", padx=25)
        self.spn_num = tk.Spinbox(self, from_=1, to=20, width=5)
        self.spn_num.pack(padx=25, pady=(0, 10), anchor="w")

        # Mod
        lbl_mode = tk.Label(self, text="Mod:", bg="#0d0d0d", fg="white", anchor="w")
        lbl_mode.pack(fill="x", padx=25)
        self.mode_var = tk.StringVar(value="train")
        tk.Radiobutton(
            self,
            text="TRAIN (fără limită timp, feedback imediat)",
            variable=self.mode_var,
            value="train",
            bg="#0d0d0d",
            fg="white",
            selectcolor="#1a1a1a"
        ).pack(anchor="w", padx=25)
        tk.Radiobutton(
            self,
            text="EXAM (limită timp, review la final)",
            variable=self.mode_var,
            value="exam",
            bg="#0d0d0d",
            fg="white",
            selectcolor="#1a1a1a"
        ).pack(anchor="w", padx=25, pady=(0, 10))

        # Timp întrebare
        lbl_time = tk.Label(
            self,
            text="Timp pe întrebare (secunde, doar EXAM):",
            bg="#0d0d0d",
            fg="white",
            anchor="w"
        )
        lbl_time.pack(fill="x", padx=25)
        self.spn_time = tk.Spinbox(self, from_=5, to=60, width=5)
        self.spn_time.pack(padx=25, pady=(0, 15), anchor="w")

        # Buton START
        btn_start = tk.Button(
            self,
            text="Start Quiz",
            command=self.start_quiz,
            bg="#00bfff",
            fg="black",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            width=50
        )
        btn_start.pack(pady=(0, 20))

        # Secțiune rapoarte
        lbl_reports = tk.Label(
            self,
            text="Rapoarte & Analiză",
            bg="#0d0d0d",
            fg="#00bfff",
            font=("Segoe UI", 10, "bold")
        )
        lbl_reports.pack(pady=5)

        self.make_button("Generează grafic progres (.png)", self.run_chart)
        self.make_button("Generează PDF din ultimul EXAM", self.run_pdf)
        self.make_button("Arată progres text (stats)", self.run_stats)

    def make_button(self, text, cmd):
        tk.Button(
            self,
            text=text,
            command=cmd,
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            width=50
        ).pack(pady=5)

    # ===============================
    # BUTOANE SECȚIUNE PRINCIPALĂ
    # ===============================
    def start_quiz(self):
        domeniu = self.cmb_domain.get().split()[0].lower()
        mode = self.mode_var.get()
        num_q = int(self.spn_num.get())
        time_q = int(self.spn_time.get())
        QuizWindow(self, domeniu, mode, num_q, time_q)

    def run_chart(self):
        try:
            subprocess.run(["python", "./src/progress_chart.py"], check=True)
        except Exception as e:
            messagebox.showerror("Eroare la grafic", str(e))

    def run_pdf(self):
        try:
            subprocess.run(["python", "./src/export_pdf.py"], check=True)
        except Exception as e:
            messagebox.showerror("Eroare la PDF", str(e))

    def run_stats(self):
        try:
            subprocess.run(["python", "./src/stats.py"], check=True)
        except Exception as e:
            messagebox.showerror("Eroare la stats", str(e))


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
