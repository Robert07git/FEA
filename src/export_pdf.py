from fpdf import FPDF
import os

def export_quiz_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()

        # Folosește Arial (standard, fără descărcare)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Raport FEA Quiz Trainer", ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(0, 10, "Istoric performanta:", ln=True)

        # Citește fișierul de scoruri
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_path = os.path.join(base_dir, "score_history.txt")

        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if lines:
                for line in lines[-15:]:
                    try:
                        # elimină caractere care pot cauza erori
                        clean_line = line.encode("latin-1", "replace").decode("latin-1")
                        pdf.multi_cell(0, 8, clean_line.strip())
                    except:
                        pdf.multi_cell(0, 8, "[linie nevalidă]")
            else:
                pdf.cell(0, 10, "Fișierul score_history.txt este gol.", ln=True)
        else:
            pdf.cell(0, 10, "Nu există fișierul score_history.txt.", ln=True)

        # Salvare PDF
        output_path = os.path.join(base_dir, "quiz_report.pdf")
        pdf.output(output_path)
        print(f"✅ PDF generat cu succes: {output_path}")

    except Exception as e:
        print("❌ Eroare la export PDF:", e)
