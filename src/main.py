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
    gresite = [r for r in results if not r["correct"]]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    header = [
        "=== RAPORT EXAM FEA QUIZ ===",
        f"Data: {timestamp}",
        f"Domeniu testat: {domeniu}",
        f"Mod: {mode.upper()}",
        f"Scor: {score}/{asked}  ({pct:.1f}%)",
        f"Timp total: {durata_sec:.1f} sec (~{durata_sec/60:.1f} min)",
        f"Timp per întrebare: {timp_per_intrebare}",
        "",
        "Întrebări care necesită atenție:",
        ""
    ]

    if not gresite:
        return "\n".join(header + ["Ai răspuns corect la toate întrebările. Excelent 🎯"])

    body = []
    for r in gresite:
        body += [
            "-" * 60,
            f"Q{r['idx']} ({r['domain']}) -> {r['question']}",
            f"Răspuns corect: {r['choices'][r['correct_index']]}",
            f"Explicație: {r['explanation']}",
            ""
        ]

    return "\n".join(header + body)


def salveaza_review_exam(domeniu, mode, score, asked, pct, durata_sec, timp_per_intrebare, results):
    if mode != "exam":
        return None

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp_file = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"exam_review_{timestamp_file}.txt"
    path = os.path.join(base_dir, filename)

    content = genereaza_review_text(
        domeniu, mode, score, asked, pct, durata_sec, timp_per_intrebare, results
    )

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    except Exception as e:
        print(f"[Avertisment] Nu am putut salva raportul EXAM: {e}")
        return None


def afiseaza_revizuire_exam(results):
    gresite = [r for r in results if not r["correct"]]
    print("\n=== REVIZUIRE ÎNTREBĂRI GREȘITE ===")
    if not gresite:
        print("Ai răspuns corect la toate întrebările. GG 🎯")
        return
    for r in gresite:
        print("-" * 60)
        print(f"Q{r['idx']} ({r['domain']}) -> {r['question']}")
        print(f"Răspuns corect: {r['choices'][r['correct_index']]}")
        print("Explicație:", r['explanation'])
        print()


def main():
    domeniu = alege_domeniu()
    questions = load_questions(domain=domeniu)

    if not questions:
        print("Nu există întrebări pentru domeniul selectat.")
        return

    num_q = alege_numar_intrebari(len(questions), domeniu)
    mode = alege_modul()
    time_limit_sec = alege_timp_limita() if mode == "exam" else None

    print(f"\nMod selectat: {mode.upper()} — {num_q} întrebări în domeniul {domeniu}\n")
    start = time.time()

    score, asked, results = run_quiz(
        questions, num_questions=num_q, mode=mode, time_limit_sec=time_limit_sec
    )

    durata = time.time() - start
    pct = (score / asked) * 100 if asked > 0 else 0

    print("\n=== REZULTAT FINAL ===")
    print(f"Scor: {score}/{asked}  ({pct:.1f}%)")
    print(f"Timp total: {durata:.1f} secunde (~{durata/60:.1f} minute)")

    salveaza_scor(domeniu, mode, score, asked, pct, durata, f"{time_limit_sec}s" if time_limit_sec else "-")

    if mode == "exam":
        afiseaza_revizuire_exam(results)
        review_path = salveaza_review_exam(domeniu, mode, score, asked, pct, durata, time_limit_sec, results)
        if review_path:
            print(f"\nRaport EXAM salvat în: {review_path}")

    print("\nRezultatul a fost salvat în score_history.txt ✅")


if __name__ == "__main__":
    main()
