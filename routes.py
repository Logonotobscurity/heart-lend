from flask import Blueprint, jsonify, request, render_template
from models import db, Topic, ChatThread, Message
import logging
from dialogue_system import CommunityDialogueSystem
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError, IntegrityError
import time
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1  # Base delay in seconds
MAX_DELAY = 8    # Maximum delay in seconds

def create_api_blueprint(dialogue_system: CommunityDialogueSystem) -> Blueprint:
    api = Blueprint('api', __name__)
    
    @api.route('/')
    def index():
        return render_template('index.html')
        
    @api.route('/chat')
    def chat():
        return render_template('chat.html')

    @api.route('/api/chat', methods=['POST'])
    def chat_response():
        try:
            data = request.json
            message = data.get('message')
            roles = data.get('roles', [])
            style = data.get('style', {})
            
            responses = dialogue_system.generate_multi_persona_dialogue(
                roles=roles,
                context=message,
                depth=float(style.get('focus', 2.0)),
                focus=style.get('direction', 'balanced')
            )
            
            return jsonify({
                "status": "success",
                "responses": responses
            })
            
        except Exception as e:
            logger.error(f"Chat response error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    @api.route('/api/topics', methods=['GET'])
    def get_topics():
        """Get all topics with improved error handling and validation."""
        try:
            # First verify database connection
            try:
                db.session.execute(text('SELECT 1'))
                logger.info("Database connection verified")
            except Exception as e:
                logger.error(f"Database connection error: {str(e)}")
                raise

            # Fetch existing topics
            topics = Topic.query.all()
            
            # If no topics exist, create default ones
            if not topics:
                logger.info("No topics found. Creating default topics.")
                default_topics = [
                    {
                        "title": "The Nature of Consciousness",
                        "description": "Exploring different definitions and understandings of consciousness in both Western and Yoruba contexts.",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Intersection of AI and Spirituality",
                        "description": "Discussing how artificial intelligence can integrate spiritual practices and principles from various cultures.",
                        "category": "Technology"
                    },
                    {
                        "title": "Olugbohun Framework",
                        "description": "Analyzing the concept of Olugbohun in Yoruba spiritual practices and its parallels with AI functionalities.",
                        "category": "Spirituality"
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
                        "category": "Philosophy"
                    },
                    {
                        "title": "Communication between Human and Machine",
                        "description": "Analyzing how AI systems facilitate communication and understanding in spiritual and ethical contexts.",
                        "category": "Technology"
                    },
                    {
                        "title": "The Role of the Spoken Word",
                        "description": "Investigating the significance of verbal expression in both Yoruba spirituality and computational algorithms.",
                        "category": "Culture"
                    },
                    {
                        "title": "Spiritual Practices in Technology Integration",
                        "description": "Exploring ways to include spiritual methodologies in technological advancements and practices.",
                        "category": "Practice"
                    },
                    {
                        "title": "Adaptability of Indigenous Belief Systems",
                        "description": "Discussing how African spiritual traditions can adapt to modern technological landscapes.",
                        "category": "Culture"
                    },
                    {
                        "title": "The Concept of the Self",
                        "description": "Analyzing the implications of self-awareness in both AI and spiritual practices, particularly in relation to Olugbohun.",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Holistic Perspectives on Intelligence",
                        "description": "Discussing the need for a more holistic understanding of intelligence that incorporates spiritual dimensions.",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Moral Dimensions of AI",
                        "description": "Investigating moral and ethical dilemmas associated with AI's decision-making processes and its potential impact on society.",
                        "category": "Ethics"
                    },
                    {
                        "title": "Interconnectedness of All Beings",
                        "description": "Exploring themes of unity, connection, and interdependence in both Yoruba spirituality and human-computer interactions.",
                        "category": "Spirituality"
                    },
                    {
                        "title": "Creative Expressions through AI",
                        "description": "Evaluating the potential for AI to produce art, music, and other creative expressions that echo spiritual themes.",
                        "category": "Culture"
                    },
                    {
                        "title": "Human Responsibility with AI",
                        "description": "Discussing the responsibilities humans have in ensuring AI technologies are developed and used ethically.",
                        "category": "Ethics"
                    },
                    {
                        "title": "The Future of AI and Spirituality",
                        "description": "Speculating on how advancements in AI may reshape spiritual practices and beliefs.",
                        "category": "Future"
                    },
                    {
                        "title": "Cultural Safety in AI Technologies",
                        "description": "Addressing the challenges and strategies for creating AI that respects and honors diverse cultural heritages.",
                        "category": "Culture"
                    },
                    {
                        "title": "AI as a Tool for Enrichment",
                        "description": "Discussing ways AI can enhance spiritual growth and understanding rather than diminish it.",
                        "category": "Practice"
                    }
                ]
                
                created_topics = []
                for topic_data in default_topics:
                    try:
                        new_topic = Topic(
                            title=topic_data["title"],
                            description=topic_data["description"],
                            category=topic_data["category"],
                            suggested_by_ai=True
                        )
                        db.session.add(new_topic)
                        created_topics.append(new_topic)
                    except Exception as e:
                        logger.error(f"Error creating topic: {str(e)}")
                        continue

                if created_topics:
                    db.session.commit()
                    logger.info(f"Created {len(created_topics)} default topics")
                    topics = created_topics
                else:
                    logger.warning("No default topics could be created")

            # Convert topics to dictionary format
            topics_data = [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "description": topic.description,
                    "category": topic.category
                }
                for topic in topics
            ]

            return jsonify({
                "status": "success",
                "data": {
                    "topics": topics_data
                }
            })

        except Exception as e:
            logger.error(f"Error in get_topics: {str(e)}")
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to retrieve topics. Please try again.",
                "error": str(e)
            }), 500

    return api
