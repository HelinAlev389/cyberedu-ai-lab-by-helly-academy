# models/ai_memory.py

from extensions import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON  # или postgresql.JSON ако си на PostgreSQL


class AIMemory(db.Model):
    __tablename__ = 'ai_memory'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('ai_session.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    embedding = db.Column(JSON, nullable=False)
    tags = db.Column(JSON, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
