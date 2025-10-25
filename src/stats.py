import os
import statistics

def load_scores():
    """Încărcă scorurile salvate în score_history.txt."""
    path = os.path.join(os.path.dirname(__file__), "score_history.txt")
    if not os.path.exists(path):
        return []

    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 4:
                domain, mode, total, pct = parts
                data.append({
                    "domain": domain,
                    "mode": mode,
                    "total": int(total),
                    "score": float(pct)
                })
    return data


def compute_statistics():
    """Returnează un dicționar cu statistici generale."""
    scores = load_scores()
    if not scores:
        return None

    values = [s["score"] for s in scores]
    domains = {}
    for s in scores:
        domains.setdefault(s["domain"], []).append(s["score"])

    return {
        "total_sessions": len(values),
        "average": round(statistics.mean(values), 2),
        "best": round(max(values), 2),
        "worst": round(min(values), 2),
        "per_domain": {k: round(statistics.mean(v), 2) for k, v in domains.items()}
    }


def format_statistics():
    """Returnează un text formatat pentru afișare."""
    stats = compute_statistics()
    if not stats:
        return "Nu există date statistice."

    txt = f"📊 Statistici generale\n"
    txt += f"Sesiuni totale: {stats['total_sessions']}\n"
    txt += f"Scor mediu general: {stats['average']}%\n"
    txt += f"Cel mai bun scor: {stats['best']}%\n"
    txt += f"Cel mai slab scor: {stats['worst']}%\n\n"
    txt += "Scor mediu pe domeniu:\n"
    for dom, avg in stats["per_domain"].items():
        txt += f" • {dom}: {avg}%\n"
    return txt
