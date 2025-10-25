import os
import matplotlib.pyplot as plt

def show_progress_chart():
    """Desenează graficul progresului scorurilor."""
    path = os.path.join(os.path.dirname(__file__), "score_history.txt")
    if not os.path.exists(path):
        raise FileNotFoundError("Nu există date de progres încă (score_history.txt).")

    scores = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 4:
                _, _, _, pct = parts
                scores.append(float(pct))

    plt.figure(figsize=(8, 4))
    plt.title("Progresul scorurilor în timp")
    plt.plot(scores, marker="o", color="#00FFFF")
    plt.xlabel("Sesiune")
    plt.ylabel("Scor (%)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()
