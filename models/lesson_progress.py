from extensions import db


class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)  # 🛠️ тук е промяната

    progress = db.Column(db.Integer, default=0)  # от 0 до 100
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='lesson_progresses')
    lesson = db.relationship('Lesson', backref='user_progresses')
