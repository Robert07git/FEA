import tkinter as tk
from tkinter import ttk, messagebox
import os
import random
from data_loader import load_questions, get_domains
from quiz_logic import QuizSession
from progress_chart import show_progress_chart
from export_pdf import export_quiz_pdf
from stats import show_dashboard


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FEA Quiz Trainer")
        self.root.geometry("800x600")
        self.root.configure(bg="#111")
        self.root.resizable(False, False)

        self.domains = get_domains()
        if not self.domains:
            self.domains = ["structural", "crash", "moldflow", "cfd", "nvh", "mix"]

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root,
            text="FEA QUIZ TRAINER",
            font=("Arial", 20, "bold"),
            bg="#111",
            fg="#00ffff"
        ).pack(pady=20)

        # Domeniu
        tk.Label(self.root, text="Alege domeniul:", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.domain_var = tk.StringVar(value="mix")
        domain_menu = ttk.Combobox(self.root, textvariable=self.domain_var, values=self.domains, state="readonly")
        domain_menu.pack(pady=10)

        # Număr întrebări
        tk.Label(self.root, text="Număr întrebări:", bg="#111", fg="white", font=("Arial", 12)).pack()
        self.num_questions_var = tk.IntVar(value=5)
        tk.Spinbox(self.root, from_=1, to=50, textvariable=self.num_questions_var, width=5).pack(pady=10)

        # Mod (TRAIN / EXAM)
        tk.Label(self.root, text="Mod de testare:", bg="#111", fg="white", font=("Arial", 12)).pack(pady=(10, 0))
        self.mode_var = tk.StringVar(value="train")

        frame_modes = tk.Frame(self.root, bg="#111")
        frame_modes.pack(pady=5)

        self.train_btn = tk.Radiobutton(
            frame_modes, text="TRAIN", variable=self.mode_var, value="train",
            indicatoron=0, width=10, font=("Arial", 11, "bold"),
            bg="#00aaaa", fg="white", selectcolor="#00cccc", activebackground="#00cccc"
        )
        self.train_btn.pack(side="left", padx=5)

        self.exam_btn = tk.Radiobutton(
            frame_modes, text="EXAM", variable=self.mode_var, value="exam",
            indicatoron=0, width=10, font=("Arial", 11, "bold"),
            bg="#333", fg="white", selectcolor="#00cccc", activebackground="#00cccc"
        )
        self.exam_btn.pack(side="left", padx=5)

        # Timp per întrebare (doar pentru exam)
        tk.Label(self.root, text="Timp per întrebare (secunde):", bg="#111", fg="white", font=("Arial", 12)).pack(pady=(15, 0))
        self.time_limit_var = tk.IntVar(value=15)
        tk.Spinbox(self.root, from_=5, to=120, textvariable=self.time_limit_var, width=5).pack(pady=10)

        # Butoane principale
        button_frame = tk.Frame(self.root, bg="#111")
        button_frame.pack(pady=20)

        start_btn = tk.Button(
            button_frame,
            text="▶ Start Quiz",
            bg="#00ffff", fg="black", font=("Arial", 12, "bold"),
            relief="flat", width=14, command=self.start_quiz
        )
        start_btn.grid(row=0, column=0, padx=10, pady=10)

        chart_btn = tk.Button(
            button_frame,
            text="📊 Grafic progres",
            bg="#00cccc", fg="black", font=("Arial", 12, "bold"),
            relief="flat", width=14, command=show_progress_chart
        )
        chart_btn.grid(row=0, column=1, padx=10, pady=10)

        pdf_btn = tk.Button(
            button_frame,
            text="📄 Generează PDF",
            bg="#0099ff", fg="white", font=("Arial", 12, "bold"),
            relief="flat", width=14, command=export_quiz_pdf
        )
        pdf_btn.grid(row=1, column=0, padx=10, pady=10)

        stats_btn = tk.Button(
            button_frame,
            text="📈 Statistici",
            bg="#0066cc", fg="white", font=("Arial", 12, "bold"),
            relief="flat", width=14, command=show_dashboard
        )
        stats_btn.grid(row=1, column=1, padx=10, pady=10)

    def start_quiz(self):
        domain = self.domain_var.get()
        num_questions = self.num_questions_var.get()
        mode = self.mode_var.get()
        time_limit = self.time_limit_var.get()

        questions = load_questions(domain)
        if not questions:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul '{domain}'!")
            return

        if num_questions > len(questions):
            num_questions = len(questions)

        selected_questions = random.sample(questions, num_questions)

        for widget in self.root.winfo_children():
            widget.destroy()

        QuizSession(self.root, selected_questions, mode=mode, time_limit=time_limit, on_end=self.quiz_finished)

    def quiz_finished(self, correct, total, results):
        from datetime import datetime
        pct = (correct / total) * 100 if total > 0 else 0
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_path = os.path.join(base_dir, "score_history.txt")

        with open(history_path, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            line = f"{timestamp} | domeniu={self.domain_var.get()} | mod={self.mode_var.get()} | scor={correct}/{total} | procent={pct:.1f}% | timp_total=- | timp_intrebare={self.time_limit_var.get()}s\n"
            f.write(line)

        messagebox.showinfo("Rezultat final", f"Scor final: {correct}/{total} ({pct:.1f}%)\nRezultatul a fost salvat în score_history.txt ✅")
        self.root.destroy()
