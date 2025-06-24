# models/ai_memory.py
from extensions import db


class AIMemory(db.Model):
    __tablename__ = 'ai_memory'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('ai_session.id'), nullable=True)
    tag = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    score = db.Column(db.Integer, nullable=True)
    user = db.relationship('User', backref='memories')

