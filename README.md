# 🧠 CyberEdu AI Lab by Helly Academy

**CyberEdu AI Lab** е образователна уеб платформа за студенти и обучаващи се в сферата на киберсигурността. Тя използва **OpenAI GPT модели**, за да анализира реални SOC логове, да ги обяснява на разбираем език и да дава конкретни препоръки.

---

## 🚀 Основни функционалности

- 🔐 Сигурна система за вход (Flask-Login)  
- 📥 AI анализ на SOC логове чрез GPT-4  
- 📂 Масов анализ на `.json` логове от директория  
- 📄 Генериране на PDF репорти с поддръжка на кирилица  
- 📦 ZIP експорт на всички резултати  
- 🗑 Изчистване на стари репорти с един клик  
- 🎨 Чист Bootstrap 5 интерфейс, стил Helly Academy  
- 📊 SIEM Dashboard с диаграми и визуализация  
- 🧠 Walkthrough модул със стъпково решаване  
- 📝 AI обратна връзка и оценка на решения  
- 🧾 Автоматично генериране на walkthrough репорти  
- 🏅 Нива, точки и сертификат при завършен курс  

---

## 🛡️ CyberEdu AI SIEM Dashboard

Интерактивен модул за анализ и интерпретация на логове. Обучаемите качват логове, анализират ги с AI и визуализират резултатите.

---

## 🎯 SIEM възможности

- 📁 Качване на `.json` логове през браузъра  
- 🤖 AI анализ с GPT-4: инцидент, риск, препоръка  
- 📊 Диаграми с Chart.js  
- 🔍 Данни по събитие: timestamp, потребител, действие, локация  
- 🧠 Обяснение на инцидента в учебен стил  
- 📄 Експорт на анализа като PDF  
- 🧼 Изчистване на логовете  

---

## 🧠 Walkthrough модул

- 📌 Задава въпроси стъпка по стъпка  
- 📝 Събира отговори и ги изпраща към AI  
- 🧠 Връща кратка обратна връзка и оценка  
- 📄 Генерира персонален walkthrough PDF отчет  
- 🏠 Възможност за връщане към главното меню  

---

## 🧪 Примерен лог файл

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
## 📊 Диаграми и AI анализ

SIEM Dashboard-ът комбинира визуална интерпретация и AI интелигентност, за да подпомогне обучаемите в анализа на инциденти.

- **📈 Разпределение на събитията** – интерактивна лента диаграма (`event_type` честота)
- **🧠 Препоръки с AI Tooltip** – към всяко събитие се показва съвет от GPT-4 (на български)
- **📋 Обобщение на лога** – показва:
  - `timestamp`  
  - `event_type`  
  - `user`  
  - `action`  
  - `location`
- **📄 PDF отчет** – целият анализ може да се експортира
- **🗑 Изчистване на логовете** – с един клик

---

## 🧾 CTF и Leaderboard модул

Симулации на реални инциденти с въпроси, логове и точки за решаване.

- 🎯 Интерактивни мисии в 3 нива (Tier 1–3)
- 💬 Въпроси и логове в реален контекст
- 🧠 GPT-4 проверява и оценява отговорите
- 📄 Автоматично генериран PDF с резултатите
- 🏆 Натрупване на точки и класиране в Leaderboard

---

## 🧠 Walkthrough модул

Насочено, стъпково упражнение за разследване на инцидент.

- ✅ Стъпка по стъпка въпроси (какво, кой, как)
- ✍️ Полета за свободен отговор
- 🤖 AI анализира отговорите и дава съвети
- 📈 Финална оценка и препоръки
- 📄 PDF отчет на цялата мисия
- 🔁 Бутон за повторение или връщане към меню

---

## 🏅 Профил и Сертификат

Потребителите имат достъп до табло с техните постижения.

- 👤 „Моят профил“ показва:
  - История на CTF и walkthrough-и
  - AI оценки и препоръки
  - Натрупани точки по мисии
- 📜 Сертификат за завършено ниво:
  - Издава се при събрани 100+ точки или завършени определени мисии
  - Изтегля се като **PDF със знак и дата**


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
## 📁 Project Structure

```text
cyberedu-ai-lab-by-helly-academy/
├── app.py                        # Основно Flask приложение
├── .env                          # API ключове и тайни
├── requirements.txt              # Python зависимости
├── README.md                     # Документация
│
├── utils/                        # Помощни модули
│   ├── pdf_export.py             # Генериране на PDF с кирилица
│   ├── ai_feedback.py            # AI логика за обратна връзка
│   ├── save_ctf_response.py      # Съхранение на отговори от CTF
│   └── certificates.py           # (по избор) Генериране на сертификати
│
├── instance/
│   └── logs/                     # Качени .json логове от потребители
│
├── results/                      # PDF репорти от анализи, walkthrough-и, CTF
│
├── static/
│   ├── style.css                 # Общи стилове
│   ├── login.css                 # Стил за формата за вход
│   ├── auth.js                   # JS логика за автентикация
│   ├── chart.js                  # Конфигурация за диаграми
│   └── fonts/
│       └── DejaVuSans.ttf        # Шрифт с поддръжка на кирилица
│
├── templates/                    # HTML шаблони
│   ├── base.html                 # Общ базов шаблон
│   ├── login.html               # Форма за вход
│   ├── register.html            # Регистрация
│   ├── dashboard.html           # Основно табло
│   ├── siem.html                # SIEM Dashboard
│   ├── reports.html             # Списък с анализи
│   ├── ctf.html                 # CTF интерфейс
│   ├── ctf_overview.html        # Всички CTF мисии
│   ├── ctf_result.html          # Резултат след мисия
│   ├── walkthrough_list.html    # Списък с walkthrough-и
│   ├── walkthrough.html         # Интерактивен walkthrough
│   ├── profile.html             # „Моят профил“ страница
│   ├── leaderboard.html         # Класация
│   ├── user_management.html     # (по избор) Админ панел
│   └── forgot_password.html     # Забравена парола

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
