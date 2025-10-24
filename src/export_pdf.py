from fpdf import FPDF
import os
from datetime import datetime

def generate_exam_report():
    """
    Generează un raport PDF complet pentru ultima sesiune de quiz (din score_history.txt)
    Include detalii despre scor, mod, domeniu și grafic de progres (dacă există).
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(base_dir, "score_history.txt")
    chart_path = os.path.join(base_dir, "progress_chart.png")
    output_path = os.path.join(base_dir, "last_exam_report.pdf")

    if not os.path.exists(history_path):
        print("⚠️ Nu există fișierul score_history.txt — rulează cel puțin o sesiune de quiz EXAM.")
        return

    # Citim ultima sesiune
    with open(history_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        print("⚠️ Fișierul e gol — nu există sesiuni salvate.")
        return

    last_line = lines[-1]

    # Extragem informațiile principale
    try:
        parts = [p.strip() for p in last_line.split("|")]
        data = {
            "timestamp": parts[0],
            "domeniu": parts[1].split("=")[1],
            "mod": parts[2].split("=")[1],
            "scor": parts[3].split("=")[1],
            "procent": parts[4].split("=")[1],
            "timp_total": parts[5].split("=")[1],
            "timp_intrebare": parts[6].split("=")[1],
        }
    except Exception as e:
        print(f"Eroare la parsarea ultimei linii: {e}")
        return

    # ======== Creare PDF ========
    pdf = FPDF()
    pdf.add_page()

    # Antet
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_text_color(0, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "FEA Quiz Trainer", ln=True, align="C")
    pdf.ln(10)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Raport sesiune EXAM", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Data generării: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Timp sesiune: {data['timestamp']}", ln=True)
    pdf.ln(5)

    # Informații despre sesiune
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Domeniu: {data['domeniu']}", ln=True)
    pdf.cell(0, 8, f"Mod: {data['mod']}", ln=True)
    pdf.cell(0, 8, f"Scor: {data['scor']}", ln=True)
    pdf.cell(0, 8, f"Procent: {data['procent']}", ln=True)
    pdf.cell(0, 8, f"Timp total: {data['timp_total']}", ln=True)
    pdf.cell(0, 8, f"Timp per întrebare: {data['timp_intrebare']}", ln=True)
    pdf.ln(8)

    # Linie separator
    pdf.set_draw_color(0, 255, 255)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Grafic dacă există
    if os.path.exists(chart_path):
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, "Grafic progres general:", ln=True)
        pdf.image(chart_path, x=25, w=160)
        pdf.ln(10)
    else:
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 8, "Graficul nu este disponibil. Generează-l din aplicație înainte de export.", ln=True)
        pdf.ln(10)

    # Concluzie
    pdf.set_font("Arial", "I", 11)
    pct_value = float(data["procent"].replace("%", ""))
    if pct_value >= 85:
        msg = "Excelent! 🏆 Cunoștințele tale sunt foarte solide."
    elif pct_value >= 60:
        msg = "Bun! Mai ai puțin de lucru pentru perfecționare."
    else:
        msg = "Continuă să exersezi — progresul vine cu practica!"
    pdf.multi_cell(0, 8, f"Analiză automată: {msg}")
    pdf.ln(5)

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 10, "FEA Quiz Trainer © 2025 | Generat automat", 0, 0, "C")

    # Salvare PDF
    pdf.output(output_path)
    print(f"✅ Raport PDF generat cu succes: {output_path}")
