import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_latest_exam_review_txt():
    """
    Caută în directorul proiectului fișiere de forma exam_review_YYYY-MM-DD_HH-MM.txt
    și îl întoarce pe cel mai nou. Dacă nu există, returnează None.
    """
    files = []
    for name in os.listdir(BASE_DIR):
        if name.startswith("exam_review_") and name.endswith(".txt"):
            full = os.path.join(BASE_DIR, name)
            files.append((name, full))

    if not files:
        return None

    # sortăm descrescător după nume (timestampul e în nume)
    files.sort(reverse=True)
    return files[0]  # (name, path)

def export_txt_to_pdf(txt_path, pdf_path):
    """
    Desenează conținutul .txt într-un PDF simplu (A4, text liniar).
    """
    # citește conținutul txt
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # margini
    x_left = 2 * cm
    y = height - 2 * cm

    # titlu
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_left, y, "Raport EXAM - FEA Quiz")
    y -= 1 * cm

    c.setFont("Helvetica", 10)

    for line in lines:
        # dacă nu mai avem loc pe pagină -> pagină nouă
        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 2 * cm

        # scriem linia
        c.drawString(x_left, y, line)
        y -= 0.5 * cm

    c.save()


def main():
    latest = find_latest_exam_review_txt()
    if not latest:
        print("Nu am găsit niciun fișier exam_review_*.txt. Rulează întâi un EXAM.")
        return

    txt_name, txt_path = latest
    # exam_review_2025-10-24_23-05.txt -> .pdf
    pdf_name = txt_name.replace(".txt", ".pdf")
    pdf_path = os.path.join(BASE_DIR, pdf_name)

    export_txt_to_pdf(txt_path, pdf_path)

    print("PDF generat cu succes:")
    print(pdf_path)


if __name__ == "__main__":
    main()
