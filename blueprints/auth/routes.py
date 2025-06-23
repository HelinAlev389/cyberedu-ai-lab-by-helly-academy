from .forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from extensions import db, mail
from models.user import User

# auth blueprint setup
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Token utilities
def generate_reset_token(username):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(username, salt="reset-password")


def confirm_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.loads(token, salt="reset-password", max_age=expiration)

# Routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Потребителското име вече съществува.')
        else:
            u = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data
            )
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u and u.check_password(form.password.data):
            login_user(u)
            return redirect(url_for('dashboard.dashboard'))
        form.password.errors.append('Невалидно потребителско име или парола.')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            token = generate_reset_token(user.username)
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            msg = Message("Нулиране на парола", recipients=[user.email])
            msg.body = (
                f"Здравей,\n\n"
                f"Кликни тук за да нулираш паролата си:\n{reset_link}\n\n"
                "Поздрави, Helly Academy"
            )
            mail.send(msg)
        flash(
            "Ако съществува акаунт с този имейл/потребителско име, ще получиш линк за нулиране на паролата.",
            "info"
        )
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        username = confirm_reset_token(token)
    except Exception:
        flash("Невалиден или изтекъл линк.", "danger")
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash("Паролата е обновена успешно. Влез с новата си парола.", "success")
            return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)


def auth():
    return None