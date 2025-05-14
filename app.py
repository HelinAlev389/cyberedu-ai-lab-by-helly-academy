import datetime
import io
import json
import os
import zipfile
from collections import Counter
from dotenv import load_dotenv
from flask import (
    Flask, request, jsonify, render_template,
    redirect, url_for, send_file, flash, request, session
)
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user, login_required, current_user
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from utils.ctf_missions import MISSIONS
from utils.pdf_export import export_to_pdf, sanitize_filename
from utils.save_ctf_response import save_ctf_report

load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "supersecret123")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# --- Forms ---

class RegistrationForm(FlaskForm):
    first_name = StringField('Име', validators=[DataRequired(), Length(1, 80)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(1, 80)])
    username = StringField('Потребителско име', validators=[DataRequired(), Length(4, 80)])
    password = PasswordField('Парола', validators=[DataRequired(), Length(6, 200)])

    confirm_password = PasswordField(
        'Потвърди парола',
        validators=[DataRequired(), EqualTo('password', message='Паролите не съвпадат.')]
    )

    role = SelectField('Роля', choices=[
        ('student', 'Студент'),
        ('teacher', 'Преподавател'),
        ('admin', 'Администратор')],
                       validators=[DataRequired()]
                       )
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    remember_me = BooleanField('Запомни ме')  # ⬅️ Добави това
    submit = SubmitField('Вход')


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
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data
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
    if isinstance(log_raw, str):
        try:
            log_data = json.loads(log_raw)
        except (json.JSONDecodeError, TypeError):
            return jsonify({"answer": "Грешка: логът не е валиден JSON."})
    else:
        log_data = log_raw

    prompt = build_prompt(json.dumps(log_data, indent=2))

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти си SOC анализатор."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
    except Exception as e:
        return jsonify({"answer": f"Грешка от OpenAI: {str(e)}"})

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)
    txt_path = f"results/{ts}_result.txt"
    pdf_path = f"results/{ts}_result.pdf"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Log:\n{json.dumps(log_data, indent=2)}\n\n---\nGPT Response:\n{result}")

    export_to_pdf(json.dumps(log_data, indent=2), result, pdf_path)

    return jsonify({"answer": result})


@app.route('/analyze-all', methods=['POST'])
@login_required
def analyze_all():
    LOGS_DIR = os.path.join("instance", "logs")
    logs_dir = LOGS_DIR
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
            summary.append({"file": fn, "status": "Skipped"})
            continue

        try:
            json.loads(log)
            prompt = build_prompt(log)
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ти си SOC анализатор."},
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content  # <-- това липсваше

            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            txt_name = f"{os.path.splitext(fn)[0]}_{ts}_result.txt"
            pdf_name = f"{os.path.splitext(fn)[0]}_{ts}_result.pdf"
            txt_path = os.path.join(results_dir, txt_name)
            pdf_path = os.path.join(results_dir, pdf_name)

            with open(txt_path, "w", encoding="utf-8") as out:
                out.write(f"Log:\n{log}\n\n---\nGPT Response:\n{result}")
            export_to_pdf(log, result, pdf_path)

            summary.append({"file": fn, "status": "OK"})
        except Exception as e:
            summary.append({"file": fn, "status": f"Error: {e}"})

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


class ForgotPasswordForm(FlaskForm):
    username = StringField('Имейл или потребителско име', validators=[DataRequired()])
    submit = SubmitField('Изпрати линк')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash("Ако съществува акаунт с този имейл/потребителско име, ще получиш линк за нулиране на паролата.", "info")
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)


@app.route("/siem")
@login_required
def siem_dashboard():
    logs_path = "instance/logs"
    log_files = [f for f in os.listdir(logs_path) if f.endswith(".json")] if os.path.exists(logs_path) else []
    return render_template("siem.html", log_files=log_files, chart_data=None)


