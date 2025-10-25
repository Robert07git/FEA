from fpdf import FPDF
import os


def export_quiz_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()

        # ✅ Înlocuim fontul implicit cu unul Unicode
        # (vei adăuga fișierul TTF o singură dată)
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

        if not os.path.exists(font_path):
            # descarcă automat fontul dacă lipsește
            import urllib.request
            print("🔽 Se descarcă fontul DejaVuSans.ttf...")
            urllib.request.urlretrieve(
                "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf",
                font_path
            )

        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=14)

        pdf.cell(0, 10, "Raport FEA Quiz Trainer", ln=True, align="C")
        pdf.set_font("DejaVu", size=11)
        pdf.ln(10)
        pdf.cell(0, 10, "Istoric performanță:", ln=True)

        # citește istoricul dacă există
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_path = os.path.join(base_dir, "score_history.txt")

        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines[-15:]:
                pdf.multi_cell(0, 8, line.strip())
        else:
            pdf.cell(0, 10, "Nu există date salvate în score_history.txt.", ln=True)

        output_path = os.path.join(base_dir, "quiz_report.pdf")
        pdf.output(output_path)
        print(f"✅ PDF generat cu succes: {output_path}")

    except Exception as e:
        print("❌ Eroare la export PDF:", e)
