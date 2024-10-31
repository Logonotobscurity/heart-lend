from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize SQLAlchemy and logging
db = SQLAlchemy()
logger = logging.getLogger(__name__)

class Topic(db.Model):
    __tablename__ = 'topic'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    suggested_by_ai = db.Column(db.Boolean, default=False, nullable=False)
    
    # Add cascade delete for related threads
    threads = db.relationship('ChatThread', backref='topic', lazy=True, 
                            cascade='all, delete-orphan',
                            passive_deletes=True)

    def __init__(self, title, description, category, suggested_by_ai=False):
        self.title = title
        self.description = description
        self.category = category
        self.suggested_by_ai = suggested_by_ai

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category
        }

class ChatThread(db.Model):
    __tablename__ = 'chat_thread'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    context = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id', ondelete='CASCADE'), 
                        nullable=False, index=True)
    
    # Add cascade delete for messages
    messages = db.relationship('Message', backref='thread', lazy=True,
                             cascade='all, delete-orphan',
                             passive_deletes=True)

class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id', ondelete='CASCADE'), 
                         nullable=False, index=True)
    role = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __init__(self, thread_id, role, content):
        self.thread_id = thread_id
        self.role = role
        self.content = content
