import os
import matplotlib.pyplot as plt

def generate_progress_chart():
    file_path = os.path.join(os.path.dirname(__file__), "score_history.txt")
    if not os.path.exists(file_path):
        print("Nu există date pentru generarea graficului.")
        return

    sessions = []
    scores = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                domain, mode, total, score = line.strip().split(",")
                sessions.append(f"{domain}-{mode}")
                scores.append(float(score))
            except ValueError:
                continue

    if not sessions:
        print("Nicio sesiune validă găsită în istoric.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(scores, marker="o", color="#00FFFF", linewidth=2)
    plt.title("Evoluția scorurilor FEA Quiz", fontsize=14, fontweight="bold", color="#00FFFF")
    plt.xlabel("Sesiuni", color="white")
    plt.ylabel("Scor (%)", color="white")
    plt.xticks(range(len(sessions)), sessions, rotation=45, ha="right", color="white")
    plt.yticks(color="white")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gcf().patch.set_facecolor("#111")
    plt.gca().set_facecolor("#111")

    plt.tight_layout()
    plt.show()
