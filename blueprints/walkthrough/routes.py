from . import walkthrough_bp
from flask import render_template, flash, redirect, url_for, request, jsonify, send_file
from flask_login import login_required
from utils.walkthroughs import WALKTHROUGHS
from extensions import db
from utils.pdf_export import export_to_pdf
import os, json, datetime
from openai import OpenAI
from flask import current_app as app


@walkthrough_bp.route("s")
@login_required
def walkthrough_list():
    return render_template("walkthrough_list.html", walkthroughs=WALKTHROUGHS)


@walkthrough_bp.route("/<walk_id>")
@login_required
def walkthrough(walk_id):
    walkthrough = WALKTHROUGHS.get(walk_id)
    if not walkthrough:
        flash("Невалиден walkthrough ID.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    log_data = None
    if walkthrough.get("log_file"):
        try:
            path = os.path.join("instance", "logs", walkthrough["log_file"])
            with open(path, encoding="utf-8") as f:
                log_data = json.load(f)
        except Exception as e:
            flash(f"⚠️ Неуспешно зареждане на лог файл: {e}", "danger")

    return render_template("walkthrough.html",
                           scenario=walkthrough,
                           log_data=log_data)


@walkthrough_bp.route("/ai-feedback", methods=["POST"])
@login_required
def ai_walkthrough_feedback():
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    data = request.get_json()
    answers = data.get("answers", [])

    if not answers or not isinstance(answers, list):
        return jsonify({"feedback": "⚠️ Няма подадени отговори."})

    try:
        prompt = "Студентът предостави следните отговори по време на инцидентен анализ:\n\n"
        for i, ans in enumerate(answers, 1):
            prompt += f"{i}. {ans}\n"

        prompt += "\nДай кратка оценка на всеки отговор и обща оценка от 1 до 10.\nИзползвай ясен и приятелски тон на български."

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти си инструктор по киберсигурност, който дава обратна връзка."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_feedback = response.choices[0].message.content
        return jsonify({"feedback": ai_feedback})
    except Exception as e:
        return jsonify({"feedback": f"Грешка от AI: {str(e)}"})


@walkthrough_bp.route("/export-pdf", methods=["POST"])
@login_required
def walkthrough_pdf():
    data = request.get_json()
    steps = data.get("steps", [])
    answers = data.get("answers", [])
    feedback = data.get("feedback", "")

    if not steps or not answers:
        return "Missing data", 400

    content = ""
    for i, (step, answer) in enumerate(zip(steps, answers), 1):
        content += f"{i}. {step}\nОтговор: {answer}\n\n"

    content += "\n---\nAI обратна връзка:\n" + feedback

    filename = f"results/walkthrough_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("results", exist_ok=True)
    export_to_pdf(content, "", filename)

    return send_file(filename, as_attachment=True)
