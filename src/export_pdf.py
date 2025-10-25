from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import unicodedata

def remove_diacritics(text):
    """Elimină diacriticele (ăîșțâ -> a i s t a) pentru compatibilitate PDF."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def generate_progress_chart(scores, timestamps, output_path):
    """Generează graficul de progres și îl salvează ca imagine PNG."""
    plt.figure(figsize=(6, 3))
    plt.plot(timestamps, scores, marker='o', linewidth=2)
    plt.title("Evolutia scorului in timp")
    plt.xlabel("Data")
    plt.ylabel("Procent (%)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def export_quiz_pdf():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_path = os.path.join(base_dir, "score_history.txt")
        chart_path = os.path.join(base_dir, "progress_chart.png")
        output_path = os.path.join(base_dir, "quiz_report.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Raport FEA Quiz Trainer", ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(0, 10, "Istoric performanta:", ln=True)

        scores = []
        timestamps = []

        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if lines:
                for line in lines[-15:]:
                    clean_line = remove_diacritics(line.strip())
                    pdf.multi_cell(180, 8, clean_line)
                    pdf.ln(1)

                    # Extrage procentul pentru grafic
                    parts = clean_line.split("procent=")
                    if len(parts) > 1:
                        try:
                            pct = float(parts[1].split("%")[0])
                            scores.append(pct)
                            timestamps.append(clean_line.split("|")[0].strip())
                        except:
                            pass
            else:
                pdf.cell(0, 10, "Fisierul score_history.txt este gol.", ln=True)
        else:
            pdf.cell(0, 10, "Nu exista fisierul score_history.txt.", ln=True)

        # ✅ Generează graficul dacă există date
        if scores:
            generate_progress_chart(scores, timestamps, chart_path)
            pdf.ln(10)
            pdf.cell(0, 10, "Grafic de progres:", ln=True)
            pdf.image(chart_path, x=15, w=180)

        pdf.output(output_path)
        print(f"✅ PDF generat cu succes: {output_path}")

    except Exception as e:
        print("❌ Eroare la export PDF:", e)
