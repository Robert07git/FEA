import random
import time
import sys
import os

# Pentru citire cu timeout pe Windows folosim msvcrt.
# Dacă rulezi pe Windows (ceea ce faci acum), asta merge perfect.
try:
    import msvcrt
    HAS_MS = True
except ImportError:
    HAS_MS = False


def _timed_input(prompt: str, timeout_seconds: int):
    """
    Cere input de la utilizator cu timeout.
    Dacă utilizatorul nu răspunde în timpul dat, returnează None.
    Implementare pentru Windows (msvcrt). Dacă nu e Windows, cade pe input normal.
    """
    # dacă nu avem msvcrt (alt OS), facem fallback fără timeout
    if not HAS_MS:
        # fallback simplu: fără timeout
        answer = input(prompt)
        return answer.strip()

    # Windows + msvcrt: citim caracter cu caracter, cu timeout
    sys.stdout.write(prompt)
    sys.stdout.flush()

    entered = ""
    start = time.time()

    while True:
        # dacă a tastat ceva
        if msvcrt.kbhit():
            ch = msvcrt.getwch()  # getwch păstrează diacritice/UTF-16 corect

            # Enter -> finalizăm inputul
            if ch == "\r" or ch == "\n":
                sys.stdout.write("\n")
                sys.stdout.flush()
                return entered.strip()

            # Backspace -> ștergem ultimul caracter vizual și logic
            if ch == "\b":
                if len(entered) > 0:
                    entered = entered[:-1]
                    # Șterge caracterul de pe ecran
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue

            # Caracter normal -> îl adăugăm și îl afișăm
            entered += ch
            sys.stdout.write(ch)
            sys.stdout.flush()

        # timeout?
        if (time.time() - start) > timeout_seconds:
            sys.stdout.write("\n")
            sys.stdout.flush()
            return None

        # mică pauză ca să nu blocăm CPU
        time.sleep(0.05)


def run_quiz(questions, num_questions=10, time_limit_sec=15):
    """
    Rulează quiz-ul.
    - questions: listă de întrebări (dict cu 'question', 'choices', 'correct_index', 'explanation')
    - num_questions: câte întrebări să pună în test
    - time_limit_sec: câte secunde are user-ul să răspundă la fiecare întrebare

    Returnează:
    - score (răspunsuri corecte)
    - asked (câte întrebări au fost puse)
    """

    # amestecăm întrebările și alegem primele num_questions
    random.shuffle(questions)
    selected = questions[:num_questions]

    score = 0
    asked = 0

    for idx, q in enumerate(selected, start=1):
        question_text = q.get("question", "???")
        choices = q.get("choices", [])
        correct_index = q.get("correct_index", 0)
        explanation = q.get("explanation", "(fără explicație)")
        domain = q.get("domain", "n/a")

        # litere pentru afișat răspunsuri: A, B, C, D...
        letters = ["A", "B", "C", "D", "E", "F"]

        print("------------------------------------------------------------")
        print(f"Q{idx}: {question_text}")
        print(f"(domeniu: {domain})")
        print()

        # afișăm opțiunile numerotate
        for i, choice in enumerate(choices):
            # ex: "1. Aplica o forta constanta pe un nod"
            print(f"{i+1}. {choice}")
        print()

        # cerem răspuns cu timeout
        answer_raw = _timed_input(
            f"Răspunsul tău (1-{len(choices)}) [timp: {time_limit_sec}s]: ",
            timeout_seconds=time_limit_sec
        )

        # determinăm corectitudinea
        if answer_raw is None:
            # timp expirat
            print("\nTimp expirat ⏱️")
            chosen_index = None
        else:
            # încearcă să convertească la int
            try:
                chosen_index = int(answer_raw) - 1
            except ValueError:
                chosen_index = None

        # feedback
        if chosen_index is not None and 0 <= chosen_index < len(choices):
            # avem răspuns valid numeric
            print(f"\nAi răspuns: {chosen_index+1}")
            if chosen_index == correct_index:
                print("Corect ✅")
                score += 1
            else:
                print("Greșit ❌")
                print(
                    f"Răspuns corect: {correct_index+1}. {choices[correct_index]}"
                )
        else:
            # nu a răspuns sau răspuns invalid
            print("Răspuns invalid sau lipsă răspuns ❌")
            print(
                f"Răspuns corect: {correct_index+1}. {choices[correct_index]}"
            )

        # explicație
        print("Explicație:", explanation)
        print()

        asked += 1

    return score, asked
