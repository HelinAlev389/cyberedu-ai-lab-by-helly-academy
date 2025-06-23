from fpdf import FPDF
import os
from datetime import datetime
from flask import session

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "", 12)
        self.cell(0, 10, "SOC CTF Доклад", ln=True, align="C")

def save_ctf_report(user, mission_id, tier, answers):
    filename = f"{user}_{mission_id}_Tier{tier}.pdf"
    filepath = os.path.join("results", filename)

    os.makedirs("results", exist_ok=True)

    pdf = PDF()

    font_path = os.path.join("static", "fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)

    pdf.cell(0, 10, txt=f"Мисия: {mission_id} | Tier {tier}", ln=True)
    pdf.cell(0, 10, txt=f"Потребител: {user}", ln=True)
    pdf.cell(0, 10, txt=f"Дата: {datetime.utcnow()}", ln=True)
    pdf.ln(10)

    for i, a in enumerate(answers, 1):
        pdf.multi_cell(0, 10, f"Въпрос {i}:\n{a}\n")

    # 🔁 ТУК е мястото за AI обратна връзка, ако я има
    if 'ai_feedback' in session:
        pdf.add_page()
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 10, "AI обратна връзка:\n\n" + session['ai_feedback'])

    pdf.output(filepath)
    return filename
