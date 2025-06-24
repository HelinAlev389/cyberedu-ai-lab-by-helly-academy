import os
import io

import markdown2
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from utils.pdf_export import export_to_pdf, sanitize_filename

from extensions import db
from models import User
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


@teacher_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ['teacher', 'admin']:
        flash("Нямате достъп до тази секция.", "danger")
        return redirect(url_for('main.index'))

    lesson_count = Lesson.query.count()
    student_count = User.query.filter_by(role='student').count()
    memory_count = AIMemory.query.count()

    # 🔽 Вземи всички студенти за dropdown
    students = User.query.filter_by(role='student').all()

    # 🔎 Провери дали има избран student_id от GET параметри
    selected_student_id = request.args.get('student_id', type=int)

    # 📥 Вземи AI интеракции (филтрирани, ако е избран студент)
    query = AIMemory.query.join(User).order_by(AIMemory.created_at.desc())

    if selected_student_id:
        query = query.filter(AIMemory.user_id == selected_student_id)

    memories = query.limit(100).all()  # Може да направиш pagination по-късно

    # 📌 Препоръки
    from services.recommendation_service import recommend_lessons_for
    recommended = recommend_lessons_for(current_user.id)

    return render_template('teacher/dashboard.html',
                           lesson_count=lesson_count,
                           student_count=student_count,
                           memory_count=memory_count,
                           recommended=recommended,
                           students=students,
                           memories=memories,
                           selected_student_id=selected_student_id)


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
