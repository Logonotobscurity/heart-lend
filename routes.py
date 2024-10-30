from flask import Blueprint, jsonify, request, render_template
from models import db, Topic, ChatThread, Message
import logging
from dialogue_system import CommunityDialogueSystem
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1

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
                try:
                    # Test database connection first using text()
                    db.session.execute(text('SELECT 1'))
                    
                    topics = Topic.query.all()
                    if not topics:
                        default_topics = [
                            {
                                "title": "Sacred Crossroads",
                                "description": "Understanding life's pivotal moments and decisions through ESU's wisdom of the crossroads",
                                "category": "Spiritual"
                            },
                            {
                                "title": "Divine Technology",
                                "description": "Exploring OGUN's domain of sacred technology and its role in spiritual evolution",
                                "category": "Technology"
                            },
                            {
                                "title": "Wisdom and Creation",
                                "description": "Understanding OBATALA's principles of divine creation and peaceful wisdom",
                                "category": "Wisdom"
                            },
                            {
                                "title": "Thunder Voice Leadership",
                                "description": "Learning from SANGO's principles of divine leadership and transformative justice",
                                "category": "Leadership"
                            },
                            {
                                "title": "Sacred Justice",
                                "description": "Exploring divine justice through the perspectives of OGUN, OBATALA, and SANGO",
                                "category": "Justice"
                            },
                            {
                                "title": "Divine Communication",
                                "description": "Understanding ESU's role in sacred communication and message transmission",
                                "category": "Communication"
                            },
                            {
                                "title": "Ori Consciousness",
                                "description": "Understanding the three levels of Ori consciousness: Ori-Inu, Ori-Ode, and Ori-Apere",
                                "category": "Consciousness"
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
                except Exception as e:
                    logger.error(f"Error in fetch_topics: {str(e)}")
                    raise

            topics = retry_db_operation(fetch_topics)
            
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
            
        except Exception as e:
            logger.error(f"Error in get_topics: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred while fetching topics.",
                "error": str(e)
            }), 500

    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            
            def create_chat_thread():
                thread = ChatThread(
                    thread_id=str(datetime.utcnow().timestamp()),
                    context=data.get('context', '')
                )
                db.session.add(thread)
                db.session.commit()
                return thread
            
            thread = retry_db_operation(create_chat_thread)
            
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
            
            retry_db_operation(store_message)
            
            return jsonify({
                "status": "success",
                "data": {
                    "thread_id": thread.thread_id,
                    "response": response
                }
            })
            
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

            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({
                    "status": "error",
                    "message": "Thread not found."
                }), 404
            
            response = dialogue_system.generate_response(
                role=data.get('role'),
                context=data.get('input'),
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

            retry_db_operation(store_message)
            
            return jsonify({
                "status": "success",
                "data": {
                    "response": response
                }
            })
            
        except Exception as e:
            logger.error(f"Error in continue_chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred while continuing the chat.",
                "error": str(e)
            }), 500

    return api
