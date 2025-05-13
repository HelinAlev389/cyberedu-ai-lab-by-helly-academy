import datetime
import os
import time

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

openai_client = OpenAI()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegistrationForm(FlaskForm):
    first_name = StringField('Име', validators=[DataRequired(), Length(1, 80)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(1, 80)])
    username = StringField('Потребителско име', validators=[DataRequired(), Length(4, 80)])
    password = PasswordField('Парола', validators=[DataRequired(), Length(6, 200)])
    role = SelectField('Роля',
                       choices=[('student', 'Студент'), ('teacher', 'Преподавател'), ('admin', 'Администратор')])
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    submit = SubmitField('Вход')


def build_prompt(log: str) -> str:
    return f"""
You are an AI SOC Analyst designed to educate students on cyber incidents.

Task:
1. Identify incident type.
2. Assess risk level.
3. Explain simply.
4. Recommend action.

Log:
{log}
"""


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Потребителското име е заето.')
        else:
            user = User(username=form.username.data, first_name=form.first_name.data,
                        last_name=form.last_name.data, role=form.role.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        form.password.errors.append('Грешно име или парола.')
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
    log = request.json.get("log", "")
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": build_prompt(log)}]
    ).choices[0].message.content

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)
    txt_path = f"results/{timestamp}_result.txt"
    pdf_path = f"results/{timestamp}_result.pdf"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(response)

    export_to_pdf(log, response, pdf_path)

    return jsonify({"answer": response})


@app.route('/reports')
@login_required
def reports():
    files = sorted([f for f in os.listdir("results") if f.endswith(".pdf")], reverse=True)
    return render_template('reports.html', reports=files)


@app.route('/scenarios')
@login_required
def scenarios():
    files = sorted(f for f in os.listdir("logs") if f.endswith(".json"))
    return render_template("scenarios.html", scenarios=files)


@app.route('/scenarios/<name>')
@login_required
def load_scenario(name):
    path = os.path.join("logs", name)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return render_template("index.html", preloaded_log=content)


@app.route('/upload-scenario', methods=['POST'])
@login_required
def upload_scenario():
    if 'file' not in request.files:
        flash("Файлът липсва.", "danger")
        return redirect(url_for('scenarios'))

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.json'):
        flash("Моля, качете валиден .json файл.", "warning")
        return redirect(url_for('scenarios'))

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{file.filename}"
    save_path = os.path.join('logs', filename)
    file.save(save_path)

    flash(f"Сценарият '{file.filename}' беше качен успешно.", "success")
    return redirect(url_for('scenarios'))


@app.route("/scenarios/delete/<name>", methods=["POST"])
@login_required
def delete_scenario(name):
    if current_user.role not in ["teacher", "admin"]:
        return "Недостатъчни права", 403

    path = os.path.join("logs", name)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Сценарият '{name}' беше изтрит.", "warning")
    else:
        flash("Файлът не съществува.", "danger")

    return redirect(url_for("scenarios"))


@app.route('/walkthrough-feedback', methods=['POST'])
@login_required
def walkthrough_feedback():
    data = request.json
    question = data.get("question", "")
    answer = data.get("answer", "")

    if not question or not answer:
        return jsonify({"feedback": "Грешка: липсва въпрос или отговор."}), 400

    prompt = f"""
You are an AI assistant helping a student learn cybersecurity incident analysis.
Evaluate the following student's answer and provide constructive feedback.

Question: {question}
Answer: {answer}

Give a short explanation whether the answer is correct or not, and why.
"""

    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a SOC analyst trainer."},
            {"role": "user", "content": prompt}
        ]
    )
    feedback = resp.choices[0].message.content
    return jsonify({"feedback": feedback})


@app.route('/walkthrough-summary', methods=['POST'])
@login_required
def walkthrough_summary():
    data = request.json
    log = data.get("log", "")
    answers = data.get("answers", {})

    parts = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])
    prompt = f"""
You are an AI SOC Analyst.
Analyze the following SOC log and user responses to training questions.

SOC Log:
{log}

Student Answers:
{parts}

Provide a full analysis including: incident type, risk level, detailed description and a recommendation.
"""

    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a cybersecurity trainer."},
            {"role": "user", "content": prompt}
        ]
    )
    result = resp.choices[0].message.content
    return jsonify({"summary": result})


@app.route('/mission/start', methods=['GET'])
@login_required
def start_training():
    with open('logs/01_failed_login.json', 'r', encoding='utf-8') as f:
        log = f.read()
    return render_template('mission.html', log=log)


@app.route('/mission/feedback', methods=['POST'])
@login_required
def training_feedback():
    data = request.json
    question = data["question"]
    answer = data["answer"]
    log = data["log"]

    prompt = f"""Log:\n{log}

Student's answer to the question: "{question}"
Answer: {answer}

Give short feedback: Is it correct? Why or why not?"""

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    feedback = response.choices[0].message.content
    return jsonify({"feedback": feedback})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
