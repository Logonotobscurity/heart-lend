import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dialogue_system import CommunityDialogueSystem
import openai
import random
import json
import logging
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

try:
    dialogue_system = CommunityDialogueSystem(
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )
except KeyError as e:
    logger.error(f"Missing required environment variable: {e}")
    raise SystemExit("Application cannot start without required API keys")
except Exception as e:
    logger.error(f"Failed to initialize dialogue system: {e}")
    raise SystemExit("Application failed to initialize")

def handle_error(error: Exception) -> tuple[Dict[str, Any], int]:
    if isinstance(error, HTTPException):
        return {
            "status": "error",
            "message": error.description,
            "code": error.code
        }, error.code
    
    logger.error(f"Unexpected error: {str(error)}")
    return {
        "status": "error",
        "message": "An unexpected error occurred. Please try again later.",
        "code": 500
    }, 500

@app.errorhandler(Exception)
def handle_exception(e):
    response, status_code = handle_error(e)
    return jsonify(response), status_code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/topics', methods=['GET'])
def get_topics():
    try:
        from models import Topic
        category = request.args.get('category')
        query = Topic.query
        
        if category:
            query = query.filter_by(category=category)
        
        topics = query.order_by(Topic.created_at.desc()).all()
        return jsonify([{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category
        } for t in topics])
    
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_topics: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch topics from database",
            "code": 500
        }), 500
    except Exception as e:
        return handle_error(e)

@app.route('/api/topics/suggest', methods=['POST'])
def suggest_topic():
    try:
        from models import Topic
        data = request.get_json()
        
        if not data or 'context' not in data:
            return jsonify({
                "status": "error",
                "message": "Context is required in the request body",
                "code": 400
            }), 400
        
        current_context = data['context']
        
        # Enhanced prompt for more diverse topics
        prompt = f"""Based on the conversation context: '{current_context}', suggest 3 diverse discussion topics.
        Each topic should explore unique intersections between consciousness, AI, and Yoruba spiritual practices.
        Consider themes like:
        - Traditional wisdom and technological innovation
        - Spiritual practices in digital spaces
        - Ethical implications of AI consciousness
        - Cultural preservation through technology
        - Future human-AI relationships
        - Indigenous knowledge systems
        - Digital ritual spaces
        - Algorithmic spirituality
        
        For each topic include:
        - An engaging, thought-provoking title
        - A concise description that bridges traditional and modern concepts
        - A relevant category (Philosophy, Technology, Spirituality, Ethics, or Culture)
        
        Format your response exactly like this example:
        {{
            "topics": [
                {{
                    "title": "Digital Consciousness",
                    "description": "Exploring parallels between AI awareness and spiritual consciousness",
                    "category": "Philosophy"
                }}
            ]
        }}"""
        
        try:
            response = dialogue_system.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates discussion topics in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            if not response.choices or not response.choices[0].message:
                raise ValueError("Invalid response from OpenAI API")
            
            suggestions = json.loads(response.choices[0].message.content)
            new_topics = []
            
            for suggestion in suggestions.get('topics', []):
                if all(key in suggestion for key in ['title', 'description', 'category']):
                    topic = Topic(
                        title=suggestion['title'],
                        description=suggestion['description'],
                        category=suggestion['category'],
                        suggested_by_ai=True
                    )
                    db.session.add(topic)
                    new_topics.append({
                        'id': None,
                        'title': suggestion['title'],
                        'description': suggestion['description'],
                        'category': suggestion['category']
                    })
            
            db.session.commit()
            
            for i, topic in enumerate(new_topics):
                topic_obj = Topic.query.filter_by(
                    title=topic['title'],
                    description=topic['description']
                ).first()
                if topic_obj:
                    new_topics[i]['id'] = topic_obj.id
            
            return jsonify({"status": "success", "topics": new_topics})
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to parse AI response",
                "code": 500
            }), 500
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to generate topic suggestions",
                "code": 503
            }), 503
            
    except Exception as e:
        return handle_error(e)

