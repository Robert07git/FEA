# pdf_exporter_modern.py — versiune 4.3 FINAL (curățare completă + mesaj confirmare)
from fpdf import FPDF
import os
import re

FONT_PATH = os.path.join("data", "DejaVuSans.ttf")

def clean_text(text):
    """Curăță și limitează textul pentru PDF"""
    if not text:
        return ""
    text = str(text)
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = re.sub(r"[^a-zA-Z0-9ăâîșțĂÂÎȘȚ .,;:!?()\\-/]", "", text)  # elimină simboluri neafișabile
    return text.strip()[:400]  # limitează la 400 caractere / linie

def export_pdf_modern(result, answers=None):
    """Generează raport PDF complet, sigur pentru orice text"""
    pdf = FPDF()
    pdf.add_page()

    # Fonturi cu suport Unicode
    if os.path.exists(FONT_PATH):
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.add_font("DejaVuB", "", FONT_PATH, uni=True)
        base_font = "DejaVu"
        bold_font = "DejaVuB"
    else:
        base_font = bold_font = "Arial"

    # Titlu principal
    pdf.set_font(bold_font, "", 18)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 12, "FEA Quiz Trainer - Raport Sesiune", new_y="NEXT", align="C")

    # Rezumat
    pdf.set_font(base_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Mod: {result['mode'].capitalize()}", new_y="NEXT")
    pdf.cell(0, 10, f"Domeniu: {result['domain']}", new_y="NEXT")
    pdf.cell(0, 10, f"Scor: {result['score']}/{result['total']} ({result['percent']}%)", new_y="NEXT")
    pdf.cell(0, 10, f"Corecte: {result['correct']} | Greșite: {result['incorrect']}", new_y="NEXT")
    pdf.cell(0, 10, f"Timp folosit: {result['time_used']} secunde", new_y="NEXT")
    pdf.cell(0, 10, f"Data: {result['date']}", new_y="NEXT")

    # Detalii TRAIN MODE
    if answers:
        pdf.ln(8)
        pdf.set_font(bold_font, "", 14)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 10, "📘 Detalii întrebări (Train Mode):", new_y="NEXT")

        pdf.set_font(base_font, "", 11)
        pdf.set_text_color(0, 0, 0)

        for i, ans in enumerate(answers, 1):
            try:
                q_text = clean_text(ans.get("question"))
                correct = clean_text(ans.get("correct"))
                selected = clean_text(ans.get("selected"))
                explanation = clean_text(ans.get("explanation"))

                pdf.multi_cell(0, 8, f"{i}. {q_text}", new_y="NEXT")
                pdf.multi_cell(0, 8, f"✔ Corect: {correct}", new_y="NEXT")
                pdf.multi_cell(0, 8, f"✖ Răspuns: {selected}", new_y="NEXT")
                pdf.multi_cell(0, 8, f"💡 Explicație: {explanation}", new_y="NEXT")
                pdf.cell(0, 5, "-" * 90, new_y="NEXT")
            except Exception as e:
                pdf.multi_cell(0, 8, f"[Eroare afișare întrebare {i}]: {e}", new_y="NEXT")

    # Salvare fișier
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "last_session_report.pdf")

    try:
        pdf.output(output_path)
        print(f"[INFO] Raport PDF exportat cu succes: {output_path}")
        return output_path
    except Exception as e:
        print("[EROARE PDF]", e)
        return None
