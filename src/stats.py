import os
import tkinter as tk
from tkinter import ttk

def show_dashboard():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hist_path = os.path.join(base_dir, "score_history.txt")
    if not os.path.exists(hist_path):
        raise FileNotFoundError("Nu există score_history.txt – rulează câteva quiz-uri înainte.")

    data = []
    with open(hist_path, "r", encoding="utf-8") as f:
        for line in f:
            p = [x.strip() for x in line.split("|")]
            if len(p) >= 5:
                data.append(p)

    win = tk.Toplevel()
    win.title("Statistici Performanță")
    win.geometry("650x400")
    tree = ttk.Treeview(win, columns=("Domeniu", "Mod", "Scor", "Procent"), show="headings")
    tree.heading("Domeniu", text="Domeniu")
    tree.heading("Mod", text="Mod")
    tree.heading("Scor", text="Scor")
    tree.heading("Procent", text="Procent (%)")

    for entry in data[-10:]:
        dom = entry[1].split("=")[1]
        mod = entry[2].split("=")[1]
        scor = entry[3].split("=")[1]
        pct = entry[4].split("=")[1]
        tree.insert("", "end", values=(dom, mod, scor, pct))

    tree.pack(fill="both", expand=True, padx=10, pady=10)
