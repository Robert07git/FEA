import os
import matplotlib.pyplot as plt
from statistics import mean

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(BASE_DIR, "score_history.txt")
OUTPUT_IMG = os.path.join(BASE_DIR, "progress_chart.png")

def parse_history_line(line):
    # Refolosim logica asemănătoare cu stats.py
    try:
        parts = [p.strip() for p in line.strip().split("|")]

        # [0] timestamp
        # [1] domeniu=...
        # [2] mod=...
        # [3] scor=7/10
        # [4] procent=70.0%
        timestamp = parts[0]
        domeniu = parts[1].split("=", 1)[1]
        mode = parts[2].split("=", 1)[1]

        scor_raw = parts[3].split("=", 1)[1]  # "7/10"
        correct, total = scor_raw.split("/")
        correct = int(correct)
        total = int(total)

        pct_raw = parts[4].split("=", 1)[1]  # "70.0%"
        pct_val = float(pct_raw.replace("%", ""))

        return {
            "timestamp": timestamp,
            "domeniu": domeniu,
            "mode": mode,
            "correct": correct,
            "total": total,
            "pct": pct_val,
        }
    except Exception:
        return None

def load_scores():
    if not os.path.exists(HISTORY_PATH):
        return []

    out = []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "":
                continue
            entry = parse_history_line(line)
            if entry:
                out.append(entry)
    return out

def main():
    entries = load_scores()
    if not entries:
        print("Nu există scoruri în score_history.txt încă.")
        return

    # ordonăm după timestamp așa cum apare în fișier (deja e în ordine cronologică
    # pentru că noi tot adăugăm la final)
    # Dacă vrem să fim siguri: putem păstra ordinea citită.

    pct_values = [e["pct"] for e in entries]
    labels_x = list(range(1, len(pct_values) + 1))

    avg_all = mean(pct_values)

    plt.figure()
    plt.plot(labels_x, pct_values, marker="o")
    plt.axhline(avg_all, linestyle="--", label=f"Media totală ({avg_all:.1f}%)")

    plt.xlabel("Sesiunea (#)")
    plt.ylabel("Scor (%)")
    plt.title("Evoluția scorului în timp (toate domeniile / toate modurile)")
    plt.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    plt.close()

    print("Grafic generat și salvat ca:")
    print(OUTPUT_IMG)
    print("Poți deschide imaginea progress_chart.png ca să vezi trendul tău.")

if __name__ == "__main__":
    main()
