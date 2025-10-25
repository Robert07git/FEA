import tkinter as tk
from tkinter import ttk, messagebox
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

        # Mod de testare
        tk.Label(self.root, text="Mod de testare:", bg="#111", fg="white", font=("Arial", 12)).pack(pady=(10, 0))
        self.mode_var = tk.StringVar(value="train")

        frame_modes = tk.Frame(self.root, bg="#111")
        frame_modes.pack(pady=5)

        self.train_btn = tk.Radiobutton(
            frame_modes, text="TRAIN", variable=self.mode_var, value="train",
            indicatoron=0, width=10, font=("Arial", 11, "bold"),
            bg="#00aaaa", fg="white", selectcolor="#00cccc", activebackground="#00cccc",
            command=self.toggle_exam_time
        )
        self.train_btn.pack(side="left", padx=10)

        self.exam_btn = tk.Radiobutton(
            frame_modes, text="EXAM", variable=self.mode_var, value="exam",
            indicatoron=0, width=10, font=("Arial", 11, "bold"),
            bg="#aa0000", fg="white", selectcolor="#ff3333", activebackground="#ff3333",
            command=self.toggle_exam_time
        )
        self.exam_btn.pack(side="left", padx=10)

        # Alegere timp (vizibil doar în modul EXAM)
        self.exam_time_label = tk.Label(self.root, text="Timp per întrebare (secunde):", bg="#111", fg="white", font=("Arial", 12))
        self.exam_time_spin = tk.Spinbox(self.root, from_=5, to=120, width=5)
        self.exam_time_label.pack_forget()
        self.exam_time_spin.pack_forget()

        # Buton START
        start_btn = tk.Button(
            self.root, text="Start Quiz", font=("Arial", 14, "bold"),
            bg="#00ffcc", fg="black", command=self.start_quiz
        )
        start_btn.pack(pady=30)

        # Alte butoane
        extras_frame = tk.Frame(self.root, bg="#111")
        extras_frame.pack(pady=15)

        tk.Button(extras_frame, text="Statistici 📊", font=("Arial", 11),
                  bg="#222", fg="white", command=show_dashboard).pack(side="left", padx=5)
        tk.Button(extras_frame, text="Grafic progres 📈", font=("Arial", 11),
                  bg="#222", fg="white", command=show_progress_chart).pack(side="left", padx=5)
        tk.Button(extras_frame, text="Export PDF 📝", font=("Arial", 11),
                  bg="#222", fg="white", command=export_quiz_pdf).pack(side="left", padx=5)

    def toggle_exam_time(self):
        """Afișează câmpul pentru timp doar când e selectat modul EXAM"""
        if self.mode_var.get() == "exam":
            self.exam_time_label.pack()
            self.exam_time_spin.pack(pady=5)
        else:
            self.exam_time_label.pack_forget()
            self.exam_time_spin.pack_forget()

    def start_quiz(self):
        domain = self.domain_var.get()
        mode = self.mode_var.get()
        num_questions = self.num_questions_var.get()

        questions = load_questions(domain)
        if not questions:
            messagebox.showerror("Eroare", f"Nu există întrebări pentru domeniul '{domain}'.")
            return

        time_limit = None
        if mode == "exam":
            time_limit = int(self.exam_time_spin.get())

        # Fereastră nouă pentru sesiunea de quiz
        quiz_window = tk.Toplevel(self.root)
        quiz_window.title(f"FEA Quiz Session - {domain.upper()}")
        quiz_window.geometry("900x600")
        quiz_window.configure(bg="#111")

        QuizSession(quiz_window, questions, num_questions, mode, time_limit)


# === Pornirea aplicației ===
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
