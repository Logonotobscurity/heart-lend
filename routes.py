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
                    # Yoruba Spiritual Practice Topics
                    {
                        "title": "Ori Consciousness Levels",
                        "description": "Exploring the three levels of Ori consciousness: Ori-Inu (Inner), Ori-Ode (External), and Ori-Apere (Transcendent)",
                        "category": "Consciousness"
                    },
                    # Add other default topics...
                ]
                
                try:
                    for topic_data in default_topics:
                        new_topic = Topic(
                            title=topic_data["title"],
                            description=topic_data["description"],
                            category=topic_data["category"],
                            suggested_by_ai=True
                        )
                        db.session.add(new_topic)
                    
                    db.session.commit()
                    topics = Topic.query.all()
                    
                except Exception as e:
                    logger.error(f"Database error creating default topics: {str(e)}")
                    db.session.rollback()
                    return jsonify({
                        "status": "error",
                        "message": "Database error creating default topics.",
                        "error": str(e)
                    }), 500
            
            # Convert topics to JSON serializable format
            topics_data = []
            for topic in topics:
                topics_data.append({
                    "id": topic.id,
                    "title": topic.title,
                    "description": topic.description,
                    "category": topic.category
                })
            
            return jsonify({
                "status": "success",
                "data": {
                    "topics": topics_data
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching topics: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Database error fetching topics.",
                "error": str(e)
            }), 500

    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            
            # Create new chat thread
            thread = ChatThread(
                thread_id=str(datetime.utcnow().timestamp()),
                context=data.get('context', '')
            )
            db.session.add(thread)
            db.session.commit()
            
            # Generate initial response
            response = dialogue_system.generate_response(
                role=data.get('role'),
                context=data.get('context'),
                conversation_style=data.get('style')
            )
            
            # Store message
            message = Message(
                thread_id=thread.id,
                role=data.get('role'),
                content=response
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "data": {
                    "thread_id": thread.thread_id,
                    "response": response
                }
            })
            
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Error starting chat.",
                "error": str(e)
            }), 500

    @api.route('/api/chat/continue', methods=['POST'])
    def continue_chat():
        try:
            data = request.get_json()
            thread_id = data.get('thread_id')
            
            if not thread_id:
                return jsonify({
                    "status": "error",
                    "message": "Thread ID is required."
                }), 400
            
            # Generate response
            response = dialogue_system.generate_layered_response(
                thread_id=thread_id,
                role=data.get('role'),
                user_input=data.get('input'),
                conversation_style=data.get('style')
            )
            
            return jsonify({
                "status": "success",
                "data": {
                    "response": response
                }
            })
            
        except Exception as e:
            logger.error(f"Error continuing chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Error continuing chat.",
                "error": str(e)
            }), 500

    return api
