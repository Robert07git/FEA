import os
import matplotlib
matplotlib.use("Agg")  # backend fără fereastră GUI
import matplotlib.pyplot as plt


def generate_progress_chart():
    base_dir = os.path.dirname(__file__)
    history_path = os.path.join(base_dir, "score_history.txt")

    # dacă nu există istoric, ieșim politicos
    if not os.path.exists(history_path):
        raise FileNotFoundError("Nu există score_history.txt încă. Rulează câteva quiz-uri mai întâi.")

    # citim scorurile
    sessions = []
    scores = []
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # format: domeniu,mod,nr_intrebari,procent
            try:
                domeniu, mode, n_q, pct = line.split(",")
                pct_val = float(pct)
                sessions.append(f"{domeniu} ({mode})")
                scores.append(pct_val)
            except ValueError:
                # linie coruptă sau alt format
                continue

    if not scores:
        raise RuntimeError("Nu am putut parsa scoruri din score_history.txt")

    # facem grafic
    plt.figure(figsize=(8,4))
    plt.plot(range(1, len(scores)+1), scores, marker="o", color="#00FFFF")
    plt.ylim(0, 100)
    plt.xlabel("Sesiune")
    plt.ylabel("Scor (%)")
    plt.title("Evoluția scorului la quiz")
    plt.grid(True, linestyle="--", alpha=0.3)

    # asigurăm folderul reports
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    out_path = os.path.join(reports_dir, "progress_chart.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


if __name__ == "__main__":
    path = generate_progress_chart()
    print("Grafic generat:", path)
