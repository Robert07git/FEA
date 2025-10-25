import os
import matplotlib.pyplot as plt
from datetime import datetime


def show_progress_chart():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        print("⚠️ Nu există fișier score_history.txt. Fă cel puțin un quiz mai întâi.")
        return

    try:
        timestamps, scores, domains, modes = [], [], [], []

        with open(history_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        for line in lines:
            parts = line.split("|")
            if len(parts) < 4:
                continue

            # extrage data
            timestamp = parts[0].split()[0].strip()
            try:
                timestamps.append(datetime.strptime(timestamp, "%Y-%m-%d"))
            except:
                continue

            # domeniu
            dom = parts[1].replace("domeniu=", "").strip()
            domains.append(dom)

            # mod (TRAIN / EXAM)
            mod = parts[2].replace("mod=", "").strip()
            modes.append(mod)

            # scor
            try:
                score_str = parts[3].split("=")[-1].split("/")[0].strip()
                total_str = parts[3].split("/")[-1].split()[0].strip()
                score = int(score_str)
                total = int(total_str)
                pct = (score / total) * 100 if total > 0 else 0
                scores.append(pct)
            except:
                scores.append(0)

        # dacă lipsesc date, ieșim
        if not timestamps or not scores:
            print("⚠️ Nu s-au putut extrage date valide din score_history.txt.")
            return

        # asigură că listele au aceeași lungime
        min_len = min(len(timestamps), len(scores))
        timestamps = timestamps[:min_len]
        scores = scores[:min_len]
        domains = domains[:min_len]
        modes = modes[:min_len]

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, scores, marker="o", linestyle="-", color="#00ffff", label="Procentaj corectitudine")
        plt.title("Evoluția scorului în timp - FEA Quiz Trainer", fontsize=14, color="#00ffff")
        plt.xlabel("Data", fontsize=12, color="white")
        plt.ylabel("Scor (%)", fontsize=12, color="white")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.ylim(0, 105)
        plt.legend()
        plt.tight_layout()

        # culoare fundal negru
        fig = plt.gcf()
        fig.patch.set_facecolor("#111")
        ax = plt.gca()
        ax.set_facecolor("#222")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        plt.show()

    except Exception as e:
        print("❌ Eroare la generarea graficului:", e)
