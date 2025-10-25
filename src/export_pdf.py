import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def read_last_session():
    """
    Citește ultima linie din score_history.txt și o întoarce ca dict:
    {
      "domeniu": ...,
      "mode": ...,
      "nq": ...,
      "pct": ...
    }
    """
    base_dir = os.path.dirname(__file__)
    hist_path = os.path.join(base_dir, "score_history.txt")

    if not os.path.exists(hist_path):
        raise FileNotFoundError("Nu există score_history.txt")

    lines = []
    with open(hist_path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if not lines:
        raise RuntimeError("Istoricul e gol")

    last = lines[-1]
    try:
        domeniu, mode, nq, pct = last.split(",")
    except ValueError:
        raise RuntimeError("Ultima linie din istoric are format invalid")

    return {
        "domain": domeniu,
        "mode": mode,
        "nq": nq,
        "pct": pct
    }


def generate_exam_report():
    """
    Creează un PDF simplu în /reports cu info din ultima sesiune.
    Returnează path-ul PDF-ului creat.
    """
    base_dir = os.path.dirname(__file__)
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    sess = read_last_session()

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_name = f"exam_report_{now}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_name)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0, 1, 1)  # turcoaz-ish
    c.drawString(50, y, "Raport FEA Quiz")
    y -= 40

    c.setFont("Helvetica", 11)
    c.setFillColorRGB(1,1,1)  # alb nu se vede pe pagină albă -> hai negru
    c.setFillColorRGB(0,0,0)

    c.drawString(50, y, f"Data generării: {now}")
    y -= 20
    c.drawString(50, y, f"Domeniu: {sess['domain']}")
    y -= 20
    c.drawString(50, y, f"Mod: {sess['mode']}")
    y -= 20
    c.drawString(50, y, f"Întrebări totale: {sess['nq']}")
    y -= 20
    c.drawString(50, y, f"Scor final: {sess['pct']}%")
    y -= 40

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Notă: Acesta este un raport sumar bazat pe ultima sesiune salvată în score_history.txt.")
    y -= 15
    c.drawString(50, y, "Pentru detalii complete (întrebări greșite / explicații) vom extinde raportul în versiunea următoare.")
    y -= 30

    c.showPage()
    c.save()

    return pdf_path


if __name__ == "__main__":
    path = generate_exam_report()
    print("PDF generat:", path)
