import os
import tkinter as tk
from tkinter import ttk, messagebox
import statistics


def show_dashboard():
    """Afișează statistici generale din score_history.txt"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        messagebox.showwarning("Lipsă date", "Nu există fișierul score_history.txt. Fă cel puțin un quiz.")
        return

    try:
        results = []
        with open(history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "scor=" not in line:
                    continue

                try:
                    parts = [p.strip() for p in line.split("|")]
                    domeniu = parts[1].split("=")[-1].strip()
                    mod = parts[2].split("=")[-1].strip().upper()
                    scor = parts[3].split("=")[-1].split("/")[0].strip()
                    total = parts[3].split("/")[-1].split()[0].strip()
                    procent = parts[4].split("=")[-1].replace("%", "").strip()

                    results.append({
                        "domeniu": domeniu,
                        "mod": mod,
                        "scor": int(scor),
                        "total": int(total),
                        "procent": float(procent)
                    })
                except:
                    continue

        if not results:
            messagebox.showinfo("Info", "Nu există înregistrări valide în score_history.txt.")
            return

        # ==========================
        #  Creare fereastră Stats
        # ==========================
        win = tk.Toplevel()
        win.title("Statistici generale - FEA Quiz Trainer")
        win.geometry("650x500")
        win.configure(bg="#111")

        title = tk.Label(win, text="📊 Statistici generale", font=("Arial", 18, "bold"),
                         bg="#111", fg="#00ffff")
        title.pack(pady=10)

        # Statistici generale
        medie_totala = statistics.mean(r["procent"] for r in results)
        nr_teste = len(results)

        lbl_sumar = tk.Label(win,
            text=f"Total sesiuni: {nr_teste}\nMedia generală: {medie_totala:.1f}%",
            font=("Arial", 12), bg="#111", fg="white")
        lbl_sumar.pack(pady=10)

        # ==========================
        #  Medii pe domenii
        # ==========================
        domenii = {}
        for r in results:
            domenii.setdefault(r["domeniu"], []).append(r["procent"])

        tk.Label(win, text="Medii pe domenii:", font=("Arial", 12, "bold"),
                 bg="#111", fg="#00ffff").pack()

        frame_dom = tk.Frame(win, bg="#111")
        frame_dom.pack(pady=5)

        for dom, valori in domenii.items():
            medie = statistics.mean(valori)
            tk.Label(frame_dom, text=f"{dom.upper():<12} → {medie:.1f}%",
                     font=("Consolas", 11), bg="#111", fg="white", anchor="w").pack()

        # ==========================
        #  Medii pe mod (TRAIN / EXAM)
        # ==========================
        moduri = {}
        for r in results:
            moduri.setdefault(r["mod"], []).append(r["procent"])

        tk.Label(win, text="\nMedii pe mod:", font=("Arial", 12, "bold"),
                 bg="#111", fg="#00ffff").pack()

        frame_mod = tk.Frame(win, bg="#111")
        frame_mod.pack(pady=5)

        for mod, valori in moduri.items():
            medie = statistics.mean(valori)
            tk.Label(frame_mod, text=f"{mod:<6} → {medie:.1f}%",
                     font=("Consolas", 11), bg="#111", fg="white", anchor="w").pack()

        # ==========================
        #  Tabel detaliat
        # ==========================
        tk.Label(win, text="\nRezultate recente:", font=("Arial", 12, "bold"),
                 bg="#111", fg="#00ffff").pack()

        table = ttk.Treeview(win, columns=("Domeniu", "Mod", "Scor", "Procent"), show="headings", height=10)
        table.pack(pady=10)

        table.heading("Domeniu", text="Domeniu")
        table.heading("Mod", text="Mod")
        table.heading("Scor", text="Scor")
        table.heading("Procent", text="Procent (%)")

        table.column("Domeniu", anchor="center", width=150)
        table.column("Mod", anchor="center", width=80)
        table.column("Scor", anchor="center", width=100)
        table.column("Procent", anchor="center", width=100)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#222", foreground="white",
                        fieldbackground="#222", rowheight=25, font=("Arial", 10))
        style.configure("Treeview.Heading",
                        background="#00aaaa", foreground="black", font=("Arial", 10, "bold"))

        # adăugare ultimele 15 rezultate
        for r in results[-15:][::-1]:
            table.insert("", "end", values=(r["domeniu"], r["mod"], f"{r['scor']}/{r['total']}", f"{r['procent']:.1f}"))

    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o eroare la încărcarea statisticilor:\n{e}")
