from flask import render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
import os
import datetime

from extensions import db
from . import dashboard_bp
from models.user import User
from models.ctf import CTFResult
from utils.ctf_missions import MISSIONS


@dashboard_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route('/api/dashboard-data', methods=['GET'])
@login_required
def dashboard_data():
    if current_user.role == "admin":
        user_count = User.query.count()
        ctf_count = CTFResult.query.count()
        leaderboard = (
            db.session.query(CTFResult.username)
            .group_by(CTFResult.username)
            .count()
        )
        return jsonify({
            "потребители": user_count,
            "ctf резултати": ctf_count,
            "класирани участници": leaderboard
        })

    elif current_user.role == "teacher":
        students = User.query.filter_by(role="student").count()
        missions = len(MISSIONS)
        reports = len([f for f in os.listdir("results") if f.endswith(".pdf")])
        return jsonify({
            "студенти": students,
            "мисии": missions,
            "pdf отчети": reports
        })

    else:
        results = CTFResult.query.filter_by(username=current_user.username).all()
        total = sum(r.points for r in results)
        completed = len(results)
        last = results[-1].timestamp.strftime("%Y-%m-%d %H:%M") if results else "Няма"
        return jsonify({
            "общо точки": total,
            "завършени мисии": completed,
            "последно участие": last
        })


@dashboard_bp.route('/leaderboard', methods=['GET'])
@login_required
def leaderboard():
    scores = (
        db.session.query(
            CTFResult.username,
            func.sum(CTFResult.points).label("total_points")
        )
        .group_by(CTFResult.username)
        .order_by(func.sum(CTFResult.points).desc())
        .all()
    )
    return render_template("leaderboard.html", scores=scores)


@dashboard_bp.route('/api/student-activity', methods=['GET'])
@login_required
def student_activity():
    if current_user.role != "student":
        return jsonify({})

    results = (
        CTFResult.query
        .with_entities(CTFResult.timestamp)
        .filter_by(username=current_user.username)
        .all()
    )
    timeline = {}
    for r in results:
        date = r.timestamp.date().isoformat()
        timeline[date] = timeline.get(date, 0) + 1

    return jsonify(timeline)
