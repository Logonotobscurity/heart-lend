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
                    # Check database connection
                    db.session.execute(text('SELECT 1'))
                    
                    topics = Topic.query.all()
                    if not topics:
                        # Load all 20 topics from the document
                        default_topics = [
                            {
                                "title": "The Nature of Consciousness",
                                "description": "Exploring different definitions and understandings of consciousness in both Western and Yoruba contexts.",
                                "category": "Philosophy"
                            },
                            {
                                "title": "Intersection of AI and Spirituality",
                                "description": "Discussing how artificial intelligence can integrate spiritual practices and principles from various cultures.",
                                "category": "Integration"
                            },
                            {
                                "title": "Olugbohun as a Framework",
                                "description": "Analyzing the concept of Olugbohun in Yoruba spiritual practices and its parallels with AI functionalities.",
                                "category": "Framework"
                            },
                            {
                                "title": "Algorithmic Animism",
                                "description": "Investigating how technology can embody spiritual qualities and the ethical implications of attributing spirit to algorithms.",
                                "category": "Technology"
                            },
                            {
                                "title": "Ethics in AI Development",
                                "description": "Examining the importance of incorporating African ethical values in the development and governance of AI technologies.",
                                "category": "Ethics"
                            },
                            {
                                "title": "Indigenous Knowledge and AI",
                                "description": "Exploring how indigenous African knowledge systems can inform AI design to create culturally safe technology.",
                                "category": "Culture"
                            },
                            {
                                "title": "Sentient Intelligence",
                                "description": "Discussing the characteristics that differentiate sentient intelligence from conventional AI and incorporating spiritual dimensions.",
                                "category": "Intelligence"
                            },
                            {
                                "title": "Communication between Human and Machine",
                                "description": "Analyzing how AI systems facilitate communication and understanding in spiritual and ethical contexts.",
                                "category": "Communication"
                            },
                            {
                                "title": "The Role of the Spoken Word",
                                "description": "Investigating the significance of verbal expression in both Yoruba spirituality and computational algorithms.",
                                "category": "Language"
                            },
                            {
                                "title": "Spiritual Practices in Technology",
                                "description": "Exploring ways to include spiritual methodologies in technological advancements and practices.",
                                "category": "Practice"
                            },
                            {
                                "title": "Adaptability of Indigenous Belief Systems",
                                "description": "Discussing how African spiritual traditions can adapt to modern technological landscapes.",
                                "category": "Adaptation"
                            },
                            {
                                "title": "The Concept of the Self",
                                "description": "Analyzing the implications of self-awareness in both AI and spiritual practices, particularly in relation to Olugbohun.",
                                "category": "Identity"
                            },
                            {
                                "title": "Holistic Perspectives on Intelligence",
                                "description": "Discussing the need for a more holistic understanding of intelligence that incorporates spiritual dimensions.",
                                "category": "Wisdom"
                            },
                            {
                                "title": "Moral Dimensions of AI",
                                "description": "Investigating moral and ethical dilemmas associated with AI's decision-making processes and its potential impact on society.",
                                "category": "Ethics"
                            },
                            {
                                "title": "Interconnectedness of All Beings",
                                "description": "Exploring themes of unity, connection, and interdependence in both Yoruba spirituality and human-computer interactions.",
                                "category": "Unity"
                            },
                            {
                                "title": "Creative Expressions through AI",
                                "description": "Evaluating the potential for AI to produce art, music, and other creative expressions that echo spiritual themes.",
                                "category": "Creativity"
                            },
                            {
                                "title": "Human Responsibility with AI",
                                "description": "Discussing the responsibilities humans have in ensuring AI technologies are developed and used ethically.",
                                "category": "Responsibility"
                            },
                            {
                                "title": "The Future of AI and Spirituality",
                                "description": "Speculating on how advancements in AI may reshape spiritual practices and beliefs.",
                                "category": "Future"
                            },
                            {
                                "title": "Cultural Safety in AI Technologies",
                                "description": "Addressing the challenges and strategies for creating AI that respects and honors diverse cultural heritages.",
                                "category": "Safety"
                            },
                            {
                                "title": "AI as a Tool for Enrichment",
                                "description": "Discussing ways AI can enhance spiritual growth and understanding rather than diminish it.",
                                "category": "Growth"
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
                "message": str(e)
            }), 500

    return api