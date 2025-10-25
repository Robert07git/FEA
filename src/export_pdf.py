from fpdf import FPDF
import os
import time

def generate_exam_report():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hist_path = os.path.join(base_dir, "score_history.txt")
    out_path = os.path.join(base_dir, f"Exam_Report_{time.strftime('%Y%m%d_%H%M')}.pdf")

    if not os.path.exists(hist_path):
        raise FileNotFoundError("Nu există score_history.txt pentru a genera PDF-ul.")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "FEA Exam Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)

    with open(hist_path, "r", encoding="utf-8") as f:
        for line in f:
            pdf.multi_cell(0, 8, txt=line.strip())

    pdf.output(out_path)
    print(f"✅ Raport PDF salvat: {out_path}")
