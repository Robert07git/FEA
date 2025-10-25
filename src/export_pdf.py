from fpdf import FPDF
import os
from datetime import datetime


class PDFReport(FPDF):
    def header(self):
        # Titlu header
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 255, 255)
        self.cell(0, 10, "FEA Quiz Report", ln=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def footer(self):
        # Footer cu pagină
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")


def generate_pdf_report(domain, mode, score, total, percent, results):
    """
    Creează un fișier PDF cu rezultatele quiz-ului.
    Include detalii despre întrebări greșite și explicații.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 200, 255)
    pdf.cell(0, 10, "Rezultate sesiune FEA Quiz", ln=True, align="C")
    pdf.ln(10)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.cell(0, 10, f"Data: {timestamp}", ln=True)
    pdf.cell(0, 10, f"Domeniu: {domain}", ln=True)
    pdf.cell(0, 10, f"Mod: {mode}", ln=True)
    pdf.cell(0, 10, f"Scor final: {score}/{total} ({percent:.1f}%)", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "Întrebări incorecte / Explicații:", ln=True)
    pdf.ln(5)

    incorrect = [r for r in results if not r["correct"]]

    if not incorrect:
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 10, "Ai răspuns corect la toate întrebările! Excelent!", ln=True)
    else:
        pdf.set_text_color(0, 0, 0)
        for r in incorrect:
            q = r["question"]
            correct = r["choices"][r["correct_index"]]
            explanation = r.get("explanation", "")
            pdf.multi_cell(0, 8, f"• {q}", align="L")
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, f"   Răspuns corect: {correct}", ln=True)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 8, f"   Explicație: {explanation}", align="L")
            pdf.ln(5)
            pdf.set_text_color(0, 0, 0)

    # Salvare fișier
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"FEA_Report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(reports_dir, filename)
    pdf.output(pdf_path)

    return pdf_path
