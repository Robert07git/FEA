import os
import matplotlib.pyplot as plt
from datetime import datetime


def show_progress_chart():
    """
    Creează un grafic al scorurilor înregistrate în score_history.txt.
    Arată progresul în timp și media totală.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        print("[INFO] Nu există fișier score_history.txt. Rulează mai întâi un quiz.")
        return

    timestamps, scores = [], []

    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) < 5:
                continue
            try:
                ts = parts[0].strip()
                score_part = parts[3].split("=")[1].strip() if "=" in parts[3] else parts[3].strip()
                pct_part = parts[4].split("=")[1].replace("%", "").strip() if "=" in parts[4] else None

                if pct_part:
                    timestamps.append(datetime.strptime(ts, "%Y-%m-%d %H:%M"))
                    scores.append(float(pct_part))
            except Exception:
                continue

    if not scores:
        print("[INFO] Nu există date valide în score_history.txt.")
        return

    plt.figure(figsize=(9, 5))
    plt.plot(timestamps, scores, marker="o", color="#00ffff", linewidth=2, label="Procentaj (%)")
    plt.title("Evoluția performanței la FEA Quiz", fontsize=14, weight="bold")
    plt.xlabel("Dată")
    plt.ylabel("Scor (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=30)
    plt.ylim(0, 100)

    avg_score = sum(scores) / len(scores)
    plt.axhline(avg_score, color="orange", linestyle="--", label=f"Medie: {avg_score:.1f}%")
    plt.legend()
    plt.tight_layout()
    plt.show()
