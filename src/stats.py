import os
from statistics import mean

def parse_history_line(line):
    try:
        parts = [p.strip() for p in line.strip().split("|")]
        timestamp = parts[0]
        domeniu = parts[1].split("=")[1]
        mode = parts[2].split("=")[1]
        correct, total = map(int, parts[3].split("=")[1].split("/"))
        procent = float(parts[4].split("=")[1].replace("%", ""))
        timp_total = float(parts[5].split("=")[1].replace("s", ""))
        timp_intrebare = parts[6].split("=")[1].replace("s", "").strip()
        timp_intrebare = float(timp_intrebare) if timp_intrebare not in ["-", ""] else None
        return {
            "timestamp": timestamp,
            "domeniu": domeniu,
            "mode": mode,
            "correct": correct,
            "total": total,
            "procent": procent,
            "timp_total_sec": timp_total,
            "timp_intrebare_sec": timp_intrebare
        }
    except Exception:
        return None

def load_history():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "score_history.txt")
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_history_line(line)
            if parsed:
                entries.append(parsed)
    return entries

def summarize_by_domain(entries):
    domains = {}
    for e in entries:
        d = e["domeniu"]
        if d not in domains:
            domains[d] = []
        domains[d].append(e["procent"])

    summary = {}
    for d, vals in domains.items():
        summary[d] = {
            "num_sessions": len(vals),
            "avg_pct": mean(vals),
            "best_pct": max(vals),
            "worst_pct": min(vals)
        }
    return summary

def best_and_worst_domain(stats):
    if not stats:
        return None, None
    items = sorted(stats.items(), key=lambda x: x[1]["avg_pct"], reverse=True)
    return items[0], items[-1]

def format_statistics():
    entries = load_history()
    if not entries:
        return "Nu există sesiuni înregistrate încă."

    all_pcts = [e["procent"] for e in entries]
    avg_all = mean(all_pcts)
    domain_stats = summarize_by_domain(entries)
    best, worst = best_and_worst_domain(domain_stats)

    result = f"Performanță generală: {avg_all:.1f}% ({len(entries)} sesiuni)\n"
    if best and worst:
        result += f"Cel mai bun domeniu: {best[0]} ({best[1]['avg_pct']:.1f}%)\n"
        result += f"Cel mai slab domeniu: {worst[0]} ({worst[1]['avg_pct']:.1f}%)"
    return result
