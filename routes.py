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
