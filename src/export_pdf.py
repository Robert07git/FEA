import os
from fpdf import FPDF
from datetime import datetime

def generate_exam_report():
    file_path = os.path.join(os.path.dirname(__file__), "score_history.txt")
    if not os.path.exists(file_path):
        print("Nu există date pentru export.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines:
            print("Nicio sesiune disponibilă.")
            return
        last_session = lines[-1].split(",")

    if len(last_session) < 4:
        print("Format invalid în istoricul scorurilor.")
        return

    domain, mode, total, score = last_session
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FEA Quiz - Raport sesiune", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Data generării: {now}", ln=True)
    pdf.cell(0, 10, f"Domeniu: {domain}", ln=True)
    pdf.cell(0, 10, f"Mod: {mode}", ln=True)
    pdf.cell(0, 10, f"Întrebări totale: {total}", ln=True)
    pdf.cell(0, 10, f"Scor obținut: {score}%", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 10, "Felicitări pentru progres! Continuă să exersezi în mod regulat pentru a-ți consolida cunoștințele în FEA și simulare numerică.")

    pdf_path = os.path.join(os.path.dirname(__file__), f"Raport_FEA_{domain}_{mode}.pdf")
    pdf.output(pdf_path)
    print(f"PDF generat: {pdf_path}")
