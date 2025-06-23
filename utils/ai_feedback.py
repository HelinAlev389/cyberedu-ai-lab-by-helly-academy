# utils/ai_feedback.py
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Зарежда .env преди достъп до ключа

def get_ctf_feedback(username, mission_id, tier, questions, answers, log_data=None):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ← вътре във функцията!

    joined = "\n".join([f"{i+1}. {q}\nОтговор: {a}" for i, (q, a) in enumerate(zip(questions, answers))])

    prompt = f"""
Ти си SOC инструктор. Студентът {username} е попълнил мисия {mission_id} - Tier {tier}.
Дай обратна връзка по следните въпроси:

{joined}

Инструкции:
- Анализирай всяка част поотделно.
- Дай препоръки.
- Обърни внимание на пропуски.
- Напиши на български с приятелски тон.
"""

    if log_data:
        prompt += "\n\nДопълнителна информация от лог файл:\n"
        prompt += json.dumps(log_data, indent=2, ensure_ascii=False)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ти си SOC инструктор и обучаваш студенти по киберсигурност."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
