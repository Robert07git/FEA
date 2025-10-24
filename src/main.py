from data_loader import load_questions
from quiz_logic import run_quiz
from datetime import datetime
import os

DOMENII = {
    "1": "structural",
    "2": "crash",
    "3": "moldflow",
    "4": "cfd",
    "5": "nvh",
    "6": "mix"
}

def alege_domeniu():
    print("=== FEA QUIZ ===")
    print("Alege domeniul pe care vrei să te testezi:")
    print("  1 - Simulare structurală (tensiuni, mesh, BC)")
    print("  2 - Crash / impact / energie absorbită")
    print("  3 - Moldflow (injecție plastic, shrinkage, warpage)")
    print("  4 - CFD (aerodinamică, curgere, presiune)")
    print("  5 - NVH (zgomot, vibrații, confort)")
    print("  6 - MIX (toate domeniile amestecate)")
    print()

    alegere = input("Introdu numărul domeniului (1-6): ").strip()

    # fallback: dacă bagi aiurea, alegem 'mix'
    domeniu = DOMENII.get(alegere, "mix")
    print(f"\nAi ales domeniul: {domeniu.upper()}.\n")
    return domeniu


def salveaza_scor(domeniu, score, asked, pct):
    """
    Salvează rezultatul într-un fișier text numit score_history.txt
    Format linie:
    2025-10-24 20:13 | domeniu=crash | scor=8/10 | procent=80.0%
    """
    # baza proiectului = folderul părinte al lui src
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"{timestamp} | domeniu={domeniu} | scor={score}/{asked} | procent={pct:.1f}%\n"

    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        # nu blocăm aplicația dacă nu putem scrie, doar informăm
        print(f"[Avertisment] Nu am putut salva scorul în score_history.txt: {e}")


def main():
    domeniu_selectat = alege_domeniu()

    # încărcăm întrebările filtrate pe domeniul ales
    questions = load_questions(domain=domeniu_selectat)

    # stabilim câte întrebări punem în sesiune
    num_q = 10
    if len(questions) < num_q:
        num_q = len(questions)

    score, asked = run_quiz(questions, num_questions=num_q)

    print("=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}")
    pct = (score / asked) * 100 if asked > 0 else 0
    print(f"Asta înseamnă {pct:.1f}% corect.")
    print()

    # feedback verbal
    if pct >= 80:
        print("Bravo, ești pe drumul bun pentru un interviu CAE junior 👌")
    elif pct >= 50:
        print("E ok, dar mai lucrează la conceptele mai slabe din domeniul ales.")
        print("Reia întrebările și rulează din nou quiz-ul.")
    else:
        print("Nu-i panică. Reia teoria de bază. Asta se învață 💪")

    # salvăm scorul în istoric
    salveaza_scor(domeniu_selectat, score, asked, pct)
    print("\nRezultatul a fost salvat în score_history.txt ✅")


if __name__ == "__main__":
    main()
