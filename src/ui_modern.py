import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from PIL import Image, ImageTk
from quiz_engine_modern import QuizEngine
from stats_manager import load_stats
from pdf_exporter_modern import export_pdf_modern as export_to_pdf
from settings_manager import load_settings, save_settings
from data_loader import load_questions, load_learning_materials
import json

# ------------------------------
# INITIAL SETUP
# ------------------------------
class FEATrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("1200x700")
        self.configure(bg="#121212")
        self.resizable(True, True)

        # load settings
        self.settings = load_settings()
        self.username = self.settings.get("username", "Guest")
        self.dark_mode = self.settings.get("dark_mode", True)
        self.num_questions = self.settings.get("num_questions", 10)

        self.current_mode = None
        self.current_domain = None
        self.quiz_engine = None
        self.frames = {}
        self.score_data = []

        self.sidebar_color = "#1e1e1e" if self.dark_mode else "#e0e0e0"
        self.main_color = "#121212" if self.dark_mode else "#f5f5f5"
        self.text_color = "#ffffff" if self.dark_mode else "#000000"
        self.accent_color = "#00bcd4"

        # leaderboard path
        self.leaderboard_path = os.path.join("data", "leaderboard.json")
        if not os.path.exists(self.leaderboard_path):
            os.makedirs("data", exist_ok=True)
            with open(self.leaderboard_path, "w") as f:
                json.dump({
                    "Structural": [],
                    "Crash": [],
                    "CFD": [],
                    "NVH": []
                }, f, indent=4)

        # sidebar setup
        self.sidebar = tk.Frame(self, bg=self.sidebar_color, width=200)
        self.sidebar.pack(side="left", fill="y")

        title = tk.Label(
            self.sidebar,
            text="FEA Trainer",
            font=("Segoe UI", 18, "bold"),
            fg=self.accent_color,
            bg=self.sidebar_color,
            pady=20
        )
        title.pack()

        self.main_frame = tk.Frame(self, bg=self.main_color)
        self.main_frame.pack(side="right", expand=True, fill="both")

        # buttons
        buttons = [
            ("🏋️ Train", self.show_train),
            ("🧾 Exam", self.show_exam),
            ("📘 Learn", self.show_learn),
            ("📈 Stats", self.show_stats),
            ("📄 Export PDF", self.export_pdf),
            ("🏆 Leaderboard", self.show_leaderboard),
            ("⚙️ Settings", self.show_settings),
        ]

        for (text, command) in buttons:
            b = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 11, "bold"),
                bg=self.sidebar_color,
                fg=self.text_color,
                relief="flat",
                activebackground=self.accent_color,
                activeforeground="#ffffff",
                command=command,
                cursor="hand2"
            )
            b.pack(fill="x", pady=5, padx=10)

        # welcome message
        self.welcome_label = tk.Label(
            self.main_frame,
            text=f"Welcome back, {self.username} 👋\nReady to train your FEA skills?",
            font=("Segoe UI", 18, "bold"),
            fg=self.accent_color,
            bg=self.main_color,
            justify="center"
        )
        self.welcome_label.pack(expand=True)

    # ------------------------------
    # CLEAN MAIN FRAME
    # ------------------------------
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ------------------------------
    # TRAIN MODE
    # ------------------------------
    def show_train(self):
        self.clear_main_frame()
        self.current_mode = "train"
        self.current_domain = None

        domain_label = tk.Label(
            self.main_frame,
            text="Select domain for TRAIN mode",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        )
        domain_label.pack(pady=10)

        domains = ["Structural", "Crash", "CFD", "NVH"]

        for domain in domains:
            b = tk.Button(
                self.main_frame,
                text=domain,
                font=("Segoe UI", 13),
                bg=self.accent_color,
                fg="#ffffff",
                relief="flat",
                command=lambda d=domain: self.start_quiz(d, "train")
            )
            b.pack(pady=5, ipadx=10, ipady=3)

    # ------------------------------
    # EXAM MODE
    # ------------------------------
    def show_exam(self):
        self.clear_main_frame()
        self.current_mode = "exam"
        self.current_domain = None

        domain_label = tk.Label(
            self.main_frame,
            text="Select domain for EXAM mode",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        )
        domain_label.pack(pady=10)

        domains = ["Structural", "Crash", "CFD", "NVH"]

        for domain in domains:
            b = tk.Button(
                self.main_frame,
                text=domain,
                font=("Segoe UI", 13),
                bg=self.accent_color,
                fg="#ffffff",
                relief="flat",
                command=lambda d=domain: self.start_quiz(d, "exam")
            )
            b.pack(pady=5, ipadx=10, ipady=3)
    # ------------------------------
    # START QUIZ (COMMON FUNCTION)
    # ------------------------------
    def start_quiz(self, domain, mode):
        self.clear_main_frame()
        self.current_domain = domain
        self.current_mode = mode

        questions = load_questions(domain)
        if not questions:
            messagebox.showerror("Error", f"No questions found for {domain}.")
            return

        if len(questions) > self.num_questions:
            import random
            questions = random.sample(questions, self.num_questions)

        self.quiz_engine = QuizEngine(questions, mode, self.username)
        self.quiz_engine.start()

        self.progress_var = tk.DoubleVar(value=0)
        self.timer_var = tk.StringVar(value="00:00")

        top_frame = tk.Frame(self.main_frame, bg=self.main_color)
        top_frame.pack(fill="x", pady=10)

        tk.Label(
            top_frame,
            text=f"{domain} - {mode.upper()} MODE",
            font=("Segoe UI", 15, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        ).pack(side="left", padx=20)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            top_frame,
            variable=self.progress_var,
            maximum=len(questions)
        )
        self.progress_bar.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        # Timer
        self.timer_label = tk.Label(
            top_frame,
            textvariable=self.timer_var,
            font=("Segoe UI", 12),
            fg=self.text_color,
            bg=self.main_color
        )
        self.timer_label.pack(side="right", padx=20)

        self.start_time = datetime.now()
        self.update_timer()

        self.show_next_question()

    # ------------------------------
    # TIMER
    # ------------------------------
    def update_timer(self):
        if not hasattr(self, "start_time"):
            return
        elapsed = (datetime.now() - self.start_time).seconds
        mins, secs = divmod(elapsed, 60)
        self.timer_var.set(f"{mins:02}:{secs:02}")
        self.after(1000, self.update_timer)

    # ------------------------------
    # SHOW NEXT QUESTION
    # ------------------------------
    def show_next_question(self):
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.main_frame:
                widget.destroy()

        question = self.quiz_engine.get_next_question()
        if not question:
            self.finish_quiz()
            return

        q_frame = tk.Frame(self.main_frame, bg=self.main_color)
        q_frame.pack(pady=20)

        q_label = tk.Label(
            q_frame,
            text=question["question"],
            font=("Segoe UI", 14, "bold"),
            wraplength=900,
            justify="left",
            fg=self.text_color,
            bg=self.main_color
        )
        q_label.pack(pady=10)

        self.selected_option = tk.StringVar()

        for opt in question["options"]:
            rb = tk.Radiobutton(
                q_frame,
                text=opt,
                variable=self.selected_option,
                value=opt,
                font=("Segoe UI", 12),
                bg=self.main_color,
                fg=self.text_color,
                selectcolor=self.main_color,
                activebackground=self.main_color,
                activeforeground=self.accent_color
            )
            rb.pack(anchor="w", padx=20, pady=3)

        submit_btn = tk.Button(
            q_frame,
            text="Submit",
            bg=self.accent_color,
            fg="#ffffff",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            command=lambda q=question: self.submit_answer(q)
        )
        submit_btn.pack(pady=10)

        progress = self.quiz_engine.current_index
        total = len(self.quiz_engine.questions)
        self.progress_var.set(progress)
        self.progress_bar["value"] = progress
        self.progress_bar["maximum"] = total

    # ------------------------------
    # SUBMIT ANSWER
    # ------------------------------
    def submit_answer(self, question):
        selected = self.selected_option.get()
        if not selected:
            messagebox.showwarning("Select an answer", "Please select an option.")
            return

        correct = self.quiz_engine.submit_answer(question, selected)

        if self.current_mode == "train":
            msg = "✅ Correct!" if correct else f"❌ Wrong!\nCorrect: {question['answer']}"
            messagebox.showinfo("Result", msg + f"\n\n{question.get('explanation', '')}")

        self.show_next_question()

    # ------------------------------
    # FINISH QUIZ
    # ------------------------------
    def finish_quiz(self):
        result = self.quiz_engine.finish()
        score = result["score"]
        total_time = result["total_time"]

        # save leaderboard entry
        with open(self.leaderboard_path, "r") as f:
            leaderboard = json.load(f)
        entry = {
            "username": self.username,
            "score": score,
            "time": total_time,
            "mode": self.current_mode,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        leaderboard[self.current_domain].append(entry)
        leaderboard[self.current_domain] = sorted(
            leaderboard[self.current_domain],
            key=lambda x: x["score"],
            reverse=True
        )[:10]
        with open(self.leaderboard_path, "w") as f:
            json.dump(leaderboard, f, indent=4)

        messagebox.showinfo(
            "Quiz Complete",
            f"You completed the quiz!\n\nScore: {score}%\nTime: {total_time}s"
        )

        if self.current_mode == "exam":
            explanations = "\n\n".join([
                f"Q: {r['question']}\nYour: {r['selected']}\nCorrect: {r['correct']}\n→ {r['explanation']}"
                for r in result["results"]
            ])
            self.clear_main_frame()
            tk.Label(
                self.main_frame,
                text=f"Exam completed — Score: {score}%\n\nDetailed Review:",
                font=("Segoe UI", 14, "bold"),
                fg=self.accent_color,
                bg=self.main_color
            ).pack(pady=10)
            text_box = tk.Text(
                self.main_frame,
                wrap="word",
                font=("Segoe UI", 11),
                bg=self.main_color,
                fg=self.text_color,
                height=25,
                width=110
            )
            text_box.insert("1.0", explanations)
            text_box.config(state="disabled")
            text_box.pack(padx=20, pady=10)

        back_btn = tk.Button(
            self.main_frame,
            text="⬅️ Back to Menu",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg="#ffffff",
            relief="flat",
            command=self.return_to_menu
        )
        back_btn.pack(pady=10)

    # ------------------------------
    # RETURN TO MAIN MENU
    # ------------------------------
    def return_to_menu(self):
        self.clear_main_frame()
        self.welcome_label = tk.Label(
            self.main_frame,
            text=f"Welcome back, {self.username} 👋\nReady to train your FEA skills?",
            font=("Segoe UI", 18, "bold"),
            fg=self.accent_color,
            bg=self.main_color,
            justify="center"
        )
        self.welcome_label.pack(expand=True)

    # ------------------------------
    # LEARN MODE
    # ------------------------------
    def show_learn(self):
        self.clear_main_frame()
        tk.Label(
            self.main_frame,
            text="Learning Center 📘",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        ).pack(pady=10)

        domains = ["Structural", "Crash", "CFD", "NVH"]
        for d in domains:
            b = tk.Button(
                self.main_frame,
                text=d,
                font=("Segoe UI", 13),
                bg=self.accent_color,
                fg="#ffffff",
                relief="flat",
                command=lambda dom=d: self.open_learn_domain(dom)
            )
            b.pack(pady=5, ipadx=10, ipady=3)

    def open_learn_domain(self, domain):
        self.clear_main_frame()
        tk.Label(
            self.main_frame,
            text=f"{domain} – Theoretical Concepts",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        ).pack(pady=10)

        materials = load_learning_materials(domain)
        if not materials:
            messagebox.showerror("Error", f"No learning materials found for {domain}.")
            return

        canvas = tk.Canvas(self.main_frame, bg=self.main_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.main_color)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, item in enumerate(materials):
            tk.Label(
                scroll_frame,
                text=f"{idx+1}. {item['title']}",
                font=("Segoe UI", 13, "bold"),
                fg=self.accent_color,
                bg=self.main_color,
                anchor="w",
                justify="left"
            ).pack(fill="x", padx=20, pady=5)

            tk.Label(
                scroll_frame,
                text=item["content"],
                font=("Segoe UI", 11),
                fg=self.text_color,
                bg=self.main_color,
                wraplength=950,
                justify="left"
            ).pack(fill="x", padx=20, pady=5)

            img_path = item.get("image")
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((500, 300))
                photo = ImageTk.PhotoImage(img)
                label_img = tk.Label(scroll_frame, image=photo, bg=self.main_color)
                label_img.image = photo
                label_img.pack(pady=10)
    # ------------------------------
    # STATS VIEW
    # ------------------------------
    def show_stats(self):
        self.clear_main_frame()
        tk.Label(
            self.main_frame,
            text="📈 Performance Statistics",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        ).pack(pady=10)

        stats = load_stats()
        if not stats:
            tk.Label(
                self.main_frame,
                text="No statistics available yet.",
                font=("Segoe UI", 12),
                fg=self.text_color,
                bg=self.main_color
            ).pack(pady=20)
            return

        tree = ttk.Treeview(self.main_frame, columns=("Domain", "Score", "Mode", "Date"), show="headings")
        tree.heading("Domain", text="Domain")
        tree.heading("Score", text="Score (%)")
        tree.heading("Mode", text="Mode")
        tree.heading("Date", text="Date")
        tree.column("Domain", width=120, anchor="center")
        tree.column("Score", width=100, anchor="center")
        tree.column("Mode", width=100, anchor="center")
        tree.column("Date", width=180, anchor="center")
        tree.pack(expand=True, fill="both", padx=20, pady=10)

        for s in stats:
            tree.insert("", "end", values=(s["domain"], s["score"], s["mode"], s["date"]))

    # ------------------------------
    # EXPORT PDF
    # ------------------------------
    def export_pdf(self):
        stats = load_stats()
        if not stats:
            messagebox.showwarning("No data", "No quiz data available to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF report as..."
        )
        if not file_path:
            return
        export_to_pdf(stats, file_path)
        messagebox.showinfo("Exported", f"PDF report saved successfully:\n{file_path}")

    # ------------------------------
    # LEADERBOARD
    # ------------------------------
    def show_leaderboard(self):
        self.clear_main_frame()
        tk.Label(
            self.main_frame,
            text="🏆 Global Leaderboard",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        ).pack(pady=10)

        with open(self.leaderboard_path, "r") as f:
            leaderboard = json.load(f)

        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        for domain, entries in leaderboard.items():
            frame = tk.Frame(notebook, bg=self.main_color)
            notebook.add(frame, text=domain)
            tree = ttk.Treeview(
                frame,
                columns=("User", "Score", "Time", "Mode", "Date"),
                show="headings"
            )
            for col in ("User", "Score", "Time", "Mode", "Date"):
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            tree.pack(expand=True, fill="both", padx=10, pady=10)
            for e in entries:
                tree.insert("", "end", values=(e["username"], e["score"], e["time"], e["mode"], e["date"]))

    # ------------------------------
    # SETTINGS
    # ------------------------------
    def show_settings(self):
        self.clear_main_frame()
        tk.Label(
            self.main_frame,
            text="⚙️ Settings",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.main_color
        ).pack(pady=10)

        frame = tk.Frame(self.main_frame, bg=self.main_color)
        frame.pack(pady=20)

        tk.Label(frame, text="Username:", font=("Segoe UI", 12), fg=self.text_color, bg=self.main_color).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        username_entry = tk.Entry(frame, font=("Segoe UI", 12))
        username_entry.insert(0, self.username)
        username_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Number of Questions:", font=("Segoe UI", 12), fg=self.text_color, bg=self.main_color).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        num_spin = tk.Spinbox(frame, from_=5, to=50, width=5, font=("Segoe UI", 12))
        num_spin.delete(0, "end")
        num_spin.insert(0, self.num_questions)
        num_spin.grid(row=1, column=1, pady=5)

        dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        tk.Checkbutton(
            frame,
            text="Enable Dark Mode",
            variable=dark_mode_var,
            bg=self.main_color,
            fg=self.text_color,
            selectcolor=self.main_color,
            font=("Segoe UI", 12)
        ).grid(row=2, column=0, columnspan=2, pady=5)

        def save_and_apply():
            self.username = username_entry.get().strip() or "Guest"
            self.num_questions = int(num_spin.get())
            self.dark_mode = dark_mode_var.get()

            self.settings["username"] = self.username
            self.settings["num_questions"] = self.num_questions
            self.settings["dark_mode"] = self.dark_mode
            save_settings(self.settings)

            messagebox.showinfo("Saved", "Settings updated successfully.\nRestart app to apply theme.")
            self.return_to_menu()

        tk.Button(
            frame,
            text="💾 Save Settings",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg="#ffffff",
            relief="flat",
            command=save_and_apply
        ).grid(row=3, column=0, columnspan=2, pady=10)

# ------------------------------
# MAIN EXECUTION
# ------------------------------
if __name__ == "__main__":
    app = FEATrainerApp()
    app.mainloop()
