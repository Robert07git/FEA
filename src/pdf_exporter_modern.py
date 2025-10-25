# pdf_exporter_modern.py — versiunea 5.1 FINAL (ReportLab + bar chart)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

def export_pdf_modern(result, answers=None):
    """Generează raport PDF complet, cu diagramă de scor"""
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "last_session_report.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    story = []

    # === Stiluri ===
    title_style = ParagraphStyle(
        name="Title",
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0066cc")
    )

    subtitle_style = ParagraphStyle(
        name="Subtitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        spaceBefore=12,
        textColor=colors.HexColor("#009999")
    )

    normal_style = ParagraphStyle(
        name="Normal",
        fontName="Helvetica",
        fontSize=11,
        alignment=TA_LEFT,
        leading=15
    )

    # === Titlu ===
    story.append(Paragraph("FEA Quiz Trainer - Raport sesiune", title_style))
    story.append(Spacer(1, 20))

    # === Rezumat ===
    story.append(Paragraph(f"<b>Mod:</b> {result['mode'].capitalize()}", normal_style))
    story.append(Paragraph(f"<b>Domeniu:</b> {result['domain']}", normal_style))
    story.append(Paragraph(f"<b>Scor:</b> {result['score']} / {result['total']} ({result['percent']}%)", normal_style))
    story.append(Paragraph(f"<b>Corecte:</b> {result['correct']} | <b>Greșite:</b> {result['incorrect']}", normal_style))
    story.append(Paragraph(f"<b>Timp folosit:</b> {result['time_used']} secunde", normal_style))
    story.append(Paragraph(f"<b>Data:</b> {result['date']}", normal_style))
    story.append(Spacer(1, 25))

    # === Inserăm grafic (bar chart) ===
    def draw_chart(canv, width, height):
        canv.saveState()

        total = result['total']
        correct = result['correct']
        incorrect = result['incorrect']
        if total == 0:
            total = 1

        correct_ratio = correct / total
        incorrect_ratio = incorrect / total

        x_start = 4 * cm
        y_start = height - 6 * cm
        bar_width = 10 * cm
        bar_height = 1 * cm

        # Fundal
        canv.setFillColor(colors.grey)
        canv.rect(x_start, y_start, bar_width, bar_height, fill=True, stroke=0)

        # Corecte (verde)
        canv.setFillColor(colors.green)
        canv.rect(x_start, y_start, bar_width * correct_ratio, bar_height, fill=True, stroke=0)

        # Greșite (roșu)
        canv.setFillColor(colors.red)
        canv.rect(x_start + bar_width * correct_ratio, y_start, bar_width * incorrect_ratio, bar_height, fill=True, stroke=0)

        # Text
        canv.setFont("Helvetica-Bold", 12)
        canv.setFillColor(colors.black)
        canv.drawCentredString(x_start + bar_width / 2, y_start - 10, f"Corecte: {correct}  |  Greșite: {incorrect}")
        canv.restoreState()

    # Salvăm funcția pentru pagină
    def on_first_page(canv, doc):
        draw_chart(canv, A4[0], A4[1])

    # === Detalii întrebări (pentru Train Mode) ===
    if answers:
        story.append(Spacer(1, 100))
        story.append(Paragraph("📘 <b>Detalii întrebări (Train Mode):</b>", subtitle_style))
        story.append(Spacer(1, 12))

        for i, ans in enumerate(answers, 1):
            q = ans.get("question", "Întrebare lipsă")
            correct = ans.get("correct", "-")
            selected = ans.get("selected", "-")
            expl = ans.get("explanation", "-")

            story.append(Paragraph(f"<b>{i}. {q}</b>", normal_style))
            story.append(Paragraph(f"✔ <b>Corect:</b> {correct}", normal_style))
            story.append(Paragraph(f"✖ <b>Răspuns:</b> {selected}", normal_style))
            story.append(Paragraph(f"💡 <b>Explicație:</b> {expl}", normal_style))
            story.append(Spacer(1, 10))

    try:
        doc.build(story, onFirstPage=on_first_page)
        print(f"[INFO] Raport PDF generat cu succes: {output_path}")
        return output_path
    except Exception as e:
        print("[EROARE PDF]", e)
        return None
