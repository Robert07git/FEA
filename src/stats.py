import os
from statistics import mean


def load_score_history():
    """
    Încarcă scorurile din fișierul score_history.txt și le returnează sub formă de listă de dict-uri.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        print("Fișierul score_history.txt nu există încă.")
        return []

    entries = []
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) < 5:
                    continue

                try:
                    timestamp = parts[0].strip()
                    domain = parts[1].split("=")[1].strip()
                    mode = parts[2].split("=")[1].strip()
                    score_raw = parts[3].split("=")[1].strip()
                    percent_raw = parts[4].split("=")[1].strip().replace("%", "")
                    percent = float(percent_raw)
                    entries.append({
                        "timestamp": timestamp,
                        "domain": domain,
                        "mode": mode,
                        "score": score_raw,
                        "percent": percent
                    })
                except Exception:
                    continue
    except Exception as e:
        print(f"Eroare la citirea istoricului: {e}")

    return entries


def compute_statistics():
    """
    Calculează statistici generale: media scorurilor, cele mai bune domenii etc.
    """
    data = load_score_history()
    if not data:
        print("Nu există date pentru statistici.")
        return None

    overall_avg = mean([d["percent"] for d in data])
    total_sessions = len(data)

    # Calculăm media pe domenii
    domains = {}
    for d in data:
        domains.setdefault(d["domain"], []).append(d["percent"])

    domain_averages = {k: mean(v) for k, v in domains.items()}
    best_domain = max(domain_averages, key=domain_averages.get)
    worst_domain = min(domain_averages, key=domain_averages.get)

    stats = {
        "total_sessions": total_sessions,
        "overall_avg": overall_avg,
        "domain_averages": domain_averages,
        "best_domain": best_domain,
        "worst_domain": worst_domain
    }
    return stats


def print_statistics():
    """
    Afișează statisticile într-un format frumos în consolă.
    """
    stats = compute_statistics()
    if not stats:
        return

    print("\n=== STATISTICI FEA QUIZ ===")
    print(f"Sesiuni totale: {stats['total_sessions']}")
    print(f"Media generală: {stats['overall_avg']:.1f}%\n")

    print("Medii pe domenii:")
    for domain, avg in stats["domain_averages"].items():
        print(f"  • {domain.capitalize()}: {avg:.1f}%")

    print(f"\nCel mai bun domeniu: {stats['best_domain'].capitalize()}")
    print(f"Cel mai slab domeniu: {stats['worst_domain'].capitalize()}")
