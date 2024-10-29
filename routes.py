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
                    return jsonify({
                        "status": "error",
                        "message": "Unable to create default topics. Please try again later.",
                        "error": str(e)
                    }), 500
            
            return jsonify({
                "status": "success",
                "data": {
                    "topics": [{
                        "id": topic.id,
                        "title": topic.title,
                        "description": topic.description,
                        "category": topic.category
                    } for topic in topics]
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching topics: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Unable to fetch topics. Please try again later.",
                "error": str(e)
            }), 500
    
    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Invalid request format. Please provide JSON data.",
                }), 400

            # Validate required parameters
            required_params = {
                'role': str,
                'context': str
            }
            
            for param, param_type in required_params.items():
                value = data.get(param)
                if not value:
                    return jsonify({
                        "status": "error",
                        "message": f"Missing required parameter: {param}"
                    }), 400
                if not isinstance(value, param_type):
                    return jsonify({
                        "status": "error",
                        "message": f"Invalid type for parameter {param}. Expected {param_type.__name__}"
                    }), 400
            
            initial_role = data['role']
            context = data['context']
            
            # Start a database transaction
            try:
                # Create new chat thread
                new_thread = ChatThread()
                new_thread.thread_id = str(datetime.utcnow().timestamp())
                new_thread.context = context
                db.session.add(new_thread)
                
                # Flush session to get the new thread ID
                db.session.flush()
                
                # Generate response after we have the thread
                response = dialogue_system.generate_response(initial_role, context)
                
                # Add initial message with the correct thread_id
                initial_message = Message()
                initial_message.thread_id = new_thread.id
                initial_message.role = initial_role
                initial_message.content = response
                db.session.add(initial_message)
                
                # Commit the transaction
                db.session.commit()
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "thread_id": new_thread.thread_id,
                        "response": response
                    }
                })
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": "Unable to save chat data. Please try again later.",
                    "error": str(e)
                }), 500
            
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Unable to start chat. Please try again later.",
                "error": str(e)
            }), 500
    
    @api.route('/api/chat/continue', methods=['POST'])
    def continue_chat():
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Invalid request format. Please provide JSON data."
                }), 400

            # Validate required parameters
            required_params = {
                'thread_id': str,
                'role': str,
                'input': str
            }
            
            for param, param_type in required_params.items():
                value = data.get(param)
                if not value:
                    return jsonify({
                        "status": "error",
                        "message": f"Missing required parameter: {param}"
                    }), 400
                if not isinstance(value, param_type):
                    return jsonify({
                        "status": "error",
                        "message": f"Invalid type for parameter {param}. Expected {param_type.__name__}"
                    }), 400
            
            thread_id = data['thread_id']
            role = data['role']
            user_input = data['input']
            conversation_style = data.get('style', {})
            
            # Validate conversation style if provided
            if conversation_style:
                if not isinstance(conversation_style, dict):
                    return jsonify({
                        "status": "error",
                        "message": "Invalid conversation style format"
                    }), 400
                
                if 'direction' in conversation_style and conversation_style['direction'] not in ['deep', 'broad', 'balanced']:
                    return jsonify({
                        "status": "error",
                        "message": "Invalid conversation direction. Must be 'deep', 'broad', or 'balanced'"
                    }), 400
                
                if 'focus' in conversation_style:
                    try:
                        focus = float(conversation_style['focus'])
                        if not (1.0 <= focus <= 3.0):
                            raise ValueError
                    except ValueError:
                        return jsonify({
                            "status": "error",
                            "message": "Invalid focus value. Must be a number between 1.0 and 3.0"
                        }), 400

            # Find thread
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({
                    "status": "error",
                    "message": "Chat thread not found"
                }), 404
            
            try:
                # Generate response
                response = dialogue_system.generate_layered_response(
                    thread_id, 
                    role, 
                    user_input,
                    conversation_style
                )
                
                # Add user message
                user_message = Message()
                user_message.thread_id = thread.id
                user_message.role = "user"
                user_message.content = user_input
                db.session.add(user_message)
                
                # Add AI response
                ai_message = Message()
                ai_message.thread_id = thread.id
                ai_message.role = role
                ai_message.content = response
                db.session.add(ai_message)
                
                # Commit the transaction
                db.session.commit()
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "response": response
                    }
                })
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": "Unable to save chat messages. Please try again later.",
                    "error": str(e)
                }), 500
            
        except Exception as e:
            logger.error(f"Error continuing chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Unable to continue chat. Please try again later.",
                "error": str(e)
            }), 500
            
    return api
