import json
import os

from flask import (
    Blueprint, render_template, request, jsonify, flash,
    redirect, url_for, current_app, g
)
from flask_login import login_required, current_user

from extensions import db
from models import AISession
from services.openai_service import OpenAIService

ai_teacher_bp = Blueprint('ai_teacher', __name__, url_prefix='/ai_teacher')
ai_service = OpenAIService()


@ai_teacher_bp.before_app_request
def load_ai_session():
    if not current_user.is_authenticated:
        return
    sess = AISession.query.filter_by(user_id=current_user.id).first()
    if not sess:
        sess = AISession(user_id=current_user.id, config={})
        db.session.add(sess)
        db.session.commit()
    g.ai_session = sess


@ai_teacher_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('ai_teacher.html')


@ai_teacher_bp.route('/message', methods=['POST'])
@login_required
def message():
    from services.memory_service import save_memory, search_memory

    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    if not user_text:
        return jsonify({'error': 'Missing message'}), 400

    # Добави потребителското съобщение в краткосрочната памет (AISession)
    history = g.ai_session.memory.get('messages', [])
    history.append({'role': 'user', 'content': user_text})

    try:
        # Вземи релевантна памет от минали разговори
        context_snippets = search_memory(current_user.id, user_text)
        context_block = "\n".join(f"- {txt}" for txt in context_snippets)

        # Изгради пълен prompt с контекст
        full_prompt = (
            f"Ти си AI учител по киберсигурност. Това са теми от предишни разговори:\n"
            f"{context_block}\n\n"
            f"Нов въпрос от студента:\n{user_text}"
        )

        # Изпрати към OpenAI
        reply = ai_service.chat(full_prompt, session_id=str(current_user.id))

        # Запиши AI отговора в сесията (краткосрочна памет)
        history.append({'role': 'assistant', 'content': reply})
        g.ai_session.memory['messages'] = history

        # Персистентна памет (дългосрочна)
        save_memory(current_user.id, g.ai_session.id, user_text, tags=["user"])
        save_memory(current_user.id, g.ai_session.id, reply, tags=["assistant"])

        db.session.commit()

        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_teacher_bp.route('/lesson', methods=['GET'])
@login_required
def lesson():
    g.ai_session.step = 'lesson'
    db.session.commit()

    cfg = g.ai_session.config or {}
    topic = cfg.get('topic', 'network').replace('_', ' ')
    difficulty = cfg.get('difficulty', 'beginner')

    # Build prompts as plain strings
    prompt_lesson = (
        f"Представи кратък урок по {topic} "
        f"на {difficulty} ниво, включително ключови термини, примери и принципи."
    )
    prompt_quiz = (
        f"Създай 3 контролни въпроса за урок по {topic} "
        f"на {difficulty} ниво. Форматирай отговора като JSON масив от обекти "
        '{"id","question","type"}.'
    )

    try:
        lesson_content = ai_service.chat(prompt_lesson, session_id=str(current_user.id))
        quiz_json = ai_service.chat(prompt_quiz, session_id=str(current_user.id))
        quiz_questions = json.loads(quiz_json)
    except Exception as e:
        flash(f"Error fetching lesson or quiz: {e}", 'danger')
        return redirect(url_for('ai_teacher.dashboard'))

    return render_template('ai_lesson.html',
                           lesson=lesson_content,
                           quiz=quiz_questions)


@ai_teacher_bp.route('/exercise', methods=['POST'])
@login_required
def exercise():
    """Receive quiz answers, grade them against the checkpoint, then generate exercises."""
    # 1) Collect student answers
    answers = {k: v for k, v in request.form.items() if k.startswith('q')}
    if not answers:
        flash("Няма подадени отговори.", "warning")
        return redirect(url_for('ai_teacher.lesson'))

    # 2) Mark the step and commit
    g.ai_session.step = 'exercise'
    db.session.commit()

    # 3) Build a single plain-text grading prompt
    answer_lines = "\n".join(f"{qid}: {ans}" for qid, ans in answers.items())
    prompt_grade = (
            "Ти си асистент-оценител. Оцени тези студентски отговори от 0 до 100 и "
            "върни само JSON обект с формата "
            "{\"scores\": {\"q1\": процент, ...}, \"average\": средна_оценка}.\n"
            + answer_lines
    )

    # 4) Call the service with a string prompt
    try:
        grade_resp = ai_service.chat(prompt_grade, session_id=str(current_user.id))
        grade_data = json.loads(grade_resp)
    except Exception as e:
        flash(f"Грешка при оценяване: {e}", "danger")
        return redirect(url_for('ai_teacher.lesson'))

    avg_score = grade_data.get("average", 0)
    checkpoint = g.ai_session.config.get("checkpoint", 50)

    # 5) Enforce checkpoint
    if avg_score < checkpoint:
        flash(
            f"Резултат {avg_score:.1f}% (праг {checkpoint}%). "
            "Моля, повтори урока.", "info"
        )
        return redirect(url_for('ai_teacher.lesson'))

    # 6) Generate exercises with a plain-text prompt
    prompt_ex = (
        f"Студентът постигна средно {avg_score:.1f}%. "
        "Генерирай 2–3 персонализирани упражнения: кратки казуси или въпроси."
    )

    try:
        exercises = ai_service.chat(prompt_ex, session_id=str(current_user.id))
    except Exception as e:
        flash(f"Грешка при генериране на упражнения: {e}", "danger")
        return redirect(url_for('ai_teacher.lesson'))

    return render_template('ai_exercises.html', exercises=exercises)


@ai_teacher_bp.route('/upload-log', methods=['POST'])
@login_required
def upload_log():
    file = request.files.get('logfile')
    if not file or not file.filename.endswith('.json'):
        flash("Моля, качете валиден .json файл.", "warning")
        return redirect(url_for('ai_teacher.dashboard'))

    upload_dir = os.path.join(current_app.instance_path, 'ai_teacher_logs')
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, file.filename)
    file.save(path)

    try:
        log_data = json.load(open(path, encoding='utf-8'))
        prompt = "Анализирай този SOC лог:\n" + json.dumps(log_data, indent=2, ensure_ascii=False)
        analysis = ai_service.chat(prompt, session_id=str(current_user.id))
    except Exception as e:
        flash(f"Грешка при анализ на лога: {e}", "danger")
        return redirect(url_for('ai_teacher.dashboard'))

    return render_template('ai_log_analysis.html',
                           log=json.dumps(log_data, indent=2, ensure_ascii=False),
                           analysis=analysis)
