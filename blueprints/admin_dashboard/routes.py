from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import and_
from datetime import datetime

from extensions import db
from models.ai_memory import AIMemory
from models.lesson import Lesson
from models.user import User
from models.activity_log import ActivityLog
from .forms import CreateUserForm, EditUserForm

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')


# Админ защита
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Достъп само за администратори.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# Лог запис
def log_action(user_id, action):
    log = ActivityLog(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()


# 🧭 Дашборд
@admin_dashboard_bp.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    lesson_count = Lesson.query.count()
    memory_count = AIMemory.query.count()
    teachers = User.query.filter_by(role='teacher').all()
    students = User.query.filter_by(role='student').all()

    username = request.args.get('username')
    date_str = request.args.get('date')

    logs_query = ActivityLog.query.join(User)

    if username:
        logs_query = logs_query.filter(User.username.ilike(f"%{username}%"))
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            logs_query = logs_query.filter(db.func.date(ActivityLog.timestamp) == date)
        except ValueError:
            flash("Невалидна дата.", "danger")

    logs = logs_query.order_by(ActivityLog.timestamp.desc()).limit(10).all()

    return render_template("admin/dashboard.html",
                           user_count=user_count,
                           lesson_count=lesson_count,
                           memory_count=memory_count,
                           teachers=teachers,
                           students=students,
                           logs=logs)


# ➕ Създаване на потребител
@admin_dashboard_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        log_action(current_user.id, f"Създаден потребител: {user.username}")

        flash("Потребителят е създаден успешно!", "success")
        return redirect(url_for('admin_dashboard.dashboard'))

    return render_template('admin/create_user.html', form=form)


# 📝 Редактиране на потребител
@admin_dashboard_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        db.session.commit()

        log_action(current_user.id, f"Редактиран потребител: {user.username}")

        flash("Потребителят е обновен.", "success")
        return redirect(url_for('admin_dashboard.dashboard'))

    return render_template('admin/edit_user.html', form=form, user=user)


# ❌ Изтриване на потребител
@admin_dashboard_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    log_action(current_user.id, f"Изтрит потребител: {user.username}")

    db.session.delete(user)
    db.session.commit()
    flash("Потребителят е изтрит.", "success")
    return redirect(url_for('admin_dashboard.dashboard'))
