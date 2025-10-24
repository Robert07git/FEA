import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

# importăm logica noastră existentă
from data_loader import load_questions
from stats import show_dashboard  # pentru progres text

# Căi utile
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS_IMG_PATH = os.path.join(BASE_DIR, "progress_chart.png")
PDF_EXPORT_SCRIPT = os.path.join(BASE_DIR, "src", "export_pdf.py")
CHART_SCRIPT = os.path.join(BASE_DIR, "src", "progress_chart.py")

DOMENII_OPTIUNI = {
    "Structural (tensiuni / mesh / BC)": "structural",
    "Crash (impact / energie absorbită)": "crash",
    "Moldflow (injecție plastic)": "moldflow",
    "CFD (aerodinamică / curgere)": "cfd",
    "NVH (zgomot / vibrații / confort)": "nvh",
    "MIX (toate domeniile)": "mix",
}


class QuizWindow(tk.Toplevel):
    """
    Versiunea 2: rulăm quiz-ul direct în GUI, întrebare cu întrebare.
    Fără input() în consolă, fără thread blocant.
    """

    def __init__(self, master, domeniu, num_intrebari, mode, time_limit_sec):
        super().__init__(master)
        self.title("FEA Quiz - Sesiune Quiz")
        self.geometry("520x520")
        self.configure(bg="#111111")

        self.domeniu = domeniu
        self.num_intrebari = num_intrebari
        self.mode = mode  # "train" sau "exam"
        self.time_limit_sec = time_limit_sec  # TODO: timer vizual în versiunea următoare

        # 1. încărcăm întrebările
        all_q = load_questions(domain=self.domeniu)
        if len(all_q) == 0:
            # fallback la mix
            all_q = load_questions(domain="mix")

        # tăiem la numărul cerut (notă: în viitor putem randomiza)
        self.questions = all_q[: self.num_intrebari]

        # 2. state joc
        self.current_index = 0          # întrebarea curentă
        self.correct_count = 0          # câte ai nimerit corect
        self.asked_count = 0            # câte au fost puse
        self.gresite = []               # pt review la EXAM (sau studiu ulterior)

        # 3. UI ELEMENTS

        # header cu domeniu și mod
        self.lbl_header = tk.Label(
            self,
            text=f"Domeniu: {self.domeniu} | Mod: {self.mode.upper()}",
            fg="#00D4FF",
            bg="#111111",
            font=("Segoe UI", 10, "bold"),
            wraplength=480,
            justify="left"
        )
        self.lbl_header.pack(pady=(15,5))

        # întrebare
        self.lbl_question = tk.Label(
            self,
            text="Întrebare aici...",
            fg="#FFFFFF",
            bg="#111111",
            font=("Segoe UI", 10, "bold"),
            wraplength=480,
            justify="left"
        )
        self.lbl_question.pack(pady=(10,5))

        # zona cu variante
        self.answer_var = tk.IntVar(value=-1)
        self.frame_choices = tk.Frame(self, bg="#111111")
        self.frame_choices.pack(pady=(5,10), fill="x")

        self.choice_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(
                self.frame_choices,
                text=f"Varianta {i+1}",
                variable=self.answer_var,
                value=i,
                bg="#111111",
                fg="#FFFFFF",
                activebackground="#111111",
                activeforeground="#00D4FF",
                selectcolor="#1F1F1F",
                wraplength=460,
                justify="left",
                anchor="w"
            )
            rb.pack(anchor="w", pady=2)
            self.choice_buttons.append(rb)

        # feedback pentru TRAIN (sau mesaj de confirmare pentru EXAM)
        self.lbl_feedback = tk.Label(
            self,
            text="",
            fg="#AAAAAA",
            bg="#111111",
            font=("Segoe UI", 9),
            wraplength=480,
            justify="left"
        )
        self.lbl_feedback.pack(pady=(5,10))

        # butonul principal (next / submit)
        self.btn_next = tk.Button(
            self,
            text="Răspunde / Următoarea",
            command=self.on_submit_answer,
            bg="#00D4FF",
            fg="#000000",
            activebackground="#00AACC",
            activeforeground="#000000",
            relief="flat",
            padx=12,
            pady=8,
            font=("Segoe UI", 10, "bold")
        )
        self.btn_next.pack(pady=(10,10))

        # buton închidere fereastră
        self.btn_close = tk.Button(
            self,
            text="Închide",
            command=self.destroy,
            bg="#333333",
            fg="#FFFFFF",
            activebackground="#444444",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=12,
            pady=8
        )
        self.btn_close.pack(pady=(0,20))

        # 4. afișăm prima întrebare
        self.show_current_question()

    def show_current_question(self):
        """Afișează întrebarea curentă și cele 4 opțiuni de răspuns în UI."""
        if self.current_index >= len(self.questions):
            # gata testul
            self.end_quiz()
            return

        qdata = self.questions[self.current_index]
        q_text = qdata["question"]
        choices = qdata["choices"]

        # întrebarea
        self.lbl_question.config(
            text=f"Q{self.current_index+1}: {q_text}"
        )

        # resetăm selecția
        self.answer_var.set(-1)

        # actualizăm opțiunile
        for i, rb in enumerate(self.choice_buttons):
            if i < len(choices):
                rb.config(text=f"{i+1}. {choices[i]}", state="normal")
            else:
                rb.config(text=f"{i+1}. -", state="disabled")

        # ștergem feedback-ul anterior
        self.lbl_feedback.config(text="")

        # schimbăm butonul pentru starea curentă
        if self.current_index == len(self.questions) - 1:
            # ultima întrebare
            self.btn_next.config(text="Finalizare / Scor")
        else:
            self.btn_next.config(text="Răspunde / Următoarea")

    def on_submit_answer(self):
        """User apasă pe 'Răspunde / Următoarea'."""
        if self.current_index >= len(self.questions):
            # dacă deja am terminat, doar afișăm scorul
            self.end_quiz()
            return

        qdata = self.questions[self.current_index]
        correct_idx = qdata["correct_index"]
        explanation = qdata["explanation"]
        domeniu_q = qdata.get("domain", self.domeniu)

        selected = self.answer_var.get()

        # am pus întrebarea -> creștem asked_count
        self.asked_count += 1

        corect = (selected == correct_idx)
        if corect:
            self.correct_count += 1
        else:
            # salvăm pt revizuire / EXAM feedback
            self.gresite.append({
                "idx": self.current_index+1,
                "domain": domeniu_q,
                "question": qdata["question"],
                "choices": qdata["choices"],
                "correct_index": qdata["correct_index"],
                "explanation": qdata["explanation"]
            })

        # în mod TRAIN: arătăm imediat dacă e corect + explicația
        if self.mode == "train":
            if corect:
                fb = "Corect ✅\n"
            else:
                fb = "Greșit ❌\n"
                fb += (
                    f"Răspuns corect: {correct_idx+1}. "
                    f"{qdata['choices'][correct_idx]}\n"
                )
            fb += f"Explicație: {explanation}"
            self.lbl_feedback.config(text=fb)
        else:
            # EXAM: nu arătăm explicația acum
            self.lbl_feedback.config(text="Răspuns înregistrat.")

        # mergem la următoarea întrebare
        self.current_index += 1

        # dacă am terminat întrebările -> afișăm scorul final
        if self.current_index >= len(self.questions):
            self.end_quiz()
        else:
            # altfel afișăm următoarea întrebare
            self.show_current_question()

    def end_quiz(self):
        """Afișează scorul final + revizuire (dacă e EXAM)."""
        if self.asked_count == 0:
            pct = 0.0
        else:
            pct = (self.correct_count / self.asked_count) * 100.0

        if pct >= 80:
            feedback = "Bravo, ești pe drumul bun pentru un interviu CAE junior 👌"
        elif pct >= 50:
            feedback = "E ok, dar mai lucrează la conceptele mai slabe din domeniul ales."
        else:
            feedback = "Nu-i panică. Reia teoria de bază. Asta se învață 💪"

        summary_lines = []
        summary_lines.append("=== REZULTAT FINAL ===")
        summary_lines.append(f"Scor: {self.correct_count}/{self.asked_count}")
        summary_lines.append(f"Procent: {pct:.1f}%")
        summary_lines.append(f"Mod: {self.mode.upper()}")
        summary_lines.append("")
        summary_lines.append(feedback)

        # dacă suntem în exam, afișăm întrebările pentru revizuit
        if self.mode == "exam" and self.gresite:
            summary_lines.append("")
            summary_lines.append("Întrebări pentru revizuit:")
            for r in self.gresite:
                good = r["choices"][r["correct_index"]]
                summary_lines.append(f"- Q{r['idx']} ({r['domain']}) -> {r['question']}")
                summary_lines.append(f"  Răspuns corect: {good}")
                summary_lines.append(f"  Explicație: {r['explanation']}")
                summary_lines.append("")

        final_text = "\n".join(summary_lines)

        # Afișăm rezultatul în locul întrebării
        self.lbl_question.config(text=final_text)

        # Dezactivăm opțiunile de răspuns
        for rb in self.choice_buttons:
            rb.config(state="disabled")

        # curățăm feedback
        self.lbl_feedback.config(text="")

        # dezactivăm butonul Next
        self.btn_next.config(state="disabled")
        # la final utilizatorul poate apăsa "Închide"


