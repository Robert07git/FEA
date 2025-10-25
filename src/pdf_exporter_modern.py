# pdf_exporter_modern.py
from fpdf import FPDF
import os


def export_pdf_modern(result, answers=None):
    """
    Generează un PDF profesional cu datele sesiunii.
    Dacă answers este furnizat, include întrebările și explicațiile (pentru Train Mode).
    """
    pdf = FPDF()
    pdf.add_page()

    # Titlu
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "FEA Quiz Trainer - Raport Sesiune", new_y="NEXT", align="C")

    # Detalii generale
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Mod: {result['mode'].capitalize()}", new_y="NEXT")
    pdf.cell(0, 10, f"Domeniu: {result['domain']}", new_y="NEXT")
    pdf.cell(0, 10, f"Scor: {result['score']}/{result['total']} ({result['percent']}%)", new_y="NEXT")
    pdf.cell(0, 10, f"Corecte: {result['correct']}, Greșite: {result['incorrect']}", new_y="NEXT")
    pdf.cell(0, 10, f"Timp utilizat: {result['time_used']} secunde", new_y="NEXT")
    pdf.cell(0, 10, f"Data: {result['date']}", new_y="NEXT")

    # Detalii întrebări (numai Train Mode)
    if answers:
        pdf.ln(8)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 10, "📘 Detalii întrebări (Train Mode)", new_y="NEXT")
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(0, 0, 0)
        for i, ans in enumerate(answers, 1):
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 8, f"{i}. {ans['question']}")
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"✔ Corect: {ans['correct']}", new_y="NEXT")
            pdf.cell(0, 8, f"✖ Răspuns: {ans['selected']}", new_y="NEXT")
            pdf.multi_cell(0, 8, f"Explicație: {ans['explanation']}", new_y="NEXT")
            pdf.cell(0, 5, "--------------------------------", new_y="NEXT")

    # Salvare fișier
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "last_session_report.pdf")
    pdf.output(output_path)
    print(f"[INFO] Raport PDF generat: {output_path}")
