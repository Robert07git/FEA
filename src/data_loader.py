import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
QUESTIONS_FILE = os.path.join(DATA_DIR, "fea_questions.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")


# ===================== ÎNCĂRCARE ÎNTREBĂRI =====================
def load_questions(domain=None):
    """
    Încarcă întrebările din fișierul JSON.
    Dacă se specifică un domeniu, returnează doar întrebările acelui domeniu.
    """
    if not os.path.exists(QUESTIONS_FILE):
        print(f"[Eroare] Fișierul {QUESTIONS_FILE} nu există.")
        return []

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if domain and domain.lower() != "mix":
            return [q for q in data if q.get("domain", "").lower() == domain.lower()]
        else:
            return data  # toate întrebările pentru modul MIX
    except Exception as e:
        print(f"[Eroare la citirea fișierului de întrebări]: {e}")
        return []


# ===================== DOMENII DISPONIBILE =====================
def get_domains():
    """Returnează lista de domenii disponibile pe baza întrebărilor din fișier."""
    if not os.path.exists(QUESTIONS_FILE):
        return []

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        domains = sorted(set(q.get("domain", "necunoscut").lower() for q in data))
        if "mix" not in domains:
            domains.append("mix")
        return domains
    except Exception as e:
        print(f"[Eroare la obținerea domeniilor]: {e}")
        return []


# ===================== SALVARE REZULTAT =====================
def save_result(result):
    """
    Salvează rezultatul unui test în fișierul JSON.
    Atributele sunt: mod, domeniu, scor, total, procent, timp_total, timp_intrebare.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)

    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            results = json.load(f)
    except json.JSONDecodeError:
        results = []

    result_entry = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mod": result.get("mod", "necunoscut"),
        "domeniu": result.get("domeniu", "necunoscut"),
        "scor": result.get("scor", 0),
        "total": result.get("total", 0),
        "procent": round(result.get("procent", 0), 2),
        "timp_total": result.get("timp_total", "n/a"),
        "timp_intrebare": result.get("timp_intrebare", "n/a")
    }

    results.append(result_entry)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


# ===================== CITIRE ISTORIC =====================
def load_results():
    """Returnează lista tuturor rezultatelor salvate."""
    if not os.path.exists(RESULTS_FILE):
        return []
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Eroare la citirea rezultatelor]: {e}")
        return []
# ===================== LEARN MODE: MATERIALE =====================
def load_learning_materials():
    """
    Încarcă materialele de învățare pentru Learn Mode din data/docs/.
    Returnează un dicționar cu domeniile și materialele aferente.
    """
    docs_dir = os.path.join(DATA_DIR, "docs")
    materials = {}

    if not os.path.exists(docs_dir):
        print(f"[Avertisment] Folderul {docs_dir} nu există.")
        return materials

    try:
        for file in os.listdir(docs_dir):
            if file.endswith(".json"):
                domain = file.replace(".json", "")
                file_path = os.path.join(docs_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    materials[domain] = json.load(f)
        print(f"[INFO] Încărcate materiale pentru {len(materials)} domenii din docs/.")
    except Exception as e:
        print(f"[Eroare la încărcarea materialelor]: {e}")

    return materials
