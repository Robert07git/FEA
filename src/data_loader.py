import json
import os

def load_questions(json_path=None):
    """
    Încarcă întrebările din fișierul JSON.
    Returnează o listă de dict-uri, fiecare dict = 1 întrebare.
    """
    if json_path is None:
        # cale implicită: ../data/fea_questions.json față de acest fișier
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "fea_questions.json")

    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    return questions
