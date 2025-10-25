import os
from collections import defaultdict


def show_dashboard():
    """
    Citește istoricul din score_history.txt și afișează statistici utile:
    - media generală
    - cele mai frecvente domenii
    - scorul maxim și minim
    - număr total de sesiuni
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        print("\n[INFO] Nu există fișier score_history.txt. Rulează un quiz mai întâi.")
        return

    domenii_stats = defaultdict(list)

    with open(history_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    if not lines:
        print("\n[INFO] Fișierul score_history.txt este gol.")
        return

    for line in lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 5:
            continue
        try:
            domeniu = parts[1].split("=")[1].strip()
            pct_text = parts[4].split("=")[1].replace("%", "").strip()
            pct = float(pct_text)
            domenii_stats[domeniu].append(pct)
        except Exception:
            continue

    total_sesiuni = sum(len(v) for v in domenii_stats.values())
    scoruri_totale = [v for lst in domenii_stats.values() for v in lst]
    medie_globala = sum(scoruri_totale) / len(scoruri_totale) if scoruri_totale else 0

    print("\n=== DASHBOARD FEA QUIZ ===")
    print(f"Total sesiuni efectuate: {total_sesiuni}")
    print(f"Scor mediu global: {medie_globala:.1f}%")

    print("\nPerformanță pe domenii:")
    for d, scoruri in domenii_stats.items():
        medie = sum(scoruri) / len(scoruri)
        max_score = max(scoruri)
        min_score = min(scoruri)
        print(f"  • {d:<10} -> Medie: {medie:.1f}% | Max: {max_score:.1f}% | Min: {min_score:.1f}% | Sesiuni: {len(scoruri)}")

    best_domain = max(domenii_stats, key=lambda d: sum(domenii_stats[d]) / len(domenii_stats[d]))
    worst_domain = min(domenii_stats, key=lambda d: sum(domenii_stats[d]) / len(domenii_stats[d]))
    print("\nCel mai bun domeniu:", best_domain)
    print("Domeniul ce necesită îmbunătățire:", worst_domain)

    print("\nSugestie:")
    if medie_globala >= 85:
        print("🏆 Excelent! Ești aproape pregătit pentru interviuri CAE.")
    elif medie_globala >= 65:
        print("📈 Foarte bine! Lucrează la consistență în domeniile mai slabe.")
    else:
        print("💡 Mai exersează. Concentrează-te pe conceptele de bază și recitește explicațiile din modul TRAIN.")
