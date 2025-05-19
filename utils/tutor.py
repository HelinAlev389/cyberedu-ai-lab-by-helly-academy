import json, os, openai

# ------------- зареждане на урока -------------
def load_lesson(lesson_id="network_security_basics"):
    path = os.path.join(os.path.dirname(__file__), "lessons.json")
    with open(path, encoding="utf-8") as f:
        lessons = json.load(f)
    return lessons.get(lesson_id)

# ------------- AI feedback --------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

def evaluate_answer(user_answer: str, rubric: str) -> str:
    """
    Връща кратко AI обяснение дали отговорът е коректен и какво може да се подобри.
    """
    prompt = (
        "You are a cybersecurity instructor. "
        "Using the rubric below, grade the student's answer in max 3 sentences. "
        "Rubric:\n"
        f"{rubric}\n\n"
        "Student answer:\n"
        f"{user_answer}\n"
        "Feedback:"
    )
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Грешка при AI оценка: {e}"
