from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from .forms import LoginForm
from models.user import User
from models.activity_log import ActivityLog

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # или към dashboard

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)

            log = ActivityLog(user_id=user.id, action="Успешен вход")
            db.session.add(log)
            db.session.commit()

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard.test_dashboard'))
            else:
                return redirect(url_for('main.index'))

        flash("Грешно потребителско име или парола.", "danger")

    # ⚠️ това гарантира, че винаги се връща валиден отговор
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Тук логика за регистрация
    return render_template('register.html')

@auth_bp.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Излязохте успешно.", "info")
    return redirect(url_for('auth.login'))
