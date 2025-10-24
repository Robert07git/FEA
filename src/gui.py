import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# importăm logica noastră existentă
from data_loader import load_questions
from quiz_logic import run_quiz
from stats import show_dashboard  # pentru progres text
import subprocess
import os

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
    Fereastra în care efectiv se rulează quiz-ul și se afișează scorul final.
    Pentru versiunea 1, rulăm quiz-ul în thread separat cu run_quiz și afișăm doar rezultatul final.

    Versiunea 2 o să facă întrebările interactive în GUI (una câte una).
    """

    def __init__(self, master, domeniu, num_intrebari, mode, time_limit_sec):
        super().__init__(master)
        self.title("FEA Quiz - Sesie Quiz")
        self.geometry("500x400")
        self.configure(bg="#111111")

        self.domeniu = domeniu
        self.num_intrebari = num_intrebari
        self.mode = mode
        self.time_limit_sec = time_limit_sec

        # UI simplu: status + rezultat + buton Close
        self.label_status = tk.Label(
            self,
            text="Rulez testul...",
            fg="#FFFFFF",
            bg="#111111",
            font=("Segoe UI", 12, "bold"),
            wraplength=460,
            justify="left"
        )
        self.label_status.pack(pady=20)

        self.label_result = tk.Label(
            self,
            text="",
            fg="#CCCCCC",
            bg="#111111",
            font=("Segoe UI", 10),
            wraplength=460,
            justify="left"
        )
        self.label_result.pack(pady=10)

        self.btn_close = tk.Button(
            self,
            text="Închide",
            command=self.destroy,
            bg="#333333",
            fg="#FFFFFF",
            activebackground="#444444",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=8
        )
        self.btn_close.pack(pady=20)

        # rulăm quiz-ul într-un thread separat ca să nu înghețe GUI-ul
        t = threading.Thread(target=self.run_quiz_and_show_result, daemon=True)
        t.start()

    def run_quiz_and_show_result(self):
        """
        Rulează run_quiz (din consola noastră logică) și apoi afișează scorul final în fereastră.
        Pentru moment, ne folosim de motorul existent, fără interacțiune grafică întrebare-cu-întrebare.

        În versiunea următoare putem controla 100% întrebările în UI (pas cu pas).
        """
        try:
            # încărcăm întrebările
            questions = load_questions(domain=self.domeniu)

            if len(questions) == 0:
                self.safe_set_text(self.label_status,
                    "Nu există întrebări pentru domeniul ales. Folosesc MIX.")
                questions = load_questions(domain="mix")

            # apelăm run_quiz
            start = time.time()
            score, asked, results = run_quiz(
                questions=questions,
                num_questions=self.num_intrebari,
                mode=self.mode,
                time_limit_sec=self.time_limit_sec
            )
            end = time.time()
            durata = end - start

            pct = (score / asked * 100.0) if asked else 0.0

            # feedback calitativ la final (reusăm aceeași logică ca în main.py)
            if pct >= 80:
                feedback = "Bravo, ești pe drumul bun pentru un interviu CAE junior 👌"
            elif pct >= 50:
                feedback = "E ok, dar mai lucrează la conceptele mai slabe din domeniul ales."
            else:
                feedback = "Nu-i panică. Reia teoria de bază. Asta se învață 💪"

            rezumat = []
            rezumat.append(f"Scor: {score}/{asked}")
            rezumat.append(f"Procent: {pct:.1f}%")
            rezumat.append(f"Timp total: {durata:.1f} sec (~{durata/60:.1f} min)")
            rezumat.append(f"Mod: {self.mode.upper()}")
            rezumat.append("")
            rezumat.append(feedback)

            # dacă am fost în modul EXAM, putem sumariza greșelile ca în consolă
            if self.mode == "exam":
                gresite = [r for r in results if not r["correct"]]
                if gresite:
                    rezumat.append("")
                    rezumat.append("Întrebări de revizuit:")
                    for r in gresite[:3]:  # primele 3 doar, ca să nu fie roman
                        rezumat.append(f"- Q{r['idx']} ({r['domain']})")

            self.safe_set_text(self.label_status, "Test finalizat ✅")
            self.safe_set_text(self.label_result, "\n".join(rezumat))

        except Exception as e:
            self.safe_set_text(self.label_status, "Eroare în rularea testului.")
            self.safe_set_text(self.label_result, str(e))

    def safe_set_text(self, widget, text):
        # ca să actualizăm UI din threadul worker în threadul principal Tk
        widget.after(0, lambda: widget.config(text=text))


class MainWindow(tk.Tk):
    """
    Fereastra principală a aplicației GUI.
    Te lasă să:
    - alegi domeniu
    - alegi nr. întrebări
    - alegi TRAIN vs EXAM
    - setezi timpul pe întrebare dacă e EXAM
    - rulezi quiz-ul (deschide QuizWindow)
    - generezi PDF din ultimul EXAM
    - generezi grafic de progres
    """

    def __init__(self):
        super().__init__()
        self.title("FEA Quiz Trainer")
        self.geometry("480x520")
        self.configure(bg="#0F0F0F")

        # stiluri simple
        label_style = {"bg": "#0F0F0F", "fg": "#FFFFFF", "font": ("Segoe UI", 10, "bold")}
        field_style = {"bg": "#1F1F1F", "fg": "#FFFFFF", "insertbackground": "#FFFFFF",
                       "relief": "flat"}

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
        tk.Label(self, text="Timp pe întrebare (secunde, doar EXAM):", **label_style).pack(anchor="w", padx=30)
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

        # timp per întrebare (doar dacă e EXAM)
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

        # deschidem o fereastră nouă care rulează quiz-ul în thread
        QuizWindow(
            master=self,
            domeniu=domeniu_real,
            num_intrebari=num_q,
            mode=mode,
            time_limit_sec=tsec
        )

    def generate_chart(self):
        # rulăm progres_chart.py ca script separat
        try:
            subprocess.run(
                ["python", CHART_SCRIPT],
                check=True,
                capture_output=True,
                text=True
            )
            # după generare, verificăm dacă există imaginea
            if os.path.exists(PROGRESS_IMG_PATH):
                messagebox.showinfo(
                    "Grafic generat",
                    f"Graficul a fost salvat ca:\n{PROGRESS_IMG_PATH}\n\nDeschide PNG-ul să vezi trendul scorurilor tale."
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
        # rulăm show_dashboard() și punem rezultatul într-o fereastră mică
        # (show_dashboard() scrie direct în consolă, deci îl capturăm într-un buffer)
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

        # popup text scrollabil
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
