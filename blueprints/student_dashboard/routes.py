import io
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, flash, send_file, request, url_for
from flask_login import login_required, current_user
from openai import OpenAI
from bs4 import BeautifulSoup

from extensions import db
from models.ai_memory import AIMemory
from models.lesson import Lesson
from models.lesson_progress import LessonProgress
from models.quiz_result import QuizResult
from models.student_note import StudentNote
from utils.pdf_export import export_to_pdf, sanitize_filename

student_dashboard_bp = Blueprint('student_dashboard', __name__, url_prefix='/student')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 💬 AI подобрение на бележки
def ai_improve_notes(prompt_html):
    soup = BeautifulSoup(prompt_html, 'html.parser')
    plain_text = soup.get_text()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "Подобри следните студентски бележки като ги направиш по-ясни и структурирани."},
            {"role": "user", "content": plain_text}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


# 🎓 Дашборд
@student_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash("Само студенти имат достъп до това табло.", "danger")
        return redirect('/')

    memories = AIMemory.query.filter_by(user_id=current_user.id).order_by(AIMemory.created_at.desc()).all()
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(5).all()

    progresses = LessonProgress.query.filter_by(user_id=current_user.id).all()
    progress_dict = {
        p.lesson_id: {
            'completed': p.progress >= 100,
            'progress': p.progress
        }
        for p in progresses
    }

    return render_template('student/dashboard.html',
                           memories=memories,
                           lessons=lessons,
                           progress=progress_dict)


# 👁️ Преглед на урок
@student_dashboard_bp.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    progress = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    if not progress:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id, progress=100,
                                  completed_at=datetime.utcnow())
        db.session.add(progress)
        db.session.commit()

    note = StudentNote.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not note:
        note = StudentNote(user_id=current_user.id, lesson_id=lesson_id, content="")
        db.session.add(note)
        db.session.commit()

    improved = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save':
            note.content = request.form.get('content', '')
            db.session.commit()
            flash("Бележката е запазена успешно.", "success")

        elif action == 'improve':
            if note.content.strip():
                improved = ai_improve_notes(note.content)
            else:
                flash("Бележката е празна и не може да бъде подобрена.", "warning")

        elif action == 'save_ai':
            note.content = request.form.get('improved_content', '')
            db.session.commit()
            flash("AI версията е запазена успешно.", "success")

    return render_template('student/lesson_view.html', lesson=lesson, note=note, improved=improved)


# ✅ Завършени уроци
@student_dashboard_bp.route('/completed')
@login_required
def completed_lessons():
    if current_user.role != 'student':
        flash("Нямате достъп.", "danger")
        return redirect('/')

    progresses = LessonProgress.query.filter_by(user_id=current_user.id).filter(LessonProgress.progress >= 100).all()
    lessons = [p.lesson for p in progresses]

    return render_template('student/completed_lessons.html', lessons=lessons)


# 🧠 Моите бележки
@student_dashboard_bp.route('/notes', methods=['GET', 'POST'])
@login_required
def all_notes():
    if current_user.role != 'student':
        flash("Нямате достъп до тази страница.", "danger")
        return redirect('/')

    notes = StudentNote.query.filter_by(user_id=current_user.id).order_by(StudentNote.updated_at.desc()).all()
    improved_note = None
    active_note = None

    if request.method == 'POST':
        note_id = int(request.form.get('note_id'))
        action = request.form.get('action')
        note = StudentNote.query.get(note_id)

        if note and note.user_id == current_user.id:
            if action == 'edit':
                active_note = note

            elif action == 'delete':
                db.session.delete(note)
                db.session.commit()
                flash("Бележката беше изтрита.", "info")
                return redirect(url_for('student_dashboard.all_notes'))

            elif action == 'save':
                note.content = request.form.get('content', '')
                db.session.commit()
                flash("Бележката беше запазена.", "success")

            elif action == 'improve':
                if note.content.strip():
                    improved_note = ai_improve_notes(note.content)
                    active_note = note
                else:
                    flash("Бележката е празна и не може да бъде подобрена.", "warning")

            elif action == 'save_ai':
                note.content = request.form.get('improved_content')
                db.session.commit()
                flash("AI версията беше запазена успешно.", "success")

    return render_template('student/notes.html',
                           notes=notes,
                           improved_note=improved_note,
                           active_note=active_note)


# 📄 Експортиране в PDF
@student_dashboard_bp.route('/export_pdf')
@login_required
def export_pdf():
    if current_user.role != 'student':
        flash("Нямате достъп.", "danger")
        return redirect('/')

    memories = AIMemory.query.filter_by(user_id=current_user.id).order_by(AIMemory.created_at).all()

    log_text = ""
    gpt_response = ""

    for mem in memories:
        log_text += f"[{mem.created_at.strftime('%Y-%m-%d %H:%M')}] {mem.content}\n\n"
        gpt_response += f"[{mem.tag}] Оценка: {mem.score}\n\n"

    buffer = io.BytesIO()
    export_to_pdf(log_text, gpt_response, buffer)
    buffer.seek(0)

    filename = f"{sanitize_filename(current_user.username)}_history.pdf"
    return send_file(buffer, mimetype="application/pdf", download_name=filename, as_attachment=True)


@student_dashboard_bp.route('/search')
@login_required
def search():
    query = request.args.get('q')
    # Тук можеш да филтрираш уроки, бележки и т.н.
    return render_template("student/search_results.html", query=query)


@student_dashboard_bp.route('/lessons')
@login_required
def student_lessons():
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).all()
    return render_template('student/lesson_list.html', lessons=lessons)


@student_dashboard_bp.route('/lessons')
@login_required
def lesson_list():
    lessons = Lesson.query.filter_by(is_published=True).order_by(Lesson.created_at.desc()).all()
    return render_template('student/lesson_list.html', lessons=lessons)


@student_dashboard_bp.route('/lesson/<int:lesson_id>/submit_quiz', methods=['POST'])
@login_required
def submit_quiz(lesson_id):
    score = request.form.get('score', type=int)
    result = QuizResult(user_id=current_user.id, lesson_id=lesson_id, score=score)
    db.session.add(result)
    db.session.commit()
    flash("Резултатът от куиза е записан успешно!", "success")
    return redirect(url_for('student_dashboard.view_lesson', lesson_id=lesson_id))
