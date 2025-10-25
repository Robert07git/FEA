from fpdf import FPDF
import os
import unicodedata

def remove_diacritics(text):
    """Elimină diacriticele (ăîșțâ -> a i s t a) pentru compatibilitate PDF."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def export_quiz_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Raport FEA Quiz Trainer", ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(0, 10, "Istoric performanta:", ln=True)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_path = os.path.join(base_dir, "score_history.txt")

        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if lines:
                for line in lines[-15:]:
                    clean_line = remove_diacritics(line.strip())
                    pdf.multi_cell(0, 8, clean_line)
            else:
                pdf.cell(0, 10, "Fisierul score_history.txt este gol.", ln=True)
        else:
            pdf.cell(0, 10, "Nu exista fisierul score_history.txt.", ln=True)

        output_path = os.path.join(base_dir, "quiz_report.pdf")
        pdf.output(output_path)
        print(f"✅ PDF generat cu succes: {output_path}")

    except Exception as e:
        print("❌ Eroare la export PDF:", e)
