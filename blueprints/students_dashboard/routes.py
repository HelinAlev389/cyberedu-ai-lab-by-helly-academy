from flask import Blueprint, render_template, redirect, flash
from flask_login import login_required, current_user
from models.ai_memory import AIMemory
from models.lesson import Lesson

student_dashboard_bp = Blueprint('student_dashboard', __name__, url_prefix='/student')


@student_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash("Само студенти имат достъп до това табло.", "danger")
        return redirect('/')

    # AI памет за текущия студент
    memories = AIMemory.query.filter_by(user_id=current_user.id).order_by(AIMemory.created_at.desc()).all()

    # Уроци (по избор)
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(5).all()

    return render_template('student/dashboard.html',
                           memories=memories,
                           lessons=lessons)
