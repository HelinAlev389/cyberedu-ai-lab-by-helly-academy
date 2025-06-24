# services/openai_service.py
import json

from openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4"

    def chat(self, user_text: str) -> str:
        messages = [
            {"role": "system",
             "content": "Ти си опитен AI учител по киберсигурност, адаптиращ урока според студентския напредък."},
            {"role": "user", "content": user_text}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[AI Error: {e}]"

    def get_intro_lesson(self) -> tuple:
        lesson_prompt = (
            "Представи кратък урок за основи на мрежовата сигурност, включително дефиниции за IP адрес, порт, firewall, IDS/IPS,"
            " типични заплахи и OWASP принципи. След това предложи 3 контролни въпроса."
        )
        lesson_text = self.chat(lesson_prompt)

        quiz_prompt = (
            "Моля, върни само JSON масив с 3 обекта, всеки със свойствата 'id', 'question', 'type' (text/choice)."
        )
        try:
            quiz_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ти си асистент, форматирай отговора като JSON."},
                    {"role": "user", "content": quiz_prompt}
                ]
            )
            quiz_json = quiz_response.choices[0].message.content
            quiz_questions = json.loads(quiz_json)
        except Exception as e:
            quiz_questions = []
            lesson_text += f"\n\n[Quiz Error: {e}]"

        return lesson_text, quiz_questions
