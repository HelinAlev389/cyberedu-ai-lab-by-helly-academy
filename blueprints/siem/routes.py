from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required
from collections import Counter
from openai import OpenAI
from wtforms.fields import datetime

from utils.pdf_export import export_to_pdf, sanitize_filename
import os, json

siem_bp = Blueprint('siem', __name__, url_prefix='/siem')
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@siem_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    logs_path = os.path.join("instance", "logs")
    log_files = [f for f in os.listdir(logs_path) if f.endswith(".json")] if os.path.exists(logs_path) else []
    return render_template("siem.html", log_files=log_files, chart_data=None)

@siem_bp.route('/analyze', methods=['POST'])
@login_required
def siem_analyze():
    logs_path = os.path.join("instance", "logs")
    log_files = [f for f in os.listdir(logs_path) if f.endswith(".json")] if os.path.exists(logs_path) else []
    logfile = request.form.get("logfile")
    filepath = os.path.join(logs_path, logfile)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("Невалиден лог формат – очаква се списък или речник.")
        if not all(isinstance(d, dict) for d in data):
            raise ValueError("Някои записи не са речници.")

        event_types = [entry.get("event_type") or entry.get("event") or "unknown" for entry in data]
        counts = Counter(event_types)

        ai_suggestions = {
            "failed_login": "Прегледай акаунта и активирай допълнителна автентикация.",
            "privilege_escalation": "Изолирай машината и провери за експлойти.",
            "suspicious": "Направи задълбочен поведенчески анализ.",
            "unknown": "Извърши ръчна проверка.",
            "invalid": "Невалиден запис – провери структурата на лога."
        }

        chart_data = {
            "labels": list(counts.keys()),
            "values": [int(v) for v in counts.values()],
            "tooltips": [ai_suggestions.get(k, "Няма препоръка.") for k in counts]
        }

        prompt = f"Анализирай SOC лог:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти си SOC анализатор."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_output = response.choices[0].message.content

        return render_template(
            "siem.html",
            log_files=log_files,
            log=json.dumps(data, indent=2, ensure_ascii=False),
            ai_analysis=ai_output,
            chart_data=chart_data,
            data=data
        )
    except Exception as e:
        flash(f"Грешка при анализ: {e}", "danger")
        return render_template(
            "siem.html",
            log_files=log_files,
            log="",
            ai_analysis="",
            chart_data=None
        )

@siem_bp.route('/upload', methods=['POST'])
@login_required
def upload_log():
    file = request.files.get("logfile")
    if not file:
        flash("Не е избран файл.", "danger")
        return redirect(url_for("siem.dashboard"))
    if not file.filename.endswith(".json"):
        flash("Само .json файлове са позволени.", "warning")
        return redirect(url_for("siem.dashboard"))

    logs_path = os.path.join("instance", "logs")
    os.makedirs(logs_path, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{file.filename}"
    file.save(os.path.join(logs_path, filename))

    flash("Файлът е качен успешно!", "success")
    return redirect(url_for("siem.dashboard"))

@siem_bp.route('/clear', methods=['POST'])
@login_required
def clear_uploaded_logs():
    logs_path = os.path.join("instance", "logs")
    deleted = []
    if os.path.exists(logs_path):
        for f in os.listdir(logs_path):
            if f.endswith(".json"):
                try:
                    os.remove(os.path.join(logs_path, f))
                    deleted.append(f)
                except Exception as e:
                    flash(f"Грешка при изтриване на {f}: {e}", "danger")
    msg = f"Изтрити {len(deleted)} лог файла." if deleted else "Няма лог файлове за изтриване."
    flash(msg, "success" if deleted else "info")
    return redirect(url_for("siem.dashboard"))

@siem_bp.route('/export-pdf', methods=['GET', 'POST'])
@login_required
def export_pdf():
    # Redirect GET requests back to dashboard to avoid Method Not Allowed
    if request.method == 'GET':
        return redirect(url_for('siem.dashboard'))

    log_json = request.form.get("log_data")
    ai_output = request.form.get("ai_output")
    if not log_json or not ai_output:
        flash("Грешка: липсват данни за PDF.", "danger")
        return redirect(url_for("siem.dashboard"))
    try:
        log_data = json.loads(log_json)
        entry = log_data[0] if isinstance(log_data, list) and log_data else {}
        event_type = sanitize_filename(entry.get("event_type", "event"))
        user = sanitize_filename(entry.get("user", "user"))
        ts = sanitize_filename(entry.get("timestamp", "timestamp"))

        report_dir = os.path.join("results")
        os.makedirs(report_dir, exist_ok=True)
        out_file = os.path.join(report_dir, f"soc_report_{event_type}_{user}_{ts}.pdf")
        export_to_pdf(json.dumps(log_data, indent=2, ensure_ascii=False), ai_output, out_file)
        return send_file(out_file, as_attachment=True)
    except Exception as e:
        flash(f"Грешка при генериране на PDF: {e}", "danger")
        return redirect(url_for("siem.dashboard"))