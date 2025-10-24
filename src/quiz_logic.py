import random
import time
import sys

# Pentru citire cu timeout pe Windows folosim msvcrt.
# Dacă nu e Windows, fallback fără timeout.
try:
    import msvcrt
    HAS_MS = True
except ImportError:
    HAS_MS = False


def _timed_input(prompt: str, timeout_seconds: int | None):
    """
    Citește input de la utilizator cu timeout (dacă timeout_seconds nu e None).
    Dacă timeout_seconds este None -> comportament normal input() fără limită.

    Returnează:
    - stringul tastat (fără whitespace la capete), sau
    - None dacă a expirat timpul (doar în modul cu timeout)
    """
    # Fără limită de timp: folosim input normal
    if timeout_seconds is None:
        answer = input(prompt)
        return answer.strip()

    # Dacă nu avem msvcrt (alt OS decât Windows), fallback fără timeout
    if not HAS_MS:
        answer = input(prompt)
        return answer.strip()

    # Windows + msvcrt: citim tastă cu tastă, cu timeout
    sys.stdout.write(prompt)
    sys.stdout.flush()

    entered = ""
    start = time.time()

    while True:
        # dacă utilizatorul tastează ceva
        if msvcrt.kbhit():
            ch = msvcrt.getwch()  # getwch -> suportă Unicode/diacritice

            # Enter => finalizează inputul
            if ch == "\r" or ch == "\n":
                sys.stdout.write("\n")
                sys.stdout.flush()
                return entered.strip()

            # Backspace => ștergem ultimul char
            if ch == "\b":
                if len(entered) > 0:
                    entered = entered[:-1]
                    # ștergere vizuală
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue

            # caracter normal
            entered += ch
            sys.stdout.write(ch)
            sys.stdout.flush()

        # verifică timeout
        if (time.time() - start) > timeout_seconds:
            sys.stdout.write("\n")
            sys.stdout.flush()
            return None

        time.sleep(0.05)


def run_quiz(questions, num_questions=10, mode="train", time_limit_sec=None):
    """
    Rulează quiz-ul.

    Parametri:
    - questions: list[dict] cu chei:
        "question", "choices", "correct_index", "explanation", "domain"
    - num_questions: câte întrebări se scot în sesiune
    - mode: "train" sau "exam"
        * train -> fără limită de timp, feedback imediat
        * exam  -> limită de timp, feedback abia la final
    - time_limit_sec: secunde per întrebare în modul exam.
                      ignorat dacă mode == "train"

    Returnează:
    - score: câte răspunsuri corecte
    - asked: câte întrebări au fost puse
    - results: list de dict cu detalii pe fiecare întrebare
    """

    # amestecăm întrebările și alegem primele N
    random.shuffle(questions)
    selected = questions[:num_questions]

    results = []
    score = 0
    asked = 0

    for idx, q in enumerate(selected, start=1):
        question_text = q.get("question", "???")
        choices = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "(fără explicație)")
        domain = q.get("domain", "n/a")

        print("------------------------------------------------------------")
        print(f"Q{idx}: {question_text}")
        print(f"(domeniu: {domain})")
        print()

        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice}")
        print()

        # construim prompt-ul în funcție de mod
        if mode == "exam":
            prompt = f"Răspunsul tău (1-{len(choices)}) [timp: {time_limit_sec}s]: "
            timeout = time_limit_sec
        else:
            prompt = f"Răspunsul tău (1-{len(choices)}): "
            timeout = None  # fără limită de timp

        answer_raw = _timed_input(prompt, timeout)

        # determinăm indexul ales
        timed_out = (answer_raw is None)
        chosen_index = None

        if not timed_out:
            try:
                chosen_index = int(answer_raw) - 1
            except (TypeError, ValueError):
                chosen_index = None

        # verificăm dacă e corect
        is_valid_choice = (
            chosen_index is not None and
            0 <= chosen_index < len(choices)
        )
        is_correct = is_valid_choice and (chosen_index == correct_index)

        if is_correct:
            score += 1

        asked += 1

        # feedback diferit în funcție de mod
        if mode == "train":
            # în TRAIN spunem imediat dacă e corect și de ce
            if timed_out:
                print("\nNu ai răspuns (fără limită de timp în TRAIN, deci asta nu ar trebui să apară).")
            else:
                print(f"\nAi răspuns: {answer_raw}")
                if is_correct:
                    print("Corect ✅")
                else:
                    print("Greșit ❌")
                    if is_valid_choice:
                        print(f"Răspuns corect: {correct_index+1}. {choices[correct_index]}")
                    else:
                        print("Răspuns invalid.")
                        print(f"Răspuns corect: {correct_index+1}. {choices[correct_index]}")
            print("Explicație:", explanation)
            print()

        else:
            # în EXAM nu dezvăluim nimic acum
            if timed_out:
                print("Timp expirat ⏱️")
            else:
                print("Răspuns înregistrat.")
            print()

        # salvăm rezultatul acestei întrebări pentru analiză finală (mai ales la EXAM)
        results.append({
            "idx": idx,
            "domain": domain,
            "question": question_text,
            "choices": choices,
            "correct_index": correct_index,
            "user_index": chosen_index,
            "timed_out": timed_out,
            "correct": is_correct,
            "explanation": explanation,
        })

    return score, asked, results
