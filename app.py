from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
import json
from utils.pdf_export import export_to_pdf


load_dotenv()
client = OpenAI()
app = Flask(__name__)


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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze-log", methods=["POST"])
def analyze_log():
    data = request.json
    log_raw = data.get("log", "")

    try:
        parsed_log = json.loads(log_raw)
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
    filename = f"results/{timestamp}_result.txt"
    pdf_filename = f"results/{timestamp}_result.pdf"
    export_to_pdf(log_raw, gpt_result, pdf_filename)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("Log:\n" + log_raw + "\n\n---\nGPT Response:\n" + gpt_result)

    return jsonify({"answer": gpt_result})


@app.route("/analyze-all", methods=["POST"])
def analyze_all_logs():
    logs_dir = "logs"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    results_summary = []

    if not os.path.exists(logs_dir):
        return jsonify({"summary": [], "error": "Logs folder not found."})

    for filename in os.listdir(logs_dir):
        if filename.endswith(".json"):
            path = os.path.join(logs_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    log_content = f.read()

                if not log_content.strip():
                    results_summary.append({"file": filename, "status": "Skipped: Empty file"})
                    continue

                json.loads(log_content)

                prompt = build_prompt(log_content)

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity teacher and SOC analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )

                gpt_result = response.choices[0].message.content

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                result_filename = f"{os.path.splitext(filename)[0]}_{timestamp}_result.txt"
                pdf_filename = os.path.join(results_dir, f"{os.path.splitext(filename)[0]}_{timestamp}_result.pdf")
                export_to_pdf(log_content, gpt_result, pdf_filename)

                with open(os.path.join(results_dir, result_filename), "w", encoding="utf-8") as f:
                    f.write("Log:\n" + log_content + "\n\n---\nGPT Response:\n" + gpt_result)

                results_summary.append({"file": filename, "status": "OK"})

            except Exception as e:
                results_summary.append({"file": filename, "status": f"Error: {str(e)}"})

    return jsonify({"summary": results_summary})


if __name__ == "__main__":
    app.run(debug=True)
