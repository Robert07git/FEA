import tkinter as tk
from tkinter import messagebox
import random, time, threading
from playsound import playsound
from data_loader import load_questions

class QuizWindow(tk.Toplevel):
    def __init__(self, parent, domain, num_questions, mode, time_limit):
        super().__init__(parent)
        self.parent = parent
        self.domain = domain
        self.mode = mode
        self.time_limit = time_limit
        self.questions = load_questions(domain)[:num_questions]
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.remaining_time = time_limit or 0
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.configure(bg="#111")
        self.geometry("920x580")
        self.title("FEA Quiz Session")
        self.create_ui()

        if mode == "exam":
            self.start_timer()

    # ======================
    # INTERFAȚĂ
    # ======================
    def create_ui(self):
        self.lbl_title = tk.Label(self, text="FEA Quiz", fg="#00FFFF", bg="#111", font=("Segoe UI", 18, "bold"))
        self.lbl_title.pack(pady=10)

        self.lbl_question = tk.Label(self, text="", fg="white", bg="#111", font=("Segoe UI", 13), wraplength=800)
        self.lbl_question.pack(pady=15)

        self.frm_options = tk.Frame(self, bg="#111")
        self.frm_options.pack()

        self.var_selected = tk.IntVar(value=-1)
        self.option_buttons = []

        self.lbl_timer = tk.Label(self, text="", fg="#00FFFF", bg="#111", font=("Consolas", 13))
        self.lbl_timer.pack(pady=5)

        self.btn_next = tk.Button(self, text="Următoarea ➜", command=self.next_question,
                                  bg="#00FFFF", fg="#111", font=("Segoe UI", 11, "bold"))
        self.btn_next.pack(pady=15)

        self.show_question()

    def show_question(self):
        if self.current_index >= len(self.questions):
            self.finish_quiz()
            return

        q = self.questions[self.current_index]
        self.lbl_question.config(text=f"Întrebarea {self.current_index+1}/{len(self.questions)}:\n{q['question']}")

        for btn in self.option_buttons:
            btn.destroy()
        self.option_buttons.clear()

        options = q.get("options", q.get("choices", []))
        random.shuffle(options)

        for i, opt in enumerate(options):
            b = tk.Radiobutton(
                self.frm_options, text=opt, variable=self.var_selected, value=i,
                font=("Segoe UI", 11), bg="#111", fg="white", selectcolor="#222", activebackground="#222"
            )
            b.pack(anchor="w", pady=3)
            self.option_buttons.append(b)

        self.var_selected.set(-1)

    # ======================
    # TIMER
    # ======================
    def start_timer(self):
        def countdown():
            while self.remaining_time > 0:
                mins, secs = divmod(self.remaining_time, 60)
                self.lbl_timer.config(text=f"Timp rămas: {mins:02}:{secs:02}")
                if self.remaining_time == 5:
                    threading.Thread(target=lambda: playsound("alert.mp3", block=False)).start()
                time.sleep(1)
                self.remaining_time -= 1
            if self.remaining_time <= 0:
                self.next_question()
        threading.Thread(target=countdown, daemon=True).start()

    # ======================
    # NAVIGARE
    # ======================
    def next_question(self):
        selected = self.var_selected.get()
        q = self.questions[self.current_index]
        correct = q["correct"]
        is_correct = selected == correct

        self.user_answers.append((q["question"], is_correct))
        if is_correct:
            self.score += 1

        self.current_index += 1
        self.remaining_time = self.time_limit or 0
        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        total = len(self.questions)
        percent = (self.score / total) * 100
        messagebox.showinfo("Rezultate", f"Scor: {self.score}/{total} ({percent:.1f}%)")
        self.destroy()
        self.parent.deiconify()

    def on_close(self):
        if messagebox.askokcancel("Confirmare", "Ești sigur că vrei să ieși?"):
            self.destroy()
            self.parent.deiconify()
