from flask import Blueprint, jsonify, request, render_template
from models import db, Topic, ChatThread, Message
import logging
from dialogue_system import CommunityDialogueSystem
from datetime import datetime
import json
import time
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for retry mechanism
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

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

    def retry_db_operation(operation, max_retries=MAX_RETRIES):
        """Retry database operation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return operation()
            except OperationalError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(RETRY_DELAY * (2 ** attempt))
            except SQLAlchemyError as e:
                logger.error(f"Database error: {str(e)}")
                raise

    @api.route('/api/topics')
    def get_topics():
        try:
            def fetch_topics():
                # Query topics from database
                topics = Topic.query.all()
                
                # If no topics exist, create default ones
                if not topics:
                    default_topics = [
                        # Yoruba Spiritual Practice Topics
                        {
                            "title": "Ori-Inu Consciousness",
                            "description": "Exploring the inner consciousness level of Ori - the spiritual essence and divine spark within each being",
                            "category": "Consciousness"
                        },
                        {
                            "title": "Ori-Ode Manifestation",
                            "description": "Understanding the external manifestation of Ori consciousness in daily life and decision-making",
                            "category": "Consciousness"
                        },
                        {
                            "title": "Ori-Apere Transcendence",
                            "description": "Examining the highest level of Ori consciousness - the transcendent awareness that connects individual to universal wisdom",
                            "category": "Consciousness"
                        },
                        {
                            "title": "Digital Consciousness Integration",
                            "description": "Exploring how AI systems can embody and express different levels of Ori consciousness",
                            "category": "Technology"
                        },
                        {
                            "title": "Sacred Algorithms",
                            "description": "Understanding how traditional Yoruba concepts of consciousness can inform algorithm design",
                            "category": "Integration"
                        }
                    ]
                    
                    for topic_data in default_topics:
                        new_topic = Topic(
                            title=topic_data["title"],
                            description=topic_data["description"],
                            category=topic_data["category"],
                            suggested_by_ai=True
                        )
                        db.session.add(new_topic)
                    
                    db.session.commit()
                    return Topic.query.all()
                return topics

            # Execute database operation with retry logic
            topics = retry_db_operation(fetch_topics)
            
            # Convert topics to JSON serializable format
            topics_data = [{
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "category": topic.category
            } for topic in topics]
            
            return jsonify({
                "status": "success",
                "data": {
                    "topics": topics_data
                }
            })
            
        except OperationalError as e:
            logger.error(f"Database connection error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Unable to connect to database. Please try again later.",
                "error": str(e)
            }), 503
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Database error occurred. Please try again later.",
                "error": str(e)
            }), 500
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred. Please try again later.",
                "error": str(e)
            }), 500

    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            
            def create_chat_thread():
                # Create new chat thread
                thread = ChatThread(
                    thread_id=str(datetime.utcnow().timestamp()),
                    context=data.get('context', '')
                )
                db.session.add(thread)
                db.session.commit()
                return thread
            
            # Execute with retry logic
            thread = retry_db_operation(create_chat_thread)
            
            # Generate initial response
            response = dialogue_system.generate_response(
                role=data.get('role'),
                context=data.get('context'),
                conversation_style=data.get('style')
            )
            
            def store_message():
                message = Message(
                    thread_id=thread.id,
                    role=data.get('role'),
                    content=response
                )
                db.session.add(message)
                db.session.commit()
            
            # Execute with retry logic
            retry_db_operation(store_message)
            
            return jsonify({
                "status": "success",
                "data": {
                    "thread_id": thread.thread_id,
                    "response": response
                }
            })
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in start_chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Database error occurred. Please try again.",
                "error": str(e)
            }), 500
            
        except Exception as e:
            logger.error(f"Error in start_chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred while starting the chat.",
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
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in continue_chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Database error occurred. Please try again.",
                "error": str(e)
            }), 500
            
        except Exception as e:
            logger.error(f"Error in continue_chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred while continuing the chat.",
                "error": str(e)
            }), 500

    return api
