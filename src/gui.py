import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from quiz_logic import run_quiz
from data_loader import load_questions
from export_pdf import export_pdf_report
from progress_chart import show_progress_chart
from stats import format_statistics


class FEATrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("900x650")
        self.configure(bg="#0A0A0A")

        self.mode = tk.StringVar(value="train")
        self.domain = tk.StringVar(value="structural")
        self.num_questions = tk.IntVar(value=5)
        self.time_limit_sec = tk.IntVar(value=15)

        self.current_question_index = 0
        self.current_score = 0
        self.questions = []
        self.selected_answer = tk.IntVar(value=-1)
        self.time_remaining = 0
        self.timer_running = False

        self.create_menu()
        self.create_main_ui()

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="📄 Export PDF Report", command=self.export_pdf)
        file_menu.add_command(label="📈 Show Progress Chart", command=self.show_chart)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.quit)
        menubar.add_cascade(label="Menu", menu=file_menu)
        self.config(menu=menubar)

    def create_main_ui(self):
        self.title_label = tk.Label(self, text="FEA Quiz Trainer",
                                    font=("Segoe UI", 22, "bold"), fg="#00FFFF", bg="#0A0A0A")
        self.title_label.pack(pady=20)

        # domeniu
        tk.Label(self, text="Alege domeniu:", fg="white", bg="#0A0A0A").pack()
        self.domain_combo = ttk.Combobox(self, values=[
            "structural", "crash", "moldflow", "cfd", "nvh", "mix"])
        self.domain_combo.current(0)
        self.domain_combo.pack(pady=5)

        # mod
        tk.Label(self, text="Mod:", fg="white", bg="#0A0A0A").pack()
        frame_modes = tk.Frame(self, bg="#0A0A0A")
        frame_modes.pack()
        self.train_btn = ttk.Radiobutton(frame_modes, text="Train", variable=self.mode, value="train")
        self.exam_btn = ttk.Radiobutton(frame_modes, text="Exam", variable=self.mode, value="exam")
        self.train_btn.grid(row=0, column=0, padx=10)
        self.exam_btn.grid(row=0, column=1, padx=10)

        # nr intrebari
        tk.Label(self, text="Număr întrebări:", fg="white", bg="#0A0A0A").pack()
        tk.Entry(self, textvariable=self.num_questions, width=5, justify="center").pack()

        # timp per întrebare
        tk.Label(self, text="Timp per întrebare (secunde):", fg="white", bg="#0A0A0A").pack()
        tk.Entry(self, textvariable=self.time_limit_sec, width=5, justify="center").pack()

        # start
        tk.Button(self, text="🚀 Start Quiz", font=("Segoe UI", 12, "bold"),
                  command=self.start_quiz, bg="#00FFFF", fg="black").pack(pady=15)

        # statistici
        self.stats_label = tk.Label(self, text=format_statistics(),
                                    fg="#00FFFF", bg="#0A0A0A", justify="left", font=("Consolas", 10))
        self.stats_label.pack(pady=10)

    def export_pdf(self):
        path = export_pdf_report()
        messagebox.showinfo("Export PDF", f"Raportul a fost salvat în:\n{path}")

    def show_chart(self):
        show_progress_chart()

    def start_quiz(self):
        domain = self.domain_combo.get()
        num = self.num_questions.get()
        mode = self.mode.get()
        tlimit = self.time_limit_sec.get()

        self.questions = load_questions(domain)
        if len(self.questions) == 0:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul {domain}.")
            return

        random.shuffle(self.questions)
        self.questions = self.questions[:num]
        self.current_question_index = 0
        self.current_score = 0

        self.show_question_ui(mode, tlimit)

    def show_question_ui(self, mode, time_limit):
        for widget in self.winfo_children():
            widget.destroy()

        q = self.questions[self.current_question_index]
        self.selected_answer.set(-1)

        tk.Label(self, text=f"Întrebarea {self.current_question_index + 1}/{len(self.questions)}",
                 fg="#00FFFF", bg="#0A0A0A", font=("Segoe UI", 12, "bold")).pack(pady=10)

        tk.Label(self, text=q["question"], wraplength=800, fg="white",
                 bg="#0A0A0A", font=("Segoe UI", 13)).pack(pady=10)

        for i, choice in enumerate(q["choices"]):
            rb = ttk.Radiobutton(self, text=choice, variable=self.selected_answer, value=i)
            rb.pack(anchor="w", padx=50, pady=3)

        self.feedback_label = tk.Label(self, text="", fg="white", bg="#0A0A0A", font=("Segoe UI", 12))
        self.feedback_label.pack(pady=10)

        # Bara progres
        self.progress = ttk.Progressbar(self, length=400, mode="determinate", maximum=time_limit)
        self.progress.pack(pady=10)
        self.progress["value"] = 0

        self.timer_label = tk.Label(self, text=f"Timp rămas: {time_limit}s", fg="#00FFFF", bg="#0A0A0A")
        self.timer_label.pack()

        self.submit_btn = tk.Button(self, text="Trimite răspunsul", command=lambda: self.check_answer(mode))
        self.submit_btn.pack(pady=10)

        self.time_remaining = time_limit
        if mode == "exam":
            self.timer_running = True
            threading.Thread(target=self.update_timer, daemon=True).start()

    def update_timer(self):
        while self.timer_running and self.time_remaining > 0:
            time.sleep(1)
            self.time_remaining -= 1
            self.progress["value"] = self.progress["maximum"] - self.time_remaining
            self.timer_label.config(text=f"Timp rămas: {self.time_remaining}s")
            if self.time_remaining <= 0:
                self.check_answer("exam")

    def check_answer(self, mode):
        self.timer_running = False
        q = self.questions[self.current_question_index]
        ans = self.selected_answer.get()

        if ans == -1:
            self.feedback_label.config(text="⚠️ Nu ai selectat niciun răspuns!", fg="orange")
            return

        correct = (ans == q["correct_index"])
        if correct:
            self.current_score += 1
            self.feedback_label.config(text="✅ Corect!", fg="lightgreen")
        else:
            text = f"❌ Greșit! Corect: {q['choices'][q['correct_index']]}"
            if mode == "train":
                text += f"\n💡 Explicație: {q['explanation']}"
            self.feedback_label.config(text=text, fg="red")

        self.after(1800, self.next_question, mode)

    def next_question(self, mode):
        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            self.show_question_ui(mode, self.time_limit_sec.get())
        else:
            pct = (self.current_score / len(self.questions)) * 100
            messagebox.showinfo("Rezultat Final",
                                f"Scor final: {self.current_score}/{len(self.questions)} ({pct:.1f}%)")
            self.destroy()


if __name__ == "__main__":
    app = FEATrainerApp()
    app.mainloop()
