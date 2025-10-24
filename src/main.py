from data_loader import load_questions
from quiz_logic import run_quiz

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

    # dacă userul bagă ceva aiurea, punem mix by default
    domeniu = DOMENII.get(alegere, "mix")
    print(f"\nAi ales domeniul: {domeniu.upper()}.\n")
    return domeniu

def main():
    domeniu_selectat = alege_domeniu()

    # încărcăm întrebările filtrate pe domeniul ales
    questions = load_questions(domain=domeniu_selectat)

    # câte întrebări să punem într-un quiz
    # dacă domeniul are mai puțin de 10 întrebări disponibile,
    # folosim tot ce avem
    num_q = 10
    if len(questions) < num_q:
        num_q = len(questions)

    score, asked = run_quiz(questions, num_questions=num_q)

    print("=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}")
    pct = (score / asked) * 100 if asked > 0 else 0
    print(f"Asta înseamnă {pct:.1f}% corect.")
    print()

    if pct >= 80:
        print("Bravo, ești pe drumul bun pentru un interviu CAE junior 👌")
    elif pct >= 50:
        print("E ok, dar mai lucrează la concepte slabe din domeniul ales.")
        print("Reia întrebările și rulează din nou quiz-ul.")
    else:
        print("Nu-i panică. Reia teoria de bază. Asta se învață 💪")

if __name__ == "__main__":
    main()