@app.route("/siem/analyze", methods=["POST"])
@login_required
def siem_analyze():
    logs_path = "instance/logs"
    log_files = [f for f in os.listdir(logs_path) if f.endswith(".json")] if os.path.exists(logs_path) else []

    logfile = request.form.get("logfile")
    filepath = os.path.join(logs_path, logfile)

    try:
        with open(filepath) as f:
            data = json.load(f)

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("Невалиден лог формат – очаква се списък или речник.")

        if not all(isinstance(d, dict) for d in data):
            raise ValueError("Някои записи не са речници.")

        event_types = []
        for entry in data:
            if isinstance(entry, dict):
                event = entry.get("event_type") or entry.get("event") or "unknown"
            else:
                event = "invalid"
            event_types.append(event)

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
            "tooltips": [ai_suggestions.get(k, "Няма препоръка.") for k in counts.keys()]
        }

        prompt = f"Анализирай SOC лог:\n{json.dumps(data, indent=2)}"

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти си SOC анализатор."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_output = response.choices[0].message.content

        return render_template("siem.html",
                               log_files=log_files,
                               log=json.dumps(data, indent=2),
                               ai_analysis=ai_output,
                               chart_data=chart_data,
                               data=data)

    except Exception as e:
        return render_template("siem.html",
                               log_files=log_files,
                               log="",
                               ai_analysis=f"Грешка при анализ: {e}",
                               chart_data={})


@app.route("/upload-log", methods=["POST"])
@login_required
def upload_log():
    file = request.files.get("logfile")
    if not file:
        flash("Не е избран файл.", "danger")
        return redirect(url_for("siem_dashboard"))

    if not file.filename.endswith(".json"):
        flash("Само .json файлове са позволени.", "warning")
        return redirect(url_for("siem_dashboard"))

    logs_path = "instance/logs"
    os.makedirs(logs_path, exist_ok=True)

    filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    save_path = os.path.join(logs_path, filename)
    file.save(save_path)

    flash("Файлът е качен успешно!", "success")
    return redirect(url_for("siem_dashboard"))


@app.route("/clear-logs", methods=["POST"])
@login_required
def clear_uploaded_logs():
    logs_path = "instance/logs"
    deleted = []

    if os.path.exists(logs_path):
        for f in os.listdir(logs_path):
            if f.endswith(".json"):
                try:
                    os.remove(os.path.join(logs_path, f))
                    deleted.append(f)
                except Exception as e:
                    flash(f"Грешка при изтриване на {f}: {e}", "danger")

    if deleted:
        flash(f"Изтрити {len(deleted)} лог файла.", "success")
    else:
        flash("Няма лог файлове за изтриване.", "info")

    return redirect(url_for("siem_dashboard"))


@app.route("/export-siem-pdf", methods=["POST"])
@login_required
def export_siem_pdf():
    log_json = request.form.get("log_data")
    ai_output = request.form.get("ai_output")

    if not log_json or not ai_output:
        flash("Грешка: липсват данни за PDF.", "danger")
        return redirect(url_for("siem_dashboard"))

    try:
        log_data = json.loads(log_json)
        log_entry = log_data[0] if isinstance(log_data, list) and log_data else {}

        event_type = sanitize_filename(log_entry.get("event_type", "event"))
        user = sanitize_filename(log_entry.get("user", "user"))
        timestamp = sanitize_filename(log_entry.get("timestamp", "timestamp"))

        filename = f"results/soc_report_{event_type}_{user}_{timestamp}.pdf"
        export_to_pdf(json.dumps(log_data, indent=2), ai_output, filename)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f"Грешка при генериране на PDF: {str(e)}", "danger")
        return redirect(url_for("siem_dashboard"))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.context_processor
def inject_request():
    return dict(request=request)


@app.route('/admin/users')
@login_required
def user_management():
    return render_template('user_management.html')


@app.route('/ctf')
@login_required
def ctf_overview():
    return render_template('ctf_overview.html', missions=MISSIONS)


@app.route('/ctf/<mission_id>/tier/<tier>', methods=['GET', 'POST'])
@login_required
def ctf_mission(mission_id, tier):
    mission = MISSIONS.get(mission_id)
    if not mission or tier not in mission["tiers"]:
        return "Невалидна мисия или Tier", 404

    tier_data = mission["tiers"][tier]

    if request.method == 'POST':
        answers = [request.form.get(f'answer{i + 1}') for i in range(len(tier_data["questions"]))]

        filename = save_ctf_report(current_user.username, mission_id, tier, answers)

        session['last_ctf_pdf'] = filename  # 📌 Записваме в session
        flash(f"Успешно записа отговорите! Генериран PDF: {filename}", "success")

        return redirect(url_for('ctf_result'))

    return render_template('ctf.html', mission=mission, tier_data=tier_data, tier=tier)


@app.route('/ctf-result')
@login_required
def ctf_result():
    filename = session.get('last_ctf_pdf')
    return render_template('ctf_result.html', filename=filename)


@app.route('/ctf/download/<filename>')
@login_required
def download_ctf_pdf(filename):
    return send_file(os.path.join("results", filename), as_attachment=True)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
