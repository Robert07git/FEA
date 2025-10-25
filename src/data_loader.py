import json
import os
from tkinter import messagebox


def load_questions(domain="mix"):
    """
    Încarcă întrebările din fișierul data/fea_questions.json.
    Dacă domeniul = "mix", le combină pe toate.
    Returnează o listă de întrebări validate.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "fea_questions.json")

    if not os.path.exists(data_path):
        messagebox.showerror("Eroare", f"Fișierul {os.path.basename(data_path)} nu a fost găsit!")
        return []

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        messagebox.showerror("Eroare JSON", f"Format invalid în {data_path}.\n{e}")
        return []

    # Verificăm dacă fișierul conține domenii valide
    if not isinstance(data, dict):
        messagebox.showerror("Eroare", "Fișierul JSON nu are structură validă (dict pe domenii).")
        return []

    all_questions = []

    if domain.lower() == "mix":
        for domeniu, lista in data.items():
            all_questions.extend(validate_questions(lista, domeniu))
    else:
        domeniu = domain.lower()
        if domeniu in data:
            all_questions = validate_questions(data[domeniu], domeniu)
        else:
            messagebox.showwarning("Avertisment", f"Domeniul '{domeniu}' nu a fost găsit în fișierul JSON.")
            return []

    if not all_questions:
        messagebox.showwarning("Avertisment", "Nu există întrebări valide în fișierul JSON pentru acest domeniu.")
        return []

    return all_questions


def validate_questions(questions, domain_name):
    """
    Verifică și structurează întrebările.
    """
    valid = []
    for q in questions:
        if not all(k in q for k in ("question", "options", "correct")):
            continue
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            continue
        try:
            correct_index = int(q["correct"])
        except ValueError:
            continue

        q_struct = {
            "domain": domain_name,
            "question": q["question"].strip(),
            "options": q["options"],
            "correct": correct_index,
            "explanation": q.get("explanation", "")
        }
        valid.append(q_struct)
    return valid
