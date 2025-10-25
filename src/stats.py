import tkinter as tk
from tkinter import ttk, messagebox
import os

def show_stats():
    file_path = os.path.join(os.path.dirname(__file__), "score_history.txt")
    if not os.path.exists(file_path):
        messagebox.showinfo("Statistici", "Nu există date salvate despre sesiuni anterioare.")
        return

    win = tk.Toplevel()
    win.title("Statistici generale")
    win.geometry("600x400")
    win.configure(bg="#111")

    tk.Label(win, text="📊 Rezumat sesiuni anterioare", font=("Segoe UI", 14, "bold"), bg="#111", fg="#00FFFF").pack(pady=10)

    tree = ttk.Treeview(win, columns=("Domeniu", "Mod", "Întrebări", "Scor (%)"), show="headings")
    for c in ("Domeniu", "Mod", "Întrebări", "Scor (%)"):
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=120)
    tree.pack(expand=True, fill="both", padx=20, pady=10)

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                domain, mode, total, score = line.strip().split(",")
                tree.insert("", "end", values=(domain, mode, total, score))
            except:
                continue

    tk.Button(win, text="Închide", command=win.destroy, bg="#00FFFF", fg="black").pack(pady=10)
