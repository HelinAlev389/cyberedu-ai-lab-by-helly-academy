import os

from flask import Blueprint, render_template, request, flash, session, redirect, url_for, json, send_file
from flask_login import login_required, current_user
from models.ctf import CTFResult
from utils.ctf_missions import MISSIONS
from utils.ai_feedback import get_ctf_feedback
from utils.save_ctf_response import save_ctf_report
from extensions import db

ctf_bp = Blueprint('ctf', __name__, url_prefix='/ctf')


@ctf_bp.route('/', methods=['GET'])
@login_required
def overview():
    return render_template('ctf_overview.html', missions=MISSIONS)


@ctf_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("ctf/dashboard.html")


@ctf_bp.route('/<mission_id>/tier/<tier>', methods=['GET', 'POST'])
@login_required
def ctf_mission(mission_id, tier, answers=None):
    mission = MISSIONS.get(mission_id)
    if not mission or tier not in mission["tiers"]:
        return "Невалидна мисия или Tier", 404

    tier_data = mission["tiers"][tier]

    if request.method == 'POST':
        answers = [request.form.get(f'answer{i + 1}') for i in range(len(tier_data["questions"]))]

        if not all(answers):
            flash("Моля, попълни всички отговори преди да предадеш мисията.", "warning")
            return render_template('ctf.html', mission=mission, tier_data=tier_data, tier=tier)

        log_data = None
        if "log_file" in mission:
            log_path = os.path.join("instance", "logs", mission["log_file"])
            try:
                with open(log_path, encoding="utf-8") as f:
                    log_data = json.load(f)
            except Exception as e:
                flash(f"Неуспешно зареждане на лог файл: {e}", "danger")

        #  AI Feedback (с log_data, ако е наличен)
        ai_feedback = get_ctf_feedback(
            current_user.username,
            mission_id,
            tier,
            tier_data["questions"],
            answers,
            log_data=log_data
        )
        session['ai_feedback'] = ai_feedback

        filename = save_ctf_report(current_user.username, mission_id, tier, answers)
        session['last_ctf_pdf'] = filename

        points_by_tier = {"1": 10, "2": 20, "3": 30}
        points = points_by_tier.get(tier, 0)

        result = CTFResult(
            username=current_user.username,
            mission_id=mission_id,
            tier=tier,
            points=points
        )
        db.session.add(result)
        db.session.commit()

        flash(f"CTF приключена! Точки: {points} | Генериран PDF: {filename}", "success")
        return redirect(url_for('ctf.result'))

    log_data = None
    if "log_file" in mission:
        log_path = os.path.join("instance", "logs", mission["log_file"])
        try:
            with open(log_path, encoding="utf-8") as f:
                log_data = json.load(f)
        except Exception as e:
            flash(f" Неуспешно зареждане на лог файл: {e}", "danger")

    return render_template('ctf.html', mission=mission, tier_data=tier_data, tier=tier, log_data=log_data)


@ctf_bp.route('/result')
@login_required
def result():
    filename = session.get('last_ctf_pdf')
    return render_template('ctf_result.html', filename=filename)


@ctf_bp.route('/download/<filename>')
@login_required
def download(filename):
    return send_file(os.path.join("results", filename), as_attachment=True)


def ctf():
    return None