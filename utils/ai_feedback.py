import os
from openai import OpenAI

def get_ctf_feedback(username, mission_id, tier, questions, answers):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ зарежда се когато трябва

    joined = "\n".join([
        f"{i+1}. {q}\nОтговор: {a}" for i, (q, a) in enumerate(zip(questions, answers))
    ])

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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ти си SOC инструктор и обучаваш студенти по киберсигурност."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
