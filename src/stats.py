import os
from statistics import mean

# Formatul liniilor din score_history.txt este:
# 2025-10-24 22:05 | domeniu=crash | mod=exam | scor=7/10 | procent=70.0% | timp_total=95.2s | timp_intrebare=15s

def parse_history_line(line):
    """
    Primește o linie din score_history.txt și returnează un dict cu valorile extrase.
    Dacă linia nu e în formatul așteptat, returnează None.
    """
    try:
        parts = [p.strip() for p in line.strip().split("|")]

        # parts:
        # [0] => "2025-10-24 22:05"
        # [1] => "domeniu=crash"
        # [2] => "mod=exam"
        # [3] => "scor=7/10"
        # [4] => "procent=70.0%"
        # [5] => "timp_total=95.2s"
        # [6] => "timp_intrebare=15s"

        timestamp = parts[0]

        domeniu = parts[1].split("=", 1)[1]
        mode = parts[2].split("=", 1)[1]

        scor_raw = parts[3].split("=", 1)[1]  # "7/10"
        correct, total = scor_raw.split("/")
        correct = int(correct)
        total = int(total)

        procent_raw = parts[4].split("=", 1)[1]  # "70.0%"
        procent_val = float(procent_raw.replace("%", ""))

        timp_total_raw = parts[5].split("=", 1)[1]  # "95.2s"
        timp_total_s = float(timp_total_raw.replace("s", ""))

        timp_per_raw = parts[6].split("=", 1)[1]  # "15s" sau "-"
        if timp_per_raw.strip() == "-":
            timp_per_q = None
        else:
            timp_per_q = float(timp_per_raw.replace("s", ""))

        return {
            "timestamp": timestamp,
            "domeniu": domeniu,
            "mode": mode,
            "correct": correct,
            "total": total,
            "procent": procent_val,
            "timp_total_sec": timp_total_s,
            "timp_intrebare_sec": timp_per_q,
        }
    except Exception:
        return None


def load_history():
    """
    Citește score_history.txt și întoarce o listă de intrări parse-uite.
    Dacă fișierul nu există sau e gol, întoarce listă goală.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(history_path):
        return []

    entries = []
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "":
                continue
            parsed = parse_history_line(line)
            if parsed:
                entries.append(parsed)

    return entries


def summarize_by_domain(entries):
    """
    Face statistici pe fiecare domeniu separat.
    Returnează un dict:
    {
        "structural": {
            "num_sessions": ...,
            "avg_pct": ...,
            "best_pct": ...,
            "worst_pct": ...,
        },
        ...
    }
    """
    domains = {}
    for e in entries:
        dom = e["domeniu"]
        pct = e["procent"]

        if dom not in domains:
            domains[dom] = {
                "pct_list": [],
            }
        domains[dom]["pct_list"].append(pct)

    # calculăm statistici simple
    summary = {}
    for dom, data in domains.items():
        pct_list = data["pct_list"]
        summary[dom] = {
            "num_sessions": len(pct_list),
            "avg_pct": mean(pct_list),
            "best_pct": max(pct_list),
            "worst_pct": min(pct_list),
        }

    return summary


def best_and_worst_domain(domain_stats):
    """
    Primește rezultatul de la summarize_by_domain și spune:
    - best (domeniul cu cea mai bună medie)
    - worst (domeniul cu cea mai slabă medie)
    """
    if not domain_stats:
        return None, None

    # sortăm după media procentelor
    items = list(domain_stats.items())  # [(dom, stats), ...]

    items_sorted = sorted(items, key=lambda x: x[1]["avg_pct"], reverse=True)
    best = items_sorted[0]
    worst = items_sorted[-1]
    return best, worst


def split_by_mode(entries):
    """
    Împarte sesiunile în TRAIN și EXAM ca să putem calcula medii separate.
    """
    train_pcts = [e["procent"] for e in entries if e["mode"] == "train"]
    exam_pcts = [e["procent"] for e in entries if e["mode"] == "exam"]
    return train_pcts, exam_pcts


def show_dashboard():
    entries = load_history()

    if not entries:
        print("Nu există încă istoric (score_history.txt e gol). Rulează câteva quiz-uri mai întâi.")
        return

    print("=== FEA QUIZ - PROGRES PERSONAL ===\n")

    # 1. statistici generale
    total_sessions = len(entries)
    all_pcts = [e["procent"] for e in entries]
    avg_all = mean(all_pcts)
    best_all = max(all_pcts)
    worst_all = min(all_pcts)

    print(f"Număr total sesiuni: {total_sessions}")
    print(f"Performanță medie generală: {avg_all:.1f}%")
    print(f"Cel mai bun scor atins vreodată: {best_all:.1f}%")
    print(f"Cel mai slab scor: {worst_all:.1f}%")
    print()

    # 2. separat pe mod TRAIN vs EXAM
    train_pcts, exam_pcts = split_by_mode(entries)
    if train_pcts:
        print(f"Train mode - medie: {mean(train_pcts):.1f}%  (din {len(train_pcts)} sesiuni)")
    else:
        print("Train mode - medie: N/A (încă nu ai rulat TRAIN)")
    if exam_pcts:
        print(f"Exam mode  - medie: {mean(exam_pcts):.1f}%  (din {len(exam_pcts)} sesiuni)")
    else:
        print("Exam mode  - medie: N/A (încă nu ai rulat EXAM)")

    print()

    # 3. analiză pe domenii
    domain_stats = summarize_by_domain(entries)
    if domain_stats:
        print("Performanță pe domenii:")
        for dom, stats in domain_stats.items():
            print(f"  - {dom}:")
            print(f"      sesiuni: {stats['num_sessions']}")
            print(f"      medie:   {stats['avg_pct']:.1f}%")
            print(f"      best:    {stats['best_pct']:.1f}%")
            print(f"      worst:   {stats['worst_pct']:.1f}%")
        print()

        best, worst = best_and_worst_domain(domain_stats)
        if best and worst:
            best_dom, best_info = best
            worst_dom, worst_info = worst
            print(f"Domeniul tău cel mai puternic: {best_dom} (medie {best_info['avg_pct']:.1f}%) 💪")
            print(f"Domeniul unde ai cel mai mult de lucrat: {worst_dom} (medie {worst_info['avg_pct']:.1f}%) ⚠️")
    else:
        print("Nu pot calcula statistici pe domenii (nu există sesiuni salvate).")

    print("\nGata. Continuă să rulezi quiz-ul, apoi revino aici să vezi progresul.\n")


if __name__ == "__main__":
    show_dashboard()
