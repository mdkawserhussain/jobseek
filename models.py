from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store secure hashes!
    subscription = db.Column(db.String(10), default='basic')  # "basic" or "premium"
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    cv = db.relationship('CV', backref='user', uselist=False)
    exams = db.relationship('Exam', backref='user', lazy=True)

class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    attempts = db.Column(db.Integer, default=0)
    exam_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
