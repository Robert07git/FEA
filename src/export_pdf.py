import os
from fpdf import FPDF
from datetime import datetime
from stats import load_history, summarize_by_domain, best_and_worst_domain

def export_pdf_report():
    """Creează un raport PDF cu performanța din score_history.txt."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    history = load_history()
    if not history:
        return "Nu există date de exportat (score_history.txt e gol)."

    # Inițializare PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 10, "FEA Quiz Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Generat: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    # Statistici generale
    all_pcts = [e["procent"] for e in history]
    avg = sum(all_pcts) / len(all_pcts)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 8, "📊 Statistici generale", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Număr sesiuni: {len(history)}")
    pdf.multi_cell(0, 8, f"Media generală: {avg:.1f}%")
    pdf.multi_cell(0, 8, f"Cel mai bun scor: {max(all_pcts):.1f}%")
    pdf.multi_cell(0, 8, f"Cel mai slab scor: {min(all_pcts):.1f}%")
    pdf.ln(8)

    # Statistici pe domenii
    domain_stats = summarize_by_domain(history)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 8, "📘 Statistici pe domenii", ln=True)
    pdf.set_font("Arial", "", 12)
    for dom, stats in domain_stats.items():
        pdf.multi_cell(0, 8,
            f"{dom.capitalize()}: medie {stats['avg_pct']:.1f}% | best {stats['best_pct']:.1f}% | worst {stats['worst_pct']:.1f}%")
    pdf.ln(8)

    # Domenii extreme
    best, worst = best_and_worst_domain(domain_stats)
    if best and worst:
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 8,
            f"Domeniul cel mai puternic: {best[0]} ({best[1]['avg_pct']:.1f}%)")
        pdf.multi_cell(0, 8,
            f"Domeniul de îmbunătățit: {worst[0]} ({worst[1]['avg_pct']:.1f}%)")

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 7, "Acest raport a fost generat automat de aplicația FEA Quiz Trainer.\nContinuați antrenamentele pentru a crește progresul!")
    
    # Salvare PDF
    out_path = os.path.join(reports_dir, f"FEA_Quiz_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
    pdf.output(out_path)
    return out_path
