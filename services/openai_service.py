# services/openai_service.py
# Helper module to centralize OpenAI GPT-4 interactions for the AI Teacher

import os
from openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # You can set default model here
        self.model = "gpt-4"

    def chat(self, user_text: str, session_id: str = None) -> str:
        """
        Send a chat message and return the AI's reply.
        Optionally accepts a session_id to maintain context in a DB or cache.
        """
        messages = [
            {"role": "system",
             "content": "Ти си опитен AI учител по киберсигурност, адаптиращ урока според студентския напредък."},
            {"role": "user", "content": user_text}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    def get_intro_lesson(self) -> tuple:
        """
        Retrieve the initial lesson content and quiz from GPT.
        Returns (lesson_text, quiz_questions_list)
        """
        prompt = (
            "Представи кратък урок за основи на мрежовата сигурност, включително дефиниции за IP адрес, порт, firewall, IDS/IPS,"
            " типични заплахи и OWASP принципи. След това предложи 3 контролни въпроса."
        )
        lesson_text = self.chat(prompt)
        # For quiz extraction, ask GPT to output as JSON
        quiz_prompt = (
            "Моля, върни само JSON масив с 3 обекта, всеки със свойствата 'id', 'question', 'type' (text/choice)."
        )
        quiz_json = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Ти си асистент, форматирай отговора като JSON."},
                {"role": "user", "content": quiz_prompt}
            ]
        ).choices[0].message.content
        # parse quiz_json string to Python list
        import json
        try:
            quiz_questions = json.loads(quiz_json)
        except json.JSONDecodeError:
            quiz_questions = []
        return lesson_text, quiz_questions

# Usage:
# from services.openai_service import OpenAIService
# ai = OpenAIService()\# lesson, quiz = ai.get_intro_lesson()
# reply = ai.chat("Как работи firewall?")
