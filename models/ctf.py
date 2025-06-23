from extensions import db
import datetime


class CTFResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    mission_id = db.Column(db.String(80), nullable=False)
    tier = db.Column(db.String(10), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