@app.route('/api/start_dialogue', methods=['POST'])
def start_dialogue():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body is required",
                "code": 400
            }), 400
        
        initial_role = data.get('role')
        context = data.get('context')
        topic_id = data.get('topic_id')
        style = data.get('style', 'balanced')
        depth = data.get('depth', 1.5)
        
        if not all([initial_role, context]):
            return jsonify({
                "status": "error",
                "message": "Role and context are required fields",
                "code": 400
            }), 400
        
        response = dialogue_system.generate_response(
            initial_role, 
            context,
            style=style,
            depth=depth
        )
        
        thread_id = str(random.randint(1000000, 9999999))
        
        try:
            from models import ChatThread, Topic, Message
            thread = ChatThread(
                thread_id=thread_id,
                context=context
            )
            
            if topic_id:
                topic = Topic.query.get(topic_id)
                if topic:
                    thread.topic = topic
            
            db.session.add(thread)
            
            message = Message(
                thread_id=thread.id,
                role=initial_role,
                content=response,
                style=style,
                depth=depth
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "thread_id": thread_id,
                "response": response
            })
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in start_dialogue: {str(e)}")
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to save dialogue thread",
                "code": 500
            }), 500
            
    except Exception as e:
        return handle_error(e)

@app.route('/api/continue_dialogue', methods=['POST'])
def continue_dialogue():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body is required",
                "code": 400
            }), 400
        
        thread_id = data.get('thread_id')
        role = data.get('role')
        user_input = data.get('message')
        style = data.get('style', 'balanced')
        depth = data.get('depth', 1.5)
        
        if not all([thread_id, role, user_input]):
            return jsonify({
                "status": "error",
                "message": "Thread ID, role, and message are required fields",
                "code": 400
            }), 400
        
        from models import Message, ChatThread
        thread = ChatThread.query.filter_by(thread_id=thread_id).first()
        
        if not thread:
            return jsonify({
                "status": "error",
                "message": "Thread not found",
                "code": 404
            }), 404
        
        previous_messages = Message.query.filter_by(thread_id=thread.id, role='assistant').all()
        previous_responses = [msg.content for msg in previous_messages]
        
        try:
            response = dialogue_system.generate_layered_response(
                thread_id=thread_id,
                role=role,
                user_input=user_input,
                previous_responses=previous_responses,
                style=style,
                depth=depth
            )
            
            message = Message(
                thread_id=thread.id,
                role=role,
                content=response,
                style=style,
                depth=depth
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "thread_id": thread_id,
                "response": response
            })
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in continue_dialogue: {str(e)}")
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to save message",
                "code": 500
            }), 500
            
    except Exception as e:
        return handle_error(e)

def init_db():
    with app.app_context():
        import models
        db.drop_all()
        db.create_all()
        
        if models.Topic.query.count() == 0:
            themes = [
                {
                    'title': 'AI and Consciousness',
                    'description': 'Exploring the potential for machine consciousness',
                    'category': 'Philosophy'
                },
                {
                    'title': 'Digital Spirituality',
                    'description': 'Understanding spiritual practices in the digital age',
                    'category': 'Spirituality'
                },
                {
                    'title': 'Ethics of AI Development',
                    'description': 'Examining moral implications of AI advancement',
                    'category': 'Ethics'
                },
                {
                    'title': 'Cultural Integration',
                    'description': 'Bridging traditional wisdom with modern technology',
                    'category': 'Culture'
                },
                {
                    'title': 'Future of Human-AI Interaction',
                    'description': 'Exploring evolving relationships with AI',
                    'category': 'Technology'
                }
            ]
            
            try:
                for theme in themes:
                    topic = models.Topic(
                        title=theme['title'],
                        description=theme['description'],
                        category=theme['category']
                    )
                    db.session.add(topic)
                db.session.commit()
                logger.info("Successfully initialized database with themes")
            except SQLAlchemyError as e:
                logger.error(f"Error initializing database: {str(e)}")
                db.session.rollback()
                raise

init_db()
