# 🧠 CyberEdu AI Lab by Helly Academy

**CyberEdu AI Lab** is an educational web platform designed for students and learners in cybersecurity. It leverages **OpenAI GPT models** to analyze real-world SOC logs, explain them in plain language, and offer actionable mitigation and prevention advice.

---

## 🚀 Core Features

- 🔐 Secure login system (Flask-Login)  
- 📥 SOC log analysis powered by OpenAI GPT-4  
- 📂 Batch analysis of `.json` logs from the `logs/` folder  
- 📄 PDF report generation  
- 📦 Download ZIP archive of all analysis results  
- 🗑 Clear old results with one click  
- 🎨 Clean Bootstrap 5 UI styled by Helly Academy  

---

## 🛡️ CyberEdu AI SIEM Dashboard

An interactive visual module designed to help learners analyze and interpret security logs. Students and instructors can upload logs, analyze them with AI, and visualize the results.

---

## 🎯 Key SIEM Features

- 📁 Upload `.json` log files from the browser  
- 🤖 Analyze logs with **GPT-4**: detect incident type, assess risk, generate summaries and recommendations  
- 📊 Generate visual charts with Chart.js  
- 🧠 Display key summary data (timestamp, event type, user, action, location)  
- 🧾 Export analysis reports as **PDFs**  
- 🧼 One-click log deletion  
- 🔐 Authenticated access required  

---

## 🧪 Sample Log File

```json
[
  {
    "timestamp": "2025-05-12T20:11:03Z",
    "event_type": "failed_login",
    "user": "student01",
    "action": "login failed",
    "location": "WebServer-01"
  },
  {
    "timestamp": "2025-05-12T20:12:55Z",
    "event_type": "privilege_escalation",
    "user": "student01",
    "action": "added to Administrators",
    "location": "DomainController-01"
  }
]
```

---

## 📊 Chart & AI Analysis

The SIEM Dashboard helps learners interpret cybersecurity logs using AI and data visualizations.

- **Event Distribution Chart**: Interactive bar chart showing the frequency of each `event_type`.  
- **AI-Powered Recommendations**: Tooltips provide plain-language explanations and advice for each event (powered by GPT-4).  
- **Log Summary Block**: Displays key info from each log entry:
  - Timestamp  
  - Event Type  
  - User  
  - Action Taken  
  - Location (system or server)  
- **AI Analysis Panel**: Educational explanations of security incidents to support learning.  
- **📄 Export to PDF**: Download the AI analysis as a PDF.  
- **Log Cleanup**: Easily delete uploaded logs with a button.  

---

## ⚙️ Tech Stack

| Component     | Description                   |
|---------------|-------------------------------|
| Python 3.10+  | Core programming language      |
| Flask         | Web framework                 |
| Flask-Login   | User authentication           |
| OpenAI API    | GPT-4 AI integration          |
| ReportLab     | PDF generation                |
| Bootstrap 5   | Responsive UI                 |
| HTML + CSS    | Web templating and styling    |
| Chart.js      | Interactive log visualizations|

---

## 📁 Project Structure

```text
cyberedu-ai-lab-by-helly-academy/
├── app.py                  # Main Flask app
├── .env                    # API keys and secrets
├── utils/
│   └── pdf_export.py       # PDF generation logic
├── instance/
│   └── logs/               # Uploaded .json log files
├── results/                # Generated reports
├── static/
│   ├── assets/
│   │   └── chart.js        # Chart configuration
│   └── style.css           # CSS styles
├── templates/
│   ├── siem.html           # SIEM dashboard page
│   └── *.html              # Other pages (login, register, etc.)
├── requirements.txt
└── README.md
```

---

## ✅ Setup & Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/HelinAlev389/cyberedu-ai-lab-by-helly-academy.git
cd cyberedu-ai-lab-by-helly-academy
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the root directory with:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=supersecret123
```

### 5. Run the Application

```bash
python app.py
```

Open your browser and go to:  
http://localhost:5000

---

## 👤 Default Admin Account

Use the following credentials for testing:

- **Username:** `admin`  
- **Password:** `admin123`  

---

## 📸 Preview

Include screenshots or GIFs to demonstrate the interface (optional).  
Place them in a `/docs/` folder, for example:

```
/docs/screenshot.png
```

---

## 🎓 Educational Use Only

This application is intended strictly for learning and teaching purposes. It simulates real SOC scenarios with AI-driven guidance for cybersecurity students.

> ⚠️ **Do not** use this platform in production or with real-world sensitive data.

---

## 🧠 Built By

**Helly Academy**  
*Real-world cybersecurity education, powered by AI.*
