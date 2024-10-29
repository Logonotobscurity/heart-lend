from flask import Blueprint, jsonify, request, render_template
from models import db, Topic, ChatThread, Message
import logging
from dialogue_system import CommunityDialogueSystem
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_api_blueprint(dialogue_system: CommunityDialogueSystem) -> Blueprint:
    api = Blueprint('api', __name__)
    
    @api.route('/')
    def index():
        return render_template('index.html')
        
    @api.route('/chat')
    def chat():
        return render_template('chat.html')
        
    @api.route('/visualization/<thread_id>')
    def visualization(thread_id):
        return render_template('visualization.html', thread_id=thread_id)

    @api.route('/api/topics')
    def get_topics():
        try:
            # Query topics from database
            topics = Topic.query.all()
            
            # If no topics exist, create some default ones
            if not topics:
                default_topics = [
                    {
                        "title": "AI Consciousness",
                        "description": "Exploring the nature of consciousness in artificial intelligence systems",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Spiritual Computing",
                        "description": "Understanding the intersection of spirituality and technology",
                        "category": "Spirituality"
                    },
                    {
                        "title": "Digital Rituals",
                        "description": "Examining how traditional practices translate into the digital age",
                        "category": "Culture"
                    }
                ]
                
                try:
                    for topic_data in default_topics:
                        new_topic = Topic()
                        new_topic.title = topic_data["title"]
                        new_topic.description = topic_data["description"]
                        new_topic.category = topic_data["category"]
                        new_topic.suggested_by_ai = True
                        db.session.add(new_topic)
                    
                    db.session.commit()
                    topics = Topic.query.all()
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Database error creating default topics: {str(e)}")
                    return jsonify({"error": "Database error"}), 500
            
            return jsonify({
                "topics": [{
                    "id": topic.id,
                    "title": topic.title,
                    "description": topic.description,
                    "category": topic.category
                } for topic in topics]
            })
            
        except Exception as e:
            logger.error(f"Error fetching topics: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            initial_role = data.get('role')
            context = data.get('context')
            
            if not initial_role or not context:
                return jsonify({"error": "Missing required parameters"}), 400
            
            response = dialogue_system.generate_response(initial_role, context)
            
            # Create new chat thread
            new_thread = ChatThread()
            new_thread.thread_id = str(datetime.utcnow().timestamp())
            new_thread.context = context
            db.session.add(new_thread)
            
            # Add initial message
            new_message = Message()
            new_message.thread = new_thread
            new_message.role = initial_role
            new_message.content = response
            db.session.add(new_message)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({"error": "Database error"}), 500
            
            return jsonify({
                "thread_id": new_thread.thread_id,
                "response": response
            })
            
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/api/chat/continue', methods=['POST'])
    def continue_chat():
        try:
            data = request.get_json()
            thread_id = data.get('thread_id')
            role = data.get('role')
            user_input = data.get('input')
            conversation_style = data.get('style')
            
            if not all([thread_id, role, user_input]):
                return jsonify({"error": "Missing required parameters"}), 400
                
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({"error": "Thread not found"}), 404
                
            response = dialogue_system.generate_layered_response(
                thread_id, 
                role, 
                user_input,
                conversation_style
            )
            
            # Add user message
            user_message = Message()
            user_message.thread = thread
            user_message.role = "user"
            user_message.content = user_input
            db.session.add(user_message)
            
            # Add AI response
            ai_message = Message()
            ai_message.thread = thread
            ai_message.role = role
            ai_message.content = response
            db.session.add(ai_message)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({"error": "Database error"}), 500
            
            return jsonify({
                "response": response
            })
            
        except Exception as e:
            logger.error(f"Error continuing chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    return api
