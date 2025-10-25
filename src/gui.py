import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from quiz_logic import QuizWindow
from progress_chart import generate_progress_chart
from export_pdf import generate_exam_report


class FEAGui(tk.Tk):
    def __init__(self):
        super().__init__()

        # fereastra principală
        self.title("FEA Quiz Trainer")
        self.configure(bg="#111")
        self.geometry("900x650")

        # stil general (dark)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "TLabel",
            background="#111",
            foreground="white",
            font=("Segoe UI", 11)
        )
        self.style.configure(
            "Header.TLabel",
            background="#111",
            foreground="#00FFFF",
            font=("Segoe UI", 16, "bold")
        )
        self.style.configure(
            "SectionTitle.TLabel",
            background="#111",
            foreground="#00FFFF",
            font=("Segoe UI", 13, "bold")
        )
        self.style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            background="#00FFFF",
            foreground="black",
            padding=6
        )
        self.style.map(
            "TButton",
            background=[("active", "#00e0e0")]
        )

        self.style.configure(
            "Dark.TFrame",
            background="#111",
            borderwidth=0,
            relief="flat"
        )

        self.style.configure(
            "Card.TFrame",
            background="#111",
            relief="flat",
            borderwidth=1
        )

        # variabile UI
        self.domain_var = tk.StringVar(value="structural")
        self.num_questions_var = tk.IntVar(value=5)
        self.mode_var = tk.StringVar(value="TRAIN")  # TRAIN sau EXAM
        self.time_limit_var = tk.IntVar(value=15)

        # încărcăm toate întrebările din fișierul JSON
        self.all_questions = self.load_questions()

        # UI
        self.build_main_ui()

    # -------------------------------------------------
    # ÎNCĂRCARE ÎNTREBĂRI DIN data/fea_questions.json
    # -------------------------------------------------
    def load_questions(self):
        """
        Returnează lista cu toate întrebările din data/fea_questions.json.
        Ridică mesaj de eroare dacă nu e găsit.
        """
        # construim path-ul absolut la fea_questions.json
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        #   <proiect>/FEA
        data_path = os.path.join(base_dir, "data", "fea_questions.json")

        if not os.path.exists(data_path):
            messagebox.showerror(
                "Eroare",
                "Fișierul fea_questions.json nu a fost găsit!\n"
                "Asigură-te că este în folderul /data lângă /src."
            )
            return []

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror(
                "Eroare",
                f"Nu pot citi fea_questions.json:\n{e}"
            )
            return []

        # verificare minimă de structură
        ok = []
        for q in data:
            if (
                "domain" in q and
                "question" in q and
                "choices" in q and
                "correct_index" in q
            ):
                ok.append(q)
        return ok

    # -------------------------------------------------
    # FUNCȚIE: START QUIZ
    # -------------------------------------------------
    def start_quiz(self):
        """
        Strânge setările UI, filtrează întrebările pe domeniu,
        ia un subset random și deschide fereastra de quiz (QuizWindow).
        """
        domain = self.domain_var.get().strip()
        num_q = self.num_questions_var.get()
        mode = self.mode_var.get().strip()  # TRAIN / EXAM
        tlim = self.time_limit_var.get() if mode == "EXAM" else None

        # extragem doar întrebările din domeniul selectat
        domain_questions = [
            q for q in self.all_questions
            if q.get("domain", "").lower() == domain.lower()
        ]

        if len(domain_questions) == 0:
            messagebox.showerror(
                "Eroare",
                f"Nu am găsit întrebări pentru domeniul '{domain}'."
            )
            return

        # amestecăm, luăm primele num_q
        random.shuffle(domain_questions)
        selected_list = domain_questions[:num_q]

        # creează fereastra quiz
        try:
            QuizWindow(
                self,
                questions=selected_list,
                mode=mode,
                time_limit=tlim
            )
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu am putut porni quiz-ul:\n{e}")
            return

    # -------------------------------------------------
    # BUTON: GRAFIC PROGRES
    # -------------------------------------------------
    def on_progress_chart(self):
        """
        Generează graficul scorurilor în /src/reports/progress_chart.png
        """
        try:
            img_path = generate_progress_chart()
            messagebox.showinfo(
                "Succes",
                f"Graficul progresului a fost salvat în:\n{img_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Eroare",
                f"Nu am putut genera graficul:\n{e}"
            )

    # -------------------------------------------------
    # BUTON: GENEREAZĂ PDF
    # -------------------------------------------------
    def on_generate_pdf(self):
        """
        Creează PDF raport (ultima sesiune din score_history.txt) în /src/reports.
        """
        try:
            pdf_path = generate_exam_report()
            messagebox.showinfo(
                "Succes",
                f"PDF generat în:\n{pdf_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Eroare",
                f"Nu am putut genera PDF-ul:\n{e}"
            )

    # -------------------------------------------------
    # BUTON: STATISTICI TEXT (rezumat scor_history.txt)
    # -------------------------------------------------
    def on_show_stats(self):
        """
        Deschide un mic rezumat statistic într-un messagebox.
        Citește score_history.txt (domeniu,mod,nr_intrebari,pct)
        """
        history_path = os.path.join(
            os.path.dirname(__file__),
            "score_history.txt"
        )

        if not os.path.exists(history_path):
            messagebox.showinfo(
                "Statistici",
                "Nu există încă score_history.txt (joacă niște quiz-uri mai întâi)."
            )
            return

        sessions = []
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # format domeniu,mod,nq,pct
                    parts = line.split(",")
                    if len(parts) == 4:
                        dom, mode, nq, pct = parts
                        sessions.append((dom, mode, nq, pct))
        except Exception as e:
            messagebox.showerror(
                "Eroare",
                f"Nu pot citi score_history.txt:\n{e}"
            )
            return

        if not sessions:
            messagebox.showinfo(
                "Statistici",
                "score_history.txt e gol sau nu am putut parsa intrările."
            )
            return

        # calculăm niște info
        pct_values = []
        for (_, _, _, pct) in sessions:
            try:
                pct_values.append(float(pct))
            except:
                pass

        if pct_values:
            avg_pct = sum(pct_values) / len(pct_values)
        else:
            avg_pct = 0.0

        last_dom, last_mode, last_nq, last_pct = sessions[-1]
        text = (
            f"Sesiuni totale: {len(sessions)}\n"
            f"Ultima sesiune:\n"
            f"  Domeniu: {last_dom}\n"
            f"  Mod: {last_mode}\n"
            f"  Întrebări: {last_nq}\n"
            f"  Scor: {last_pct}%\n\n"
            f"Scor mediu total: {avg_pct:.1f}%"
        )

        messagebox.showinfo("Statistici", text)

    # -------------------------------------------------
    # UI LAYOUT
    # -------------------------------------------------
    def build_main_ui(self):
        """
        Construiește panoul principal:
        - Setări sesiune (domeniu, nr întrebări, mod TRAIN/EXAM, timp)
        - Secțiunea Rapoarte & Analiză (grafic, pdf, statistici)
        """

        # ====== top frame mare ======
        main_frame = ttk.Frame(self, style="Dark.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ------------------
        # Titlu mare
        # ------------------
        header = ttk.Label(
            main_frame,
            text="Setări sesiune",
            style="Header.TLabel"
        )
        header.pack(pady=(0, 15))

        # ------------------
        # GRID cu setări
        # ------------------
        settings_frame = ttk.Frame(main_frame, style="Card.TFrame")
        settings_frame.pack(pady=5)

        # Domeniu
        ttk.Label(
            settings_frame,
            text="Domeniu:",
            style="TLabel"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)

        domain_cb = ttk.Combobox(
            settings_frame,
            textvariable=self.domain_var,
            values=[
                "structural",
                "crash",
                "moldflow",
                "cfd",
                "nvh"
            ],
            font=("Segoe UI", 10),
            state="readonly",
            width=20
        )
        domain_cb.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Numar intrebari
        ttk.Label(
            settings_frame,
            text="Număr întrebări:",
            style="TLabel"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

        spin_q = tk.Spinbox(
            settings_frame,
            from_=1, to=20,
            textvariable=self.num_questions_var,
            font=("Segoe UI", 10),
            width=5,
            bg="#222",
            fg="white",
            insertbackground="white",
            highlightbackground="#00FFFF",
            relief="flat"
        )
        spin_q.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Mod (TRAIN / EXAM)
        ttk.Label(
            settings_frame,
            text="Mod:",
            style="TLabel"
        ).grid(row=2, column=0, sticky="ne", padx=5, pady=5)

        mode_frame = ttk.Frame(settings_frame, style="Card.TFrame")
        mode_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        rb_train = tk.Radiobutton(
            mode_frame,
            text="TRAIN (feedback imediat)",
            variable=self.mode_var,
            value="TRAIN",
            bg="#111",
            fg="white",
            activebackground="#111",
            activeforeground="#00FFFF",
            selectcolor="#111",
            font=("Segoe UI", 10),
            anchor="w"
        )
        rb_train.pack(anchor="w", pady=2)

        rb_exam = tk.Radiobutton(
            mode_frame,
            text="EXAM (limită timp, feedback final)",
            variable=self.mode_var,
            value="EXAM",
            bg="#111",
            fg="white",
            activebackground="#111",
            activeforeground="#00FFFF",
            selectcolor="#111",
            font=("Segoe UI", 10),
            anchor="w"
        )
        rb_exam.pack(anchor="w", pady=2)

        # timp per întrebare (EXAM)
        ttk.Label(
            settings_frame,
            text="Timp pe întrebare (secunde, doar EXAM):",
            style="TLabel"
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)

        spin_t = tk.Spinbox(
            settings_frame,
            from_=5, to=120,
            textvariable=self.time_limit_var,
            font=("Segoe UI", 10),
            width=5,
            bg="#222",
            fg="white",
            insertbackground="white",
            highlightbackground="#00FFFF",
            relief="flat"
        )
        spin_t.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # buton START QUIZ
        start_btn = ttk.Button(
            settings_frame,
            text="▶ Start Quiz",
            command=self.start_quiz
        )
        start_btn.grid(
            row=4, column=0,
            columnspan=2,
            pady=(15, 5)
        )

        # separatoare vizuale
        sep = tk.Frame(
            main_frame,
            bg="#00FFFF",
            height=2
        )
        sep.pack(fill="x", pady=20)

        # ------------------
        # Rapoarte & Analiză
        # ------------------
        reports_frame = ttk.Frame(main_frame, style="Card.TFrame")
        reports_frame.pack(pady=5)

        ttk.Label(
            reports_frame,
            text="Rapoarte & Analiză",
            style="SectionTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # buton grafic progres
        btn_chart = ttk.Button(
            reports_frame,
            text="📊 Grafic progres",
            command=self.on_progress_chart
        )
        btn_chart.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # buton generează PDF
        btn_pdf = ttk.Button(
            reports_frame,
            text="📄 Generează PDF",
            command=self.on_generate_pdf
        )
        btn_pdf.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # buton statistici
        btn_stats = ttk.Button(
            reports_frame,
            text="📈 Statistici",
            command=self.on_show_stats
        )
        btn_stats.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # make columns expand evenly
        reports_frame.columnconfigure(0, weight=1)
        reports_frame.columnconfigure(1, weight=1)


# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    app = FEAGui()
    app.mainloop()
