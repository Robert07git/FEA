from fpdf import FPDF
import os
from stats import compute_statistics, load_scores

def export_pdf_report():
    """Creează un raport PDF detaliat în folderul reports/."""
    pdf_dir = os.path.join(os.path.dirname(__file__), "../reports")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "FEA_Quiz_Report.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FEA Quiz Detailed Report", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 12)
    stats = compute_statistics()
    if stats:
        pdf.cell(0, 10, f"Sesiuni totale: {stats['total_sessions']}", ln=True)
        pdf.cell(0, 10, f"Scor mediu general: {stats['average']}%", ln=True)
        pdf.cell(0, 10, f"Cel mai bun scor: {stats['best']}%", ln=True)
        pdf.cell(0, 10, f"Cel mai slab scor: {stats['worst']}%", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, "Scoruri medii pe domenii:", ln=True)
        for dom, avg in stats["per_domain"].items():
            pdf.cell(0, 10, f" - {dom}: {avg}%", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Istoric sesiuni:", ln=True)
    pdf.set_font("Arial", "", 11)

    scores = load_scores()
    for s in scores[-20:]:
        pdf.cell(0, 8,
                  f"{s['domain']} - {s['mode']} | {s['total']} întrebări | Scor: {s['score']}%",
                  ln=True)

    pdf.output(pdf_path)
    return pdf_path
