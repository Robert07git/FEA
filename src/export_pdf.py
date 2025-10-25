from fpdf import FPDF
import os
import urllib.request

def export_quiz_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()

        # ✅ Folder și font
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

        # ✅ Dacă lipsește fontul, îl descarcă dintr-o sursă stabilă
        if not os.path.exists(font_path):
            print("🔽 Se descarcă fontul DejaVuSans.ttf...")
            try:
                urllib.request.urlretrieve(
                    "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
                    font_path
                )
                print("✅ Font descărcat cu succes.")
            except Exception as e:
                print(f"❌ Eroare la descărcarea fontului: {e}")
                return

        # ✅ Încarcă fontul în FPDF cu suport Unicode
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=14)

        pdf.cell(0, 10, "Raport FEA Quiz Trainer", ln=True, align="C")
        pdf.set_font("DejaVu", size=11)
        pdf.ln(10)
        pdf.cell(0, 10, "Istoric performanță:", ln=True)

        # ✅ Citește istoricul
        history_path = os.path.join(base_dir, "score_history.txt")

        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                for line in lines[-15:]:
                    pdf.multi_cell(0, 8, line.strip())
            else:
                pdf.cell(0, 10, "Fișierul score_history.txt este gol.", ln=True)
        else:
            pdf.cell(0, 10, "Nu există fișierul score_history.txt.", ln=True)

        # ✅ Salvare PDF
        output_path = os.path.join(base_dir, "quiz_report.pdf")
        pdf.output(output_path)
        print(f"✅ PDF generat cu succes: {output_path}")

    except Exception as e:
        print("❌ Eroare la export PDF:", e)
