# pdf_exporter_modern.py
from fpdf import FPDF
import os

FONT_PATH = os.path.join("data", "DejaVuSans.ttf")

def export_pdf_modern(result, answers=None):
    """
    Generează un PDF cu suport complet pentru caractere Unicode (ă, î, ș, ț)
    Include rezumatul sesiunii și, dacă este TRAIN MODE, detalii pe întrebări.
    """
    pdf = FPDF()
    pdf.add_page()

    # === FONT & STIL ===
    if os.path.exists(FONT_PATH):
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_font("DejaVu", "", 12)
        font_used = "DejaVu"
    else:
        pdf.set_font("Arial", "", 12)
        font_used = "Arial"

    # === TITLU ===
    pdf.set_font(font_used, "B", 18)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "FEA Quiz Trainer - Raport Sesiune", new_y="NEXT", align="C")

    pdf.set_font(font_used, "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Mod: {result['mode'].capitalize()}", new_y="NEXT")
    pdf.cell(0, 10, f"Domeniu: {result['domain']}", new_y="NEXT")
    pdf.cell(0, 10, f"Scor: {result['score']}/{result['total']} ({result['percent']}%)", new_y="NEXT")
    pdf.cell(0, 10, f"Corecte: {result['correct']}, Greșite: {result['incorrect']}", new_y="NEXT")
    pdf.cell(0, 10, f"Timp utilizat: {result['time_used']} secunde", new_y="NEXT")
    pdf.cell(0, 10, f"Data: {result['date']}", new_y="NEXT")

    # === DETALII TRAIN MODE ===
    if answers:
        pdf.ln(8)
        pdf.set_font(font_used, "B", 14)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 10, "📘 Detalii întrebări (Train Mode):", new_y="NEXT")

        pdf.set_font(font_used, "", 11)
        pdf.set_text_color(0, 0, 0)
        for i, ans in enumerate(answers, 1):
            pdf.multi_cell(0, 8, f"{i}. {ans['question']}")
            pdf.cell(0, 8, f"✔ Corect: {ans['correct']}", new_y="NEXT")
            pdf.cell(0, 8, f"✖ Răspuns selectat: {ans['selected']}", new_y="NEXT")
            pdf.multi_cell(0, 8, f"💡 Explicație: {ans['explanation']}", new_y="NEXT")
            pdf.cell(0, 5, "--------------------------------------------", new_y="NEXT")

    # === Salvare PDF ===
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "last_session_report.pdf")
    pdf.output(output_path)
    print(f"[INFO] Raport PDF exportat cu succes: {output_path}")
