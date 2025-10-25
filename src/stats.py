import os
from fpdf import FPDF
from datetime import datetime


def export_quiz_pdf():
    """
    Generează un raport PDF cu istoricul scorurilor din score_history.txt.
    Salvează fișierul în folderul 'reports'.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")
    reports_dir = os.path.join(base_dir, "reports")

    if not os.path.exists(history_path):
        print("[INFO] Nu există score_history.txt — rulează măcar un quiz.")
        return

    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    lines = []
    with open(history_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    if not lines:
        print("[INFO] Fișierul score_history.txt este gol.")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Titlu mare
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 255, 255)
    pdf.cell(0, 10, "FEA Quiz - Raport Rezultate", ln=True, align="C")
    pdf.ln(10)

    # Data generării
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(20, 20, 20)
    pdf.cell(0, 10, f"Generat la: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 255, 100)
    pdf.cell(0, 10, "Istoric performanță:", ln=True)
    pdf.ln(5)

    # Fundal gri închis
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "", 11)

    for line in lines[-20:]:  # ultimele 20 sesiuni
        pdf.multi_cell(0, 8, line, border=0, align="L", fill=True)
        pdf.ln(1)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(255, 255, 0)
    pdf.cell(0, 10, "Interpretare:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(0, 8,
        "Rezultatele de mai sus reflectă evoluția ta în timp. "
        "Încearcă să crești consistența peste 80% în modul EXAM. "
        "Pentru o învățare eficientă, analizează domeniile cu scor scăzut."
    )

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 8, "FEA Quiz Trainer © 2025 — Mechanical Engineer Edition", ln=True, align="C")

    filename = f"FEA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(reports_dir, filename)
    pdf.output(output_path)

    print(f"[OK] Raport PDF generat cu succes: {output_path}")