class MainWindow(tk.Tk):
    """
    Fereastra principală a aplicației GUI.
    Te lasă să:
    - alegi domeniu
    - alegi nr. întrebări
    - alegi TRAIN vs EXAM
    - setezi timpul pe întrebare (în viitor pt timer)
    - rulezi quiz-ul (deschide QuizWindow)
    - generezi PDF din ultimul EXAM
    - generezi grafic de progres
    - vezi progres text (stats)
    """

    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("900x600")
        self.configure(bg="#0F0F0F")

        label_style = {"bg": "#0F0F0F", "fg": "#FFFFFF", "font": ("Segoe UI", 10, "bold")}
        field_style = {
            "bg": "#1F1F1F",
            "fg": "#FFFFFF",
            "insertbackground": "#FFFFFF",
            "relief": "flat"
        }

        section_title = tk.Label(
            self,
            text="Setări sesiune",
            bg="#0F0F0F",
            fg="#00D4FF",
            font=("Segoe UI", 12, "bold")
        )
        section_title.pack(pady=(20,10))

        # Domeniu
        tk.Label(self, text="Domeniu:", **label_style).pack(anchor="w", padx=30)
        self.combo_domain = ttk.Combobox(
            self,
            values=list(DOMENII_OPTIUNI.keys()),
            state="readonly"
        )
        self.combo_domain.current(0)
        self.combo_domain.pack(padx=30, fill="x", pady=(0,10))

        # Nr întrebări
        tk.Label(self, text="Număr întrebări:", **label_style).pack(anchor="w", padx=30)
        self.entry_numq = tk.Entry(self, **field_style)
        self.entry_numq.insert(0, "5")
        self.entry_numq.pack(padx=30, fill="x", pady=(0,10))

        # Mod (TRAIN / EXAM)
        tk.Label(self, text="Mod:", **label_style).pack(anchor="w", padx=30)
        self.mode_var = tk.StringVar(value="train")
        frame_modes = tk.Frame(self, bg="#0F0F0F")
        frame_modes.pack(anchor="w", padx=30, pady=(0,10))

        rb_train = tk.Radiobutton(
            frame_modes,
            text="TRAIN (fără limită timp, feedback imediat)",
            variable=self.mode_var,
            value="train",
            bg="#0F0F0F",
            fg="#FFFFFF",
            activebackground="#0F0F0F",
            activeforeground="#00D4FF",
            selectcolor="#1F1F1F"
        )
        rb_train.pack(anchor="w")

        rb_exam = tk.Radiobutton(
            frame_modes,
            text="EXAM (limită timp, review la final)",
            variable=self.mode_var,
            value="exam",
            bg="#0F0F0F",
            fg="#FFFFFF",
            activebackground="#0F0F0F",
            activeforeground="#00D4FF",
            selectcolor="#1F1F1F"
        )
        rb_exam.pack(anchor="w")

        # Timp per întrebare
        tk.Label(
            self,
            text="Timp pe întrebare (secunde, doar EXAM):",
            **label_style
        ).pack(anchor="w", padx=30)
        self.entry_time = tk.Entry(self, **field_style)
        self.entry_time.insert(0, "15")
        self.entry_time.pack(padx=30, fill="x", pady=(0,20))

        # Buton Start Quiz
        self.btn_start = tk.Button(
            self,
            text="Start Quiz",
            command=self.start_quiz_clicked,
            bg="#00D4FF",
            fg="#000000",
            activebackground="#00AACC",
            activeforeground="#000000",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=16,
            pady=10
        )
        self.btn_start.pack(padx=30, fill="x")

        # Linie separatoare
        tk.Label(
            self,
            text="Rapoarte & Analiză",
            bg="#0F0F0F",
            fg="#00D4FF",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(30,10))

        # Buton generare grafic progres
        self.btn_chart = tk.Button(
            self,
            text="Generează grafic progres (.png)",
            command=self.generate_chart,
            bg="#333333",
            fg="#FFFFFF",
            activebackground="#444444",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=10
        )
        self.btn_chart.pack(padx=30, fill="x", pady=(0,10))

        # Buton export PDF
        self.btn_pdf = tk.Button(
            self,
            text="Generează PDF din ultimul EXAM",
            command=self.generate_pdf,
            bg="#333333",
            fg="#FFFFFF",
            activebackground="#444444",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=10
        )
        self.btn_pdf.pack(padx=30, fill="x", pady=(0,10))

        # Buton progres text (stats)
        self.btn_stats = tk.Button(
            self,
            text="Arată progres text (stats)",
            command=self.show_stats_popup,
            bg="#333333",
            fg="#FFFFFF",
            activebackground="#444444",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=10
        )
        self.btn_stats.pack(padx=30, fill="x", pady=(0,30))

        # Footer
        tk.Label(
            self,
            text="FEA Quiz Trainer v1 GUI",
            bg="#0F0F0F",
            fg="#777777",
            font=("Segoe UI", 8)
        ).pack(side="bottom", pady=10)

    def start_quiz_clicked(self):
        # citim opțiunile din UI
        domeniu_ui = self.combo_domain.get()
        domeniu_real = DOMENII_OPTIUNI.get(domeniu_ui, "mix")

        try:
            num_q = int(self.entry_numq.get().strip())
        except ValueError:
            messagebox.showerror("Eroare", "Număr întrebări invalid.")
            return

        mode = self.mode_var.get().strip()
        if mode not in ("train", "exam"):
            messagebox.showerror("Eroare", "Mod invalid.")
            return

        if mode == "exam":
            try:
                tsec = int(self.entry_time.get().strip())
                if tsec < 3:
                    messagebox.showerror("Eroare", "Timp prea mic (<3s).")
                    return
                if tsec > 120:
                    messagebox.showerror("Eroare", "Timp prea mare (>120s).")
                    return
            except ValueError:
                messagebox.showerror("Eroare", "Timpul per întrebare trebuie să fie număr.")
                return
        else:
            tsec = None

        # deschidem o fereastră nouă care rulează quiz-ul în GUI
        QuizWindow(
            master=self,
            domeniu=domeniu_real,
            num_intrebari=num_q,
            mode=mode,
            time_limit_sec=tsec
        )

    def generate_chart(self):
        # rulăm progress_chart.py ca script separat
        try:
            result = subprocess.run(
                ["python", CHART_SCRIPT],
                check=True,
                capture_output=True,
                text=True
            )
            # după generare, verificăm dacă există imaginea
            if os.path.exists(PROGRESS_IMG_PATH):
                messagebox.showinfo(
                    "Grafic generat",
                    f"Graficul a fost salvat ca:\n{PROGRESS_IMG_PATH}\n\nPoți deschide PNG-ul să vezi trendul scorurilor tale."
                )
            else:
                messagebox.showwarning(
                    "Atenție",
                    "Scriptul a rulat, dar nu am găsit progress_chart.png."
                )
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Eroare la grafic", e.stderr or str(e))

    def generate_pdf(self):
        # rulăm export_pdf.py ca script separat
        try:
            result = subprocess.run(
                ["python", PDF_EXPORT_SCRIPT],
                check=True,
                capture_output=True,
                text=True
            )
            # outputul scriptului îl punem într-un popup
            messagebox.showinfo("Export PDF", result.stdout.strip())
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Eroare la PDF", e.stderr or str(e))

    def show_stats_popup(self):
        # capturăm outputul din show_dashboard() într-un popup
        import io
        import sys
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            show_dashboard()
        except Exception as e:
            buf.write(f"Eroare la stats: {e}")
        finally:
            sys.stdout = old_stdout

        content = buf.getvalue()

        win = tk.Toplevel(self)
        win.title("Progres personal (stats)")
        win.geometry("480x320")
        win.configure(bg="#111111")

        txt = tk.Text(
            win,
            bg="#1F1F1F",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            wrap="word",
            relief="flat"
        )
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("1.0", content)
        txt.config(state="disabled")


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
