import os
import io
import json
import zipfile
import datetime

from dotenv import load_dotenv
from flask import (
    Flask, request, jsonify, render_template,
    redirect, url_for, send_file
)
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user, login_required, current_user
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from utils.pdf_export import export_to_pdf

load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "supersecret123")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

openai_client = OpenAI()

# --- Models ---

class User(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(80), unique=True, nullable=False)
    password    = db.Column(db.String(200), nullable=False)
    first_name  = db.Column(db.String(80), nullable=False)
    last_name   = db.Column(db.String(80), nullable=False)
    role        = db.Column(db.String(20), nullable=False)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Forms ---

class RegistrationForm(FlaskForm):
    first_name = StringField('Име', validators=[DataRequired(), Length(1, 80)])
    last_name  = StringField('Фамилия', validators=[DataRequired(), Length(1, 80)])
    username   = StringField('Потребителско име', validators=[DataRequired(), Length(4, 80)])
    password   = PasswordField('Парола', validators=[DataRequired(), Length(6, 200)])
    role       = SelectField('Роля', choices=[
                    ('student', 'Студент'),
                    ('teacher','Преподавател'),
                    ('admin','Администратор')],
                    validators=[DataRequired()])
    submit     = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    submit   = SubmitField('Вход')


# --- Prompt builder ---

def build_prompt(log: str) -> str:
    return f"""
You are an AI SOC Analyst designed to educate students on cyber incidents.

Task:
1. Identify the type of incident in the log (e.g., brute-force, phishing).
2. Assess the risk level (Low, Medium, High).
3. Explain what is happening in simple, educational language.
4. Suggest a prevention or response recommendation.

Here is the log to analyze:
{log}
"""


# --- Routes ---

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Потребителското име вече съществува.')
        else:
            u = User(
                username   = form.username.data,
                first_name = form.first_name.data,
                last_name  = form.last_name.data,
                role       = form.role.data
            )
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u and u.check_password(form.password.data):
            login_user(u)
            return redirect(url_for('dashboard'))
        form.password.errors.append('Невалидно потребителско име или парола.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/analyze-log', methods=['POST'])
@login_required
def analyze_log():
    log_raw = request.json.get("log", "")
    try:
        json.loads(log_raw)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"answer": "Грешка: логът не е валиден JSON."})

    prompt = build_prompt(log_raw)
    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content":"You are a cybersecurity teacher and SOC analyst."},
            {"role":"user",   "content":prompt}
        ]
    )
    result = resp.choices[0].message.content

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)
    txt_path = f"results/{ts}_result.txt"
    pdf_path = f"results/{ts}_result.pdf"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Log:\n{log_raw}\n\n---\nGPT Response:\n{result}")
    export_to_pdf(log_raw, result, pdf_path)

    return jsonify({"answer": result})


@app.route('/analyze-all', methods=['POST'])
@login_required
def analyze_all():
    logs_dir = "logs"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    summary = []

    if not os.path.exists(logs_dir):
        return jsonify({"summary": [], "error": "Logs folder not found."})

    for fn in os.listdir(logs_dir):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(logs_dir, fn)
        with open(path, "r", encoding="utf-8") as f:
            log = f.read()
        if not log.strip():
            summary.append({"file":fn, "status":"Skipped"})
            continue

        try:
            json.loads(log)
            prompt = build_prompt(log)
            resp = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role":"system", "content":"You are a cybersecurity teacher and SOC analyst."},
                    {"role":"user",   "content":prompt}
                ]
            )
            result = resp.choices[0].message.content

            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            txt_name = f"{os.path.splitext(fn)[0]}_{ts}_result.txt"
            pdf_name = f"{os.path.splitext(fn)[0]}_{ts}_result.pdf"
            txt_path = os.path.join(results_dir, txt_name)
            pdf_path = os.path.join(results_dir, pdf_name)

            with open(txt_path, "w", encoding="utf-8") as out:
                out.write(f"Log:\n{log}\n\n---\nGPT Response:\n{result}")
            export_to_pdf(log, result, pdf_path)

            summary.append({"file":fn, "status":"OK"})
        except Exception as e:
            summary.append({"file":fn, "status":f"Error: {e}"})

    return jsonify({"summary": summary})


@app.route('/reports')
@login_required
def reports():
    files = sorted(
        [f for f in os.listdir("results") if f.endswith(".pdf")],
        reverse=True
    )
    return render_template('reports.html', reports=files)


@app.route('/export')
@login_required
def export_zip():
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w") as zf:
        for f in os.listdir("results"):
            if f.endswith((".txt", ".pdf")):
                zf.write(os.path.join("results", f), arcname=f)
    mem.seek(0)
    return send_file(mem, download_name="helly_ai_reports.zip", as_attachment=True)


@app.route('/clear-results', methods=['POST'])
@login_required
def clear_results():
    deleted = []
    for f in os.listdir("results"):
        if f.endswith((".txt", ".pdf")):
            try:
                os.remove(os.path.join("results", f))
                deleted.append(f)
            except:
                pass
    return jsonify({"deleted": deleted})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
