from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze-log", methods=["POST"])
def analyze_log():
    data = request.json
    log = data.get("log", "")

    prompt = f"""
You are an AI SOC Analyst designed to educate students on cyber incidents.

Task:
1. Identify the type of incident in the log (e.g., brute-force, phishing).
2. Assess the risk level (Low, Medium, High).
3. Explain what is happening in simple, educational language.
4. Suggest a prevention or response recommendation.

Here is the log to analyze:
{log}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a cybersecurity teacher and SOC analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return jsonify({"answer": response.choices[0].message.content})


if __name__ == "__main__":
    app.run(debug=True)
