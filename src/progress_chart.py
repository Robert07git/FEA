import os
import matplotlib.pyplot as plt


def plot_progress_chart():
    """
    Generează un grafic de progres bazat pe istoricul scorurilor din score_history.txt.
    Afișează scorurile în funcție de ordine (ex: sesiuni succesive).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        print("Fișierul score_history.txt nu există încă.")
        return

    sessions = []
    scores = []
    modes = []
    domains = []

    try:
        with open(history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Linie tipică: "2025-10-25 15:32 | domeniu=structural | mod=exam | scor=4/5 | procent=80.0%"
                parts = line.split("|")
                if len(parts) < 5:
                    continue

                try:
                    domain = parts[1].split("=")[1].strip()
                    mode = parts[2].split("=")[1].strip()
                    score_part = parts[3].split("=")[1].strip()
                    percent_part = parts[4].split("=")[1].strip().replace("%", "")
                    percent = float(percent_part)

                    domains.append(domain)
                    modes.append(mode)
                    scores.append(percent)
                    sessions.append(len(sessions) + 1)
                except Exception:
                    continue
    except Exception as e:
        print(f"Eroare la citirea istoricului: {e}")
        return

    if not scores:
        print("Nu există date valide pentru grafic.")
        return

    plt.figure(figsize=(8, 4))
    plt.plot(sessions, scores, marker="o", linestyle="-", color="cyan", linewidth=2)
    plt.title("Evoluția scorurilor FEA Quiz", fontsize=14, color="deepskyblue", pad=10)
    plt.xlabel("Sesiune", fontsize=11)
    plt.ylabel("Scor (%)", fontsize=11)
    plt.ylim(0, 110)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()

    # Salvăm graficul în folderul reports
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    img_path = os.path.join(reports_dir, "progress_chart.png")
    plt.savefig(img_path, dpi=150)
    plt.close()

    print(f"Graficul a fost generat cu succes: {img_path}")
