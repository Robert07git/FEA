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


def alege_modul():
    print("Alege modul de testare:")
    print("  1 - TRAIN  (fără limită de timp, feedback imediat și explicații după fiecare întrebare)")
    print("  2 - EXAM   (limită de timp pe întrebare, feedback abia la final)")
    alegere = input("Mod (1-2): ").strip()
    if alegere == "2":
        print("\nMod selectat: EXAM\n")
        return "exam"
    else:
        print("\nMod selectat: TRAIN\n")
        return "train"


def alege_timp_limita():
    """
    Întreabă utilizatorul câte secunde are voie pe întrebare (pentru EXAM).
    """
    while True:
        try:
            t = int(input("Câte secunde per întrebare? (ex: 10, 15, 30): ").strip())
            if t < 3:
                print("Sub 3 secunde e prea agresiv 🙂. Hai să punem măcar 3s.")
                continue
            if t > 120:
                print("Peste 120s e prea lent. Dacă vrei studiu fără timp, folosește modul TRAIN.")
                continue
            return t
        except ValueError:
            print("Introdu un număr întreg. Exemplu valid: 15")


def salveaza_scor(domeniu, mode, score, asked, pct, durata_sec, timp_per_intrebare):
    """
    Scrie scorul într-un fișier local score_history.txt, împreună cu timpul și modul.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (
        f"{timestamp} | domeniu={domeniu} | mod={mode} | "
        f"scor={score}/{asked} | procent={pct:.1f}% | "
        f"timp_total={durata_sec:.1f}s | timp_intrebare={timp_per_intrebare}\n"
    )

    try:
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"[Avertisment] Nu am putut salva scorul în score_history.txt: {e}")


def genereaza_review_text(domeniu, mode, score, asked, pct, durata_sec, timp_per_intrebare, results):
    """
    Construiește textul raportului pentru sesiunea EXAM.
    Include doar întrebările greșite / fără răspuns.
    """
    gresite = [r for r in results if not r["correct"]]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    header = []
    header.append("=== RAPORT EXAM FEA QUIZ ===")
    header.append(f"Data: {timestamp}")
    header.append(f"Domeniu testat: {domeniu}")
    header.append(f"Mod: {mode.upper()}")
    header.append(f"Scor: {score}/{asked}  ({pct:.1f}%)")
    header.append(f"Timp total: {durata_sec:.1f} sec (~{durata_sec/60:.1f} min)")
    header.append(f"Timp per întrebare în EXAM: {timp_per_intrebare}")
    header.append("")
    header.append("Întrebări care necesită atenție (greșite / fără răspuns):")
    header.append("")

    body_lines = []

    if not gresite:
        body_lines.append("Ai răspuns corect la toate întrebările. Excelent 🎯")
    else:
        for r in gresite:
            idx = r["idx"]
            qtext = r["question"]
            choices = r["choices"]
            correct_idx = r["correct_index"]
            expl = r["explanation"]
            domeniu_q = r["domain"]

            body_lines.append("------------------------------------------------------------")
            body_lines.append(f"Q{idx} ({domeniu_q}) -> {qtext}")
            body_lines.append(f"Răspuns corect: {correct_idx+1}. {choices[correct_idx]}")
            body_lines.append("Explicație: " + expl)
            body_lines.append("")

    return "\n".join(header + body_lines)


def salveaza_review_exam(domeniu, mode, score, asked, pct, durata_sec, timp_per_intrebare, results):
    """
    Dacă modul este EXAM, salvăm un fișier text separat cu întrebările greșite.
    Numele fișierului: exam_review_YYYY-MM-DD_HH-MM.txt
    """
    if mode != "exam":
        return None  # nu facem fișier pentru TRAIN

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp_file = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"exam_review_{timestamp_file}.txt"
    path = os.path.join(base_dir, filename)

    content = genereaza_review_text(
        domeniu=domeniu,
        mode=mode,
        score=score,
        asked=asked,
        pct=pct,
        durata_sec=durata_sec,
        timp_per_intrebare=timp_per_intrebare,
        results=results
    )

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    except Exception as e:
        print(f"[Avertisment] Nu am putut salva raportul EXAM: {e}")
        return None


def afiseaza_revizuire_exam(results):
    """
    După EXAM: afișăm în consolă doar întrebările greșite / fără răspuns,
    cu răspunsul corect și explicația, ca să poți învăța.
    """
    gresite = [r for r in results if not r["correct"]]

    print("\n=== REVIZUIRE ÎNTREBĂRI GREȘITE ===")
    if not gresite:
        print("Ai răspuns corect la toate întrebările. GG 🎯")
        return

    for r in gresite:
        idx = r["idx"]
        qtext = r["question"]
        choices = r["choices"]
        correct_idx = r["correct_index"]
        expl = r["explanation"]
        domeniu_q = r["domain"]

        print("------------------------------------------------------------")
        print(f"Q{idx} ({domeniu_q}) -> {qtext}")
        print(f"Răspuns corect: {correct_idx+1}. {choices[correct_idx]}")
        print("Explicație:", expl)
        print()


def main():
    # 1. Alegem domeniul
    domeniu_selectat = alege_domeniu()

    # 2. Încărcăm întrebările din domeniul ales
    questions = load_questions(domain=domeniu_selectat)

    max_intrebari = len(questions)
    if max_intrebari == 0:
        print("Nu există întrebări pentru domeniul ales. Se folosește automat MIX.")
        domeniu_selectat = "mix"
        questions = load_questions(domain=domeniu_selectat)
        max_intrebari = len(questions)

    # 3. Alegem câte întrebări vrei
    num_q = alege_numar_intrebari(max_intrebari, domeniu_selectat)

    # 4. Alegem modul (TRAIN / EXAM)
    mode = alege_modul()

    # 5. Dacă e EXAM, alegem timpul per întrebare
    if mode == "exam":
        time_limit_sec = alege_timp_limita()
        print(f"\nOK. Vei avea {time_limit_sec} secunde / întrebare.\n")
    else:
        time_limit_sec = None
        print("Mod TRAIN: fără limită de timp per întrebare.\n")

    # 6. Rulăm quiz-ul și măsurăm durata totală
    start_time = time.time()
    score, asked, results = run_quiz(
        questions,
        num_questions=num_q,
        mode=mode,
        time_limit_sec=time_limit_sec
    )
    end_time = time.time()
    durata_sec = end_time - start_time

    # 7. Scor final
    print("=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}")
    pct = (score / asked) * 100 if asked > 0 else 0
    print(f"Asta înseamnă {pct:.1f}% corect.")
    print(f"Timp total folosit: {durata_sec:.1f} secunde (~{durata_sec/60:.1f} minute)")
    print()

    if pct >= 80:
        print("Bravo, ești pe drumul bun pentru un interviu CAE junior 👌")
    elif pct >= 50:
        print("E ok, dar mai lucrează la conceptele mai slabe din domeniul ales.")
    else:
        print("Nu-i panică. Reia teoria de bază. Asta se învață 💪")

    # 8. Dacă ai fost în modul EXAM, îți arătăm greșelile pe ecran
    if mode == "exam":
        afiseaza_revizuire_exam(results)

    # 9. Salvăm scorul în istoricul general
    salveaza_scor(
        domeniu_selectat,
        mode,
        score,
        asked,
        pct,
        durata_sec,
        f"{time_limit_sec}s" if time_limit_sec is not None else "-"
    )

    # 10. Salvăm raportul EXAM într-un fișier separat (doar în modul EXAM)
    review_path = salveaza_review_exam(
        domeniu=domeniu_selectat,
        mode=mode,
        score=score,
        asked=asked,
        pct=pct,
        durata_sec=durata_sec,
        timp_per_intrebare=f"{time_limit_sec}s" if time_limit_sec is not None else "-",
        results=results
    )

    if review_path:
        print(f"\nRaportul EXAM a fost salvat în: {review_path} ✅")

    print("\nRezultatul a fost salvat în score_history.txt ✅")


if __name__ == "__main__":
    main()
