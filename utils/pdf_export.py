from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def export_to_pdf(log_text: str, gpt_response: str, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)

    y = height - 40
    c.drawString(40, y, "CyberEdu AI SOC Report")
    y -= 30

    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Log:")
    y -= 20
    c.setFont("Helvetica", 10)

    for line in log_text.splitlines():
        c.drawString(40, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40

    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "GPT Analysis:")
    y -= 20
    c.setFont("Helvetica", 10)

    for line in gpt_response.splitlines():
        c.drawString(40, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40

    c.save()
