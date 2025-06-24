from datetime import datetime
from extensions import db


class AISession(db.Model):
    __tablename__ = 'ai_session'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    step = db.Column(db.String(50), default='intro')
    memory = db.Column(db.JSON, default={})
    config = db.Column(db.JSON, nullable=False, default={})
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
