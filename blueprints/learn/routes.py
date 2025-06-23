import json
import os

from flask import render_template, request, session
from flask_login import login_required

from utils.tutor import evaluate_answer
from . import learn_bp


@learn_bp.route("/", methods=["GET", "POST"])
@login_required
def learn():
    catalog = lessons_catalog()
    lesson_id = request.args.get("lesson_id", "network_security_basics")
    lesson = catalog.get(lesson_id)
    if not lesson:
        return "Lesson not found", 404

    step_index = session.get("lesson_step", 0)
    feedback = prev_answer = None

    if request.method == "POST":
        action = request.form.get("action")
        max_idx = len(lesson["steps"]) - 1

        if action in {"next", "back", "restart", "skip"}:
            if action == "next":
                step_index = min(step_index + 1, max_idx)
            elif action == "back":
                step_index = max(step_index - 1, 0)
            elif action == "restart":
                step_index = 0
            elif action == "skip":
                step_index = min(step_index + 1, max_idx)

        elif action == "submit_answer":
            user_answer = request.form.get("user_answer", "")
            step = lesson["steps"][step_index]
            rubric = step.get("rubric", "")
            feedback = evaluate_answer(user_answer, rubric)
            prev_answer = user_answer

        session["lesson_step"] = step_index

    step = lesson["steps"][step_index]
    return render_template(
        "lesson.html",
        title=lesson["title"],
        content=step["content"],
        expect_input=step.get("expect_input", False),
        feedback=feedback,
        prev_answer=prev_answer,
        available_lessons=list(catalog.keys()),
    )


def lessons_catalog() -> dict:
    path = os.path.join(os.path.dirname(__file__), "../../lessons.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
