import random

def run_quiz(questions, num_questions=10):
    """
    Rulează quiz-ul.
    - alege aleator întrebări
    - colectează scorul
    - întoarce scorul final
    """
    # Amestecăm întrebările ca să nu fie mereu aceeași ordine
    random.shuffle(questions)

    score = 0
    asked = 0

    for q in questions[:num_questions]:
        asked += 1
        print("--------------------------------------------------")
        print(f"Q{asked}: {q['question']}")
        print()

        for i, choice in enumerate(q["choices"]):
            print(f"{i+1}. {choice}")

        print()
        user_answer = input("Răspunsul tău (1-4): ").strip()

        # validare input
        if user_answer not in ["1", "2", "3", "4"]:
            print("Input invalid. Îl considerăm greșit ❌")
            is_correct = False
        else:
            user_index = int(user_answer) - 1
            is_correct = (user_index == q["correct_index"])

        if is_correct:
            print("Corect ✅")
            score += 1
        else:
            correct_text = q["choices"][q["correct_index"]]
            print(f"Greșit ❌. Răspuns corect: {correct_text}")

        print("Explicație:", q["explanation"])
        print()

    return score, asked
