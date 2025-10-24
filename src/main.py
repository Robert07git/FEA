from data_loader import load_questions
from quiz_logic import run_quiz
from datetime import datetime
import os
import time

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
    Cere utilizatorului câte întrebări vrea în test, dar nu îl lasă
    să ceară mai multe decât există în domeniul ales.
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


def alege_timp_limita():
    """
    Întreabă utilizatorul câte secunde are voie pe întrebare.
    Punem și un fallback rezonabil dacă introduce prostii.
    """
    while True:
        try:
            t = int(input("Câte secunde per întrebare? (ex: 10, 15, 30): ").strip())
            if t < 3:
                print("Sub 3 secunde e prea agresiv 🙂. Hai să punem măcar 3s.")
                continue
            if t > 120:
                print("Peste 120s e prea lent. Dacă vrei studiu fără timp, putem face un mod separat. Alege <=120.")
                continue
            return t
        except ValueError:
            print("Introdu un număr întreg. Exemplu valid: 15")


def salveaza_scor(domeniu, score, asked, pct, durata_sec, timp_per_intrebare):
    """
    Scrie scorul într-un fișier local score_history.txt, împreună cu timpul.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (
        f"{timestamp} | domeniu={domeniu} | scor={score}/{asked} | procent={pct:.1f}% | "
        f"timp_total={durata_sec:.1f}s | timp_intrebare={timp_per_intrebare}s\n"
    )

    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"[Avertisment] Nu am putut salva scorul în score_history.txt: {e}")


def main():
    # 1. Alegi domeniul
    domeniu_selectat = alege_domeniu()

    # 2. Încărcăm întrebările pentru acel domeniu
    questions = load_questions(domain=domeniu_selectat)

    # Dacă domeniul selectat e gol (nu ar trebui, dar safety):
    max_intrebari = len(questions)
    if max_intrebari == 0:
        print("Nu există întrebări pentru domeniul ales. Se folosește automat MIX.")
        domeniu_selectat = "mix"
        questions = load_questions(domain=domeniu_selectat)
        max_intrebari = len(questions)

    # 3. Alegi câte întrebări vrei
    num_q = alege_numar_intrebari(max_intrebari, domeniu_selectat)

    # 4. Alegi timpul per întrebare
    time_limit_sec = alege_timp_limita()
    print(f"\nOK. Vei avea {time_limit_sec} secunde / întrebare.\n")

    # 5. Rulăm quiz-ul și măsurăm durata totală a sesiunii
    start_time = time.time()
    score, asked = run_quiz(
        questions,
        num_questions=num_q,
        time_limit_sec=time_limit_sec
    )
    end_time = time.time()
    durata_sec = end_time - start_time

    # 6. Calculăm scorul și afișăm rezultatul final
    print("=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}")
    pct = (score / asked) * 100 if asked > 0 else 0
    print(f"Asta înseamnă {pct:.1f}% corect.")
    print(f"Timp total folosit: {durata_sec:.1f} secunde (~{durata_sec/60:.1f} minute)")
    print()

    # Feedback calitativ
    if pct >= 80:
        print("Bravo, ești pe drumul bun pentru un interviu CAE junior 👌")
    elif pct >= 50:
        print("E ok, dar mai lucrează la conceptele mai slabe din domeniul ales.")
    else:
        print("Nu-i panică. Reia teoria de bază. Asta se învață 💪")

    # 7. Salvăm scorul + timpul în istoric
    salveaza_scor(
        domeniu_selectat,
        score,
        asked,
        pct,
        durata_sec,
        time_limit_sec
    )

    print("\nRezultatul a fost salvat în score_history.txt ✅")


if __name__ == "__main__":
    main()
