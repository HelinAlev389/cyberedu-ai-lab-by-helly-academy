import os
import io

import markdown2
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from services.openai_service import generate_image_url
from utils.pdf_export import export_to_pdf, sanitize_filename

from extensions import db
from models import User, AISession
from models.ai_memory import AIMemory
from models.lesson import Lesson
from .forms import LessonForm

teacher_dashboard_bp = Blueprint('teacher_dashboard', __name__, url_prefix='/teacher')
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@teacher_dashboard_bp.route('/lessons', methods=['GET', 'POST'])
@login_required
def manage_lessons():
    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате достъп до тази секция.", "danger")
        return redirect(url_for('main.index'))

    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(
            title=form.title.data,
            topic=form.topic.data,
            content=form.content.data,
            created_by=current_user.id
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Урокът е създаден успешно!", "success")
        return redirect(url_for('teacher_dashboard.manage_lessons'))

    lessons = Lesson.query.all()
    return render_template('teacher/lessons.html', form=form, lessons=lessons)


@teacher_dashboard_bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    # Преобразуване на Markdown съдържанието в HTML
    html_content = markdown2.markdown(lesson.content, extras=["fenced-code-blocks", "tables", "code-friendly"])

    from services.recommendation_service import recommend_lessons_for
    recommend_lessons_for(current_user.id)

    return render_template('teacher/lesson_view.html', lesson=lesson, html_content=html_content)


@teacher_dashboard_bp.route('/progress')
@login_required
def view_progress():
    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате достъп до тази секция.", "danger")
        return redirect(url_for('main.index'))

    from models.ai_memory import AIMemory
    from models.user import User

    # Вземи последните 100 събития
    memory = AIMemory.query.order_by(AIMemory.created_at.desc()).limit(100).all()

    # Групирай по потребител и тагове
    progress_map = {}
    for mem in memory:
        progress_map.setdefault(mem.user_id, []).append(mem)

    users = User.query.filter_by(role='student').all()
    return render_template('teacher/progress.html', users=users, progress=progress_map)


@teacher_dashboard_bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    url = f"/static/uploads/{filename}"
    return jsonify({'success': 1, 'file': {'url': url}})


@teacher_dashboard_bp.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате достъп до тази секция.", "danger")
        return redirect(url_for('main.index'))

    form = LessonForm(obj=lesson)

    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.topic = form.topic.data
        lesson.content = form.content.data
        db.session.commit()
        flash("Урокът е редактиран успешно!", "success")
        return redirect(url_for('teacher_dashboard.manage_lessons'))

    return render_template('teacher/edit_lesson.html', form=form, lesson=lesson)


@teacher_dashboard_bp.route('/lesson/<int:lesson_id>/export_pdf')
@login_required
def export_lesson_pdf(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    from utils.pdf_export import export_to_pdf
    html_content = markdown2.markdown(lesson.content)
    pdf_buffer = io.BytesIO()
    export_to_pdf(html_content, "", pdf_buffer)
    pdf_buffer.seek(0)

    filename = f"{lesson.title.replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)


@teacher_dashboard_bp.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате достъп да изтривате уроци.", "danger")
        return redirect(url_for('teacher_dashboard.manage_lessons'))

    db.session.delete(lesson)
    db.session.commit()
    flash("Урокът беше успешно изтрит.", "success")
    return redirect(url_for('teacher_dashboard.manage_lessons'))


@teacher_dashboard_bp.route('/lesson/<int:lesson_id>/publish', methods=['POST'])
@login_required
def publish_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате права да публикувате уроци.", "danger")
        return redirect(url_for('main.index'))

    lesson.is_published = True
    db.session.commit()
    flash("Урокът е публикуван успешно!", "success")
    return redirect(url_for('teacher_dashboard.manage_lessons'))


@teacher_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        flash("Нямате достъп до тази страница.", "danger")
        return redirect(url_for('auth.login'))

    return render_template('teacher/dashboard_simple.html', user=current_user)


@teacher_dashboard_bp.route('/test_dashboard')
@login_required
def test_dashboard():
    return f"""
    <h2>Добре дошъл, {current_user.username}!</h2>
    <p>Роля: <strong>{current_user.role}</strong></p>
    <p>Статус: {'Логнат си' if current_user.is_authenticated else 'Не си логнат'}</p>
    """


@teacher_dashboard_bp.route('/dashboard/export_pdf')
@login_required
def export_pdf():
    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате достъп до тази секция.", "danger")
        return redirect(url_for('main.index'))

    student_id = request.args.get('student_id', type=int)
    query = AIMemory.query.join(User).order_by(AIMemory.created_at.desc())

    if student_id:
        query = query.filter(AIMemory.user_id == student_id)
        user = User.query.get(student_id)
        filename_base = sanitize_filename(user.username)
    else:
        filename_base = "all_students"

    memories = query.limit(100).all()

    # Събиране на текстовете
    log_text = ""
    gpt_response = ""

    for mem in reversed(memories):  # хронологично
        log_text += f"[{mem.created_at.strftime('%Y-%m-%d %H:%M')}] {mem.user.username}:\n{mem.content}\n\n"
        gpt_response += f"[{mem.tag}] Оценка: {mem.score}\n\n"

    # 📄 Създай PDF в паметта
    pdf_buffer = io.BytesIO()
    export_to_pdf(log_text, gpt_response, pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{filename_base}_ai_report.pdf"
    )


@teacher_dashboard_bp.route('/ai-config', methods=['GET', 'POST'])
@login_required
def set_ai_config(topic=None, difficulty=None, checkpoint=None):
    if current_user.role != 'teacher':
        flash("Само преподаватели имат достъп.", "danger")
        return redirect(url_for('auth.login'))

    # Търсим или създаваме сесия
    session = AISession.query.filter_by(user_id=current_user.id).first()
    if not session:
        session = AISession(user_id=current_user.id, config={})
        db.session.add(session)
        db.session.commit()

    if request.method == 'POST':
        topic = request.form.get('topic', 'network')
        difficulty = request.form.get('difficulty', 'beginner')
        checkpoint = int(request.form.get('checkpoint', 50))

        session.config = {
            'topic': topic,
            'difficulty': difficulty,
            'checkpoint': checkpoint
        }
        db.session.commit()

        flash("Настройките са запазени успешно ✅", "success")
        return redirect(url_for('teacher_dashboard.manage_lessons'))

    notes = request.form.get('notes', '')
    session.config = {
        'topic': topic,
        'difficulty': difficulty,
        'checkpoint': checkpoint,
        'notes': notes
    }

    return render_template('teacher/config_ai.html', cfg=session.config or {})


@teacher_dashboard_bp.route('/generate_lesson', methods=['GET', 'POST'])
@login_required
def generate_lesson():
    if current_user.role != 'teacher':
        flash("Само преподаватели имат достъп до тази страница.", "danger")
        return redirect(url_for('auth.login'))

    session = AISession.query.filter_by(user_id=current_user.id).first()
    if not session or not session.config:
        flash("Моля, първо конфигурирайте AI учителя.", "warning")
        return redirect(url_for('teacher_dashboard.set_ai_config'))

    from services.openai_service import OpenAIService
    ai = OpenAIService()

    cfg = session.config
    topic = cfg.get('topic', 'network')
    difficulty = cfg.get('difficulty', 'beginner')
    notes = cfg.get('notes', '')

    lesson_prompt = f"""
    Създай красиво структуриран HTML урок по темата "{topic}" 
    на ниво {difficulty}. Включи:

    - кратко въведение с икона и заглавие
    - поне 2 тематични изображения (може да са примерни URL или alt текст)
    - анимирани секции (използвай CSS класове, напр. "fade-in", "slide-in")
    - мини куиз с 2 въпроса с възможни отговори (радио бутони)
    - завършек с обобщение и съвет

    Бележки от преподавателя: {notes if notes else "Няма"}
    Използвай HTML и класове, които могат лесно да се стилизират.
    """

    try:
        generated_lesson = ai.chat(lesson_prompt)
    except Exception as e:
        flash(f"Грешка при AI генерация: {e}", "danger")
        return redirect(url_for('teacher_dashboard.dashboard'))

    # след lesson_prompt
    image_prompt = f"Създай илюстрация по темата '{topic}' подходяща за урок по {difficulty} ниво"

    try:
        image_url = generate_image_url(image_prompt)  # ще направим този метод
    except Exception as e:
        image_url = None

    from .forms import LessonForm
    form = LessonForm(data={
        'title': f"Урок: {topic.capitalize()} ({difficulty})",
        'topic': topic,
        'content': generated_lesson
    })

    if request.method == 'POST' and form.validate_on_submit():
        is_published = form.submit_publish.data  # True ако натиснат е бутона за публикуване

        lesson = Lesson(
            title=form.title.data,
            topic=form.topic.data,
            content=form.content.data,
            created_by=current_user.id,
            is_published=is_published
        )

        db.session.add(lesson)
        db.session.commit()

        flash("Урокът е запазен успешно!" + (" (публикуван)" if is_published else " (като чернова)"), "success")
        return redirect(url_for('teacher_dashboard.manage_lessons'))

    return render_template('teacher/ai_generated_preview.html', form=form)


@teacher_dashboard_bp.route('/lesson/<int:lesson_id>/submit_quiz', methods=['POST'])
@login_required
def submit_quiz(lesson_id):
    from models.quiz_result import QuizResult

    score = int(request.form.get('score', 0))
    result = QuizResult(user_id=current_user.id, lesson_id=lesson_id, score=score)
    db.session.add(result)
    db.session.commit()

    return jsonify({'status': 'ok'})
