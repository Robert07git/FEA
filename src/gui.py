import tkinter as tk
from tkinter import ttk
import os

# Această funcție se integrează cu GUI-ul principal (FEAQuizApp)
def show_stats():
    # Verifică dacă există fișierul cu istoricul scorurilor
    history_file = os.path.join(os.path.dirname(__file__), "score_history.txt")
    if not os.path.exists(history_file):
        tk.messagebox.showinfo("Statistici", "Nu există date salvate despre sesiuni anterioare.")
        return

    # Creează o fereastră separată
    stats_win = tk.Toplevel()
    stats_win.title("Statistici generale")
    stats_win.geometry("600x400")
    stats_win.configure(bg="#111")

    title = tk.Label(
        stats_win,
        text="📊 Rezumat sesiuni anterioare",
        font=("Segoe UI", 14, "bold"),
        fg="#00FFFF",
        bg="#111",
    )
    title.pack(pady=10)

    # Creează un Treeview pentru a afișa datele
    tree = ttk.Treeview(stats_win, columns=("Domeniu", "Mod", "Întrebări", "Scor"), show="headings")
    tree.heading("Domeniu", text="Domeniu")
    tree.heading("Mod", text="Mod")
    tree.heading("Întrebări", text="Întrebări totale")
    tree.heading("Scor", text="Scor (%)")
    tree.pack(expand=True, fill="both", padx=20, pady=10)

    # Încarcă datele din fișier
    with open(history_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        try:
            domain, mode, total, score = line.strip().split(",")
            tree.insert("", "end", values=(domain, mode, total, score))
        except ValueError:
            continue

    # Buton de închidere
    close_btn = tk.Button(
        stats_win,
        text="Închide",
        command=stats_win.destroy,
        bg="#00FFFF",
        fg="black",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=10,
        pady=5,
    )
    close_btn.pack(pady=10)
