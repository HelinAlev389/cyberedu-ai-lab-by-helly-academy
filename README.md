# 🧠 CyberEdu AI Lab by Helly Academy

**CyberEdu AI Lab** е обучителна уеб платформа, създадена за ученици и студенти по киберсигурност. Тя използва **GPT AI модел**, за да анализира логове от реални инциденти, обяснява ги на достъпен език и предлага мерки за реакция и превенция.

---

## 🚀 Функционалности

- 🔐 Login система с Flask-Login
- 📥 SOC лог анализ чрез OpenAI GPT (gpt-3.5-turbo)
- 📂 Групов анализ на `.json` логове от папка `logs/`
- 📄 Генериране на PDF отчети
- 📦 ZIP архив на всички анализи
- 🗑 Изчистване на резултатите
- 🎨 Модерен Bootstrap UI с Helly Academy стил

---

## ⚙️ Използвани технологии

| Компонент     | Описание                  |
|---------------|---------------------------|
| Python 3.10+  | Основен език              |
| Flask         | Уеб сървър                |
| Flask-Login   | Аутентикация              |
| OpenAI API    | GPT анализ                |
| ReportLab     | PDF генерация             |
| Bootstrap 5   | Дизайн и оформление       |
| HTML + CSS    | Уеб интерфейс             |

---

## 📁 Структура на проекта

cyberedu-ai-lab-by-helly-academy/
├── app.py
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── dashboard.html
│ └── reports.html
├── static/
│ ├── style.css
│ └── script.js
├── logs/
│ └── *.json
├── results/
│ └── *.pdf / *.txt
├── utils/
│ └── pdf_export.py
├── .env
├── .gitignore
└── README.md


---

## ✅ Инсталация и стартиране

1. Клонирай проекта:

```bash
git clone https://github.com/HelinAlev389/cyberedu-ai-lab-by-helly-academy.git
cd cyberedu-ai-lab-by-helly-academy


Създай виртуална среда:

```bash

python -m venv venv
venv\Scripts\activate   # за Windows
Инсталирай зависимостите:

```bash

pip install -r requirements.txt
Създай .env файл:

env

OPENAI_API_KEY=sk-...
SECRET_KEY=supersecret123
Стартирай приложението:

```bash

python app.py
Отвори в браузъра: http://localhost:5000

👤 Данни за достъп
Потребител: admin

Парола: admin123
