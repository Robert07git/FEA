import random
import time
import pygame  # pentru sunet
from data_loader import load_questions

pygame.mixer.init()

def play_tick():
    """Sunet scurt de avertizare la 5 secunde rămase."""
    try:
        pygame.mixer.Sound("tick.wav").play()
    except:
        pass

def run_quiz(domain, mode, num_questions, time_limit_sec=None):
    """
    Rulează quiz-ul și returnează:
    scor, număr întrebări, listă cu rezultate (pentru PDF și statistici).
    """
    questions = load_questions(domain)
    if len(questions) == 0:
        raise ValueError(f"Nu există întrebări pentru domeniul {domain}.")

    selected = random.sample(questions, min(num_questions, len(questions)))
    results = []
    score = 0

    for idx, q in enumerate(selected, start=1):
        print(f"\nÎntrebarea {idx}/{num_questions}: {q['question']}")
        for i, ch in enumerate(q["choices"], start=1):
            print(f"  {i}. {ch}")

        answered = False
        start_time = time.time()
        user_choice = None

        while not answered:
            if mode == "exam" and time_limit_sec is not None:
                elapsed = time.time() - start_time
                if elapsed >= time_limit_sec:
                    print("\n⏰ Timpul a expirat!")
                    break
                if time_limit_sec - elapsed <= 5:
                    play_tick()

            ans = input("Răspuns (1-4): ").strip()
            if ans in ["1", "2", "3", "4"]:
                user_choice = int(ans) - 1
                answered = True
            else:
                print("Introdu un număr valid (1-4).")

        correct = (user_choice == q["correct_index"])
        if correct:
            score += 1
            print("✅ Corect!")
        else:
            print(f"❌ Greșit! Răspuns corect: {q['correct_index']+1}. {q['choices'][q['correct_index']]}")
        if mode == "train":
            print(f"Explicație: {q['explanation']}")

        results.append({
            "idx": idx,
            "domain": domain,
            "question": q["question"],
            "choices": q["choices"],
            "correct_index": q["correct_index"],
            "correct": correct,
            "explanation": q["explanation"],
        })

    pct = (score / num_questions) * 100 if num_questions > 0 else 0
    avg_time = f"{time_limit_sec}s" if time_limit_sec else "-"

    return score, num_questions, results, pct, avg_time
