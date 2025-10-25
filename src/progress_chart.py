import os
import matplotlib.pyplot as plt

def generate_progress_chart():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hist = os.path.join(base_dir, "score_history.txt")
    out = os.path.join(base_dir, "progress_chart.png")

    if not os.path.exists(hist):
        raise FileNotFoundError("Nu există score_history.txt – rulează câteva quiz-uri înainte.")

    dates, scores = [], []
    with open(hist, "r", encoding="utf-8") as f:
        for line in f:
            try:
                parts = [p.strip() for p in line.split("|")]
                date = parts[0]
                pct = float(parts[4].split("=")[1].replace("%", ""))
                dates.append(date)
                scores.append(pct)
            except:
                continue

    plt.figure(figsize=(8, 5))
    plt.plot(dates, scores, marker="o", linewidth=2)
    plt.title("Evoluția scorului (%)")
    plt.ylabel("Scor (%)")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
