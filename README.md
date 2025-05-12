# cyberedu-ai-lab-by-helly-academy
CyberEdu AI Lab by Helly Academy – SOC Анализатор в реално време за ученици и студенти


# CyberEdu AI Lab – SOC Анализатор с ChatGPT

🚀 Образователен AI проект за анализ на SOC инциденти в реално време, предназначен за студенти и ученици.

---

## 📦 Какво включва проектът

- Flask уеб приложение
- GPT базиран SOC анализатор
- HTML интерфейс за въвеждане на логове
- Препоръки, оценки на риск и обяснения на разбираем език

---

## 🛠️ Изисквания

- Python 3.10+
- OpenAI API ключ (валиден и активен)
- Виртуална среда (препоръчително)

---

## 🔐 Настройка на `.env` файл

1. Създай файл `.env` в основната директория
2. Въведи своя OpenAI API ключ така:
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX


3. Не качвай `.env` в GitHub – той вече е включен в `.gitignore`

---

## ▶️ Стартиране на проекта

```bash
# Активирай виртуалната среда
source venv/Scripts/activate  # Windows
# или
source venv/bin/activate      # macOS/Linux

# Инсталирай зависимости
pip install -r requirements.txt

# Стартирай приложението
python app.py


{
  "timestamp": "2025-05-12T14:03:00Z",
  "event": "failed_login",
  "user": "student01",
  "ip_address": "192.168.1.56",
  "location": "Lab-PC-03"
}


