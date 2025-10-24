from data_loader import load_questions
from quiz_logic import run_quiz

def main():
    print("=== FEA QUIZ ===")
    print("Test de cunoștințe FEA / Crash / CAE")
    print("Răspunde sincer 😏")
    print()

    questions = load_questions()
    score, asked = run_quiz(questions, num_questions=10)

    print("=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}")
    pct = (score / asked) * 100 if asked > 0 else 0
    print(f"Asta înseamnă {pct:.1f}% corect.")
    print()

    if pct >= 80:
        print("Bravo, ești pe drumul bun pentru un interviu CAE junior 👌")
    elif pct >= 50:
        print("E ok, dar mai lucrează la concepte de bază (elemente, BC, contact).")
        print("Reia zonele slabe și rulează din nou quiz-ul.")
    else:
        print("Nu-i panică. Reia noțiunile de bază FEA și crash. Asta se învață 💪")

if __name__ == "__main__":
    main()
