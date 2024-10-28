from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    suggested_by_ai = db.Column(db.Boolean, default=False)
    threads = db.relationship('ChatThread', backref='topic', lazy=True, cascade='all, delete-orphan')

class ChatThread(db.Model):
    __tablename__ = 'chat_thread'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(64), unique=True, nullable=False)
    context = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id', ondelete='CASCADE'))
    messages = db.relationship('Message', backref='thread', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(64))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
