from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
import json

load_dotenv()
client = OpenAI()

app = Flask(__name__)


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
        return jsonify({"answer": "⚠ Грешка: логът не е валиден JSON. Моля, провери синтаксиса."})

    prompt = f"""
You are an AI SOC Analyst designed to educate students on cyber incidents.

Task:
1. Identify the type of incident in the log (e.g., brute-force, phishing).
2. Assess the risk level (Low, Medium, High).
3. Explain what is happening in simple, educational language.
4. Suggest a prevention or response recommendation.
Here is the log to analyze:
{log_raw}
"""

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

    with open(filename, "w", encoding="utf-8") as f:
        f.write("Log:\n" + log_raw + "\n\n---\nGPT Response:\n" + gpt_result)

    return jsonify({"answer": gpt_result})

if __name__ == "__main__":
    app.run(debug=True)