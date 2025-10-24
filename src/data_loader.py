import json
import os

def load_questions(json_path=None, domain=None):
    """
    Încarcă întrebările din fișierul JSON și (opțional) filtrează după domeniu.

    Parametri:
    - json_path: cale custom către fișierul .json (de obicei nu ai nevoie să setezi)
    - domain: "structural", "crash", "moldflow", "cfd", "nvh", "mix" sau None

    Returnează:
    - listă de dict-uri cu întrebări
    """

    # dacă nu primim cale, construim automat data/fea_questions.json
    if json_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "fea_questions.json")

    # citim toate întrebările din fișier
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # dacă nu vrem filtrare sau vrem "mix", întoarcem toate
    if domain is None or domain.lower() == "mix":
        return questions

    # altfel filtrăm întrebările doar pe domeniul ales
    filtered = [q for q in questions if q.get("domain", "").lower() == domain.lower()]

    # dacă nu găsim nimic pe domeniul cerut (greșeală de input),
    # ca fallback dăm toate întrebările
    if not filtered:
        return questions

    return filtered
