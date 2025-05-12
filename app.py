from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from openai import OpenAI
from dotenv import load_dotenv
import os
import datetime
import json
import zipfile
import io
from utils.pdf_export import export_to_pdf

load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "supersecret123")

# Init OpenAI
client = OpenAI()

# Init Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# User model
class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Prompt builder
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


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze-log", methods=["POST"])
def analyze_log():
    data = request.json
    log_raw = data.get("log", "")

    try:
        json.loads(log_raw)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"answer": "Грешка: логът не е валиден JSON. Моля, провери синтаксиса."})

    prompt = build_prompt(log_raw)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a cybersecurity teacher and SOC analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    gpt_result = response.choices[0].message.content

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)
    txt_path = f"results/{timestamp}_result.txt"
    pdf_path = f"results/{timestamp}_result.pdf"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Log:\n{log_raw}\n\n---\nGPT Response:\n{gpt_result}")

    export_to_pdf(log_raw, gpt_result, pdf_path)
    return jsonify({"answer": gpt_result})


@app.route("/analyze-all", methods=["POST"])
def analyze_all_logs():
    logs_dir = "logs"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    summary = []

    if not os.path.exists(logs_dir):
        return jsonify({"summary": [], "error": "Logs folder not found."})

    for file in os.listdir(logs_dir):
        if file.endswith(".json"):
            path = os.path.join(logs_dir, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    log = f.read()

                if not log.strip():
                    summary.append({"file": file, "status": "Skipped: empty file"})
                    continue

                json.loads(log)
                prompt = build_prompt(log)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity teacher and SOC analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.choices[0].message.content

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                txt_name = f"{os.path.splitext(file)[0]}_{timestamp}_result.txt"
                pdf_name = f"{os.path.splitext(file)[0]}_{timestamp}_result.pdf"

                with open(os.path.join(results_dir, txt_name), "w", encoding="utf-8") as out:
                    out.write(f"Log:\n{log}\n\n---\nGPT Response:\n{result}")

                export_to_pdf(log, result, os.path.join(results_dir, pdf_name))
                summary.append({"file": file, "status": "OK"})

            except Exception as e:
                summary.append({"file": file, "status": f"Error: {str(e)}"})

    return jsonify({"summary": summary})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            user = User(id=1)
            login_user(user)
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Грешно потребителско име или парола.")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/reports")
@login_required
def reports():
    files = [f for f in os.listdir("results") if f.endswith(".pdf")]
    files.sort(reverse=True)
    return render_template("reports.html", reports=files)


@app.route("/export")
@login_required
def export():
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w") as z:
        for file in os.listdir("results"):
            if file.endswith(".pdf") or file.endswith(".txt"):
                z.write(os.path.join("results", file), arcname=file)
    memory.seek(0)
    return send_file(memory, download_name="helly_ai_reports.zip", as_attachment=True)


@app.route("/clear-results", methods=["POST"])
@login_required
def clear_results():
    deleted = []
    for file in os.listdir("results"):
        if file.endswith(".pdf") or file.endswith(".txt"):
            try:
                os.remove(os.path.join("results", file))
                deleted.append(file)
            except Exception as e:
                deleted.append(f"{file} (error: {e})")
    return jsonify({"deleted": deleted})


if __name__ == "__main__":
    app.run(debug=True)
