from datetime import datetime
from app import db

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    suggested_by_ai = db.Column(db.Boolean, default=False)
    # Add relationship to ChatThread
    threads = db.relationship('ChatThread', backref='topic', lazy=True)

class ChatThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(64), unique=True, nullable=False)
    context = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add topic relationship with cascade
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id', ondelete='SET NULL'), nullable=True)
    # Add relationship to messages with cascade
    messages = db.relationship('Message', backref='thread', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(64))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
