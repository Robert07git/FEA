# pdf_exporter_modern.py — versiune 4.2.2 (fără erori FPDF)
from fpdf import FPDF
import os

FONT_PATH = os.path.join("data", "DejaVuSans.ttf")

def safe_text(text):
    """Curăță caracterele care pot rupe PDF-ul"""
    if not text:
        return ""
    return str(text).replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

def export_pdf_modern(result, answers=None):
    """Generează raport PDF complet cu suport Unicode"""
    pdf = FPDF()
    pdf.add_page()

    # ===== Fonturi =====
    if os.path.exists(FONT_PATH):
        pdf.add_font("DejaVuSans", "", FONT_PATH, uni=True)
        pdf.add_font("DejaVuSansBold", "", FONT_PATH, uni=True)
        base_font = "DejaVuSans"
        bold_font = "DejaVuSansBold"
    else:
        base_font = "Arial"
        bold_font = "Arial"

    # ===== Titlu =====
    pdf.set_font(bold_font, "", 18)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "FEA Quiz Trainer - Raport Sesiune", new_y="NEXT", align="C")

    # ===== Rezumat =====
    pdf.set_font(base_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Mod: {result['mode'].capitalize()}", new_y="NEXT")
    pdf.cell(0, 10, f"Domeniu: {result['domain']}", new_y="NEXT")
    pdf.cell(0, 10, f"Scor: {result['score']}/{result['total']} ({result['percent']}%)", new_y="NEXT")
    pdf.cell(0, 10, f"Corecte: {result['correct']}, Greșite: {result['incorrect']}", new_y="NEXT")
    pdf.cell(0, 10, f"Timp: {result['time_used']} secunde", new_y="NEXT")
    pdf.cell(0, 10, f"Data: {result['date']}", new_y="NEXT")

    # ===== Întrebări din TRAIN MODE =====
    if answers:
        pdf.ln(8)
        pdf.set_font(bold_font, "", 14)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 10, "📘 Detalii întrebări (Train Mode):", new_y="NEXT")

        pdf.set_font(base_font, "", 11)
        pdf.set_text_color(0, 0, 0)

        for i, ans in enumerate(answers, 1):
            q_text = safe_text(ans.get("question"))
            correct = safe_text(ans.get("correct"))
            selected = safe_text(ans.get("selected"))
            explanation = safe_text(ans.get("explanation"))

            pdf.multi_cell(0, 8, f"{i}. {q_text}", new_y="NEXT")
            pdf.cell(0, 8, f"✔ Corect: {correct}", new_y="NEXT")
            pdf.cell(0, 8, f"✖ Răspuns: {selected}", new_y="NEXT")
            pdf.multi_cell(0, 8, f"💡 Explicație: {explanation}", new_y="NEXT")
            pdf.cell(0, 5, "---------------------------------------------", new_y="NEXT")

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "last_session_report.pdf")

    try:
        pdf.output(output_path)
        print(f"[INFO] Raport PDF exportat cu succes: {output_path}")
    except Exception as e:
        print("[EROARE PDF]", e)
