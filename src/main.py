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
    domeniu = DOMENII.get(alegere, "mix")
    print(f"\nAi ales domeniul: {domeniu.upper()}.\n")
    return domeniu


def alege_numar_intrebari(max_intrebari, domeniu_curent):
    """
    Întreabă utilizatorul câte întrebări vrea, dar nu îl lasă să depășească
    numărul de întrebări disponibile pentru domeniul ales.
    """
    while True:
        try:
            num = int(input(
                f"Câte întrebări vrei să ai în test pentru domeniul '{domeniu_curent}'? (maxim {max_intrebari}) "
            ))
            if 1 <= num <= max_intrebari:
                return num
            else:
                print(f"Ai cerut {num}, dar domeniul '{domeniu_curent}' are doar {max_intrebari} întrebări disponibile.")
                print("Te rog introdu un număr valid.\n")
        except ValueError:
            print("Introdu un număr valid (ex: 5, 10).")


def salveaza_scor(domeniu, score, asked, pct):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"{timestamp} | domeniu={domeniu} | scor={score}/{asked} | procent={pct:.1f}%\n"

    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"[Avertisment] Nu am putut salva scorul în score_history.txt: {e}")


def main():
    # 1. Alege domeniul
    domeniu_selectat = alege_domeniu()

    # 2. Încarcă întrebările filtrate pentru domeniul respectiv
    questions = load_questions(domain=domeniu_selectat)

    # 3. Verificăm câte întrebări sunt disponibile
    max_intrebari = len(questions)

    if max_intrebari == 0:
        print("Nu există întrebări pentru domeniul ales. Se folosește automat MIX.")
        domeniu_selectat = "mix"
        questions = load_questions(domain=domeniu_selectat)
        max_intrebari = len(questions)

    # 4. Întreabă utilizatorul câte întrebări vrea
    num_q = alege_numar_intrebari(max_intrebari, domeniu_selectat)

    # 5. Rulăm quiz-ul cu timer per întrebare (de ex. 15 secunde)
    TIME_LIMIT_SEC = 15
    score, asked = run_quiz(
        questions,
        num_questions=num_q,
        time_limit_sec=TIME_LIMIT_SEC
    )

    # 6. Afișăm rezultatul final
    print("=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}")
    pct = (score / asked) * 100 if asked > 0 else 0
    print(f"Asta înseamnă {pct:.1f}% corect.")
    print()

    if pct >= 80:
        print("Bravo, ești pe drumul bun pentru un interviu CAE junior 👌")
    elif pct >= 50:
        print("E ok, dar mai lucrează la conceptele mai slabe din domeniul ales.")
    else:
        print("Nu-i panică. Reia teoria de bază. Asta se învață 💪")

    # 7. Salvăm scorul în istoric
    salveaza_scor(domeniu_selectat, score, asked, pct)
    print("\nRezultatul a fost salvat în score_history.txt ✅")


if __name__ == "__main__":
    main()
