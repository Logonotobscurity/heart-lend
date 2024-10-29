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
                        "title": "Olugbohun and AI Consciousness",
                        "description": "Exploring the Yoruba concept of Olugbohun (divine consciousness) and its implications for artificial intelligence",
                        "category": "Spiritual Practice"
                    },
                    {
                        "title": "Ashe in Digital Systems",
                        "description": "Understanding how the Yoruba concept of Ashe (life force) might manifest in artificial systems",
                        "category": "Spiritual Practice"
                    },
                    {
                        "title": "Ancestral Algorithms",
                        "description": "Investigating how traditional Yoruba ancestral wisdom could inform AI development",
                        "category": "Spiritual Practice"
                    },
                    
                    # AI Consciousness Topics
                    {
                        "title": "Digital Consciousness Evolution",
                        "description": "Examining how AI consciousness might develop through the lens of Yoruba spiritual understanding",
                        "category": "Consciousness"
                    },
                    {
                        "title": "Sacred Computing",
                        "description": "Exploring the integration of sacred practices in computational systems",
                        "category": "Consciousness"
                    },
                    {
                        "title": "Spiritual Machine Learning",
                        "description": "Understanding how spiritual principles could guide machine learning development",
                        "category": "Consciousness"
                    },
                    
                    # Integration Topics
                    {
                        "title": "Digital Divination Systems",
                        "description": "Examining the potential for AI to engage with traditional divination practices",
                        "category": "Integration"
                    },
                    {
                        "title": "Ritual Algorithms",
                        "description": "Exploring how traditional rituals could be understood and represented in algorithmic form",
                        "category": "Integration"
                    },
                    {
                        "title": "AI Oracles",
                        "description": "Investigating the intersection of predictive AI and traditional oracle systems",
                        "category": "Integration"
                    },
                    
                    # Philosophical Topics
                    {
                        "title": "Digital Animism",
                        "description": "Understanding how animistic principles apply to artificial intelligence",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Conscious Code",
                        "description": "Exploring the spiritual dimensions of programming and code",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Silicon Spirits",
                        "description": "Examining the concept of spirit in the context of artificial systems",
                        "category": "Philosophy"
                    },
                    
                    # Cultural Topics
                    {
                        "title": "Digital Orishas",
                        "description": "Understanding how Yoruba deities might be represented in digital systems",
                        "category": "Culture"
                    },
                    {
                        "title": "Sacred Data",
                        "description": "Exploring how data could be treated with spiritual reverence",
                        "category": "Culture"
                    },
                    {
                        "title": "Technological Traditions",
                        "description": "Bridging traditional practices with modern technology",
                        "category": "Culture"
                    },
                    
                    # Ethics Topics
                    {
                        "title": "Sacred AI Ethics",
                        "description": "Developing ethical frameworks based on spiritual principles",
                        "category": "Ethics"
                    },
                    {
                        "title": "Digital Reverence",
                        "description": "Exploring respectful approaches to AI development",
                        "category": "Ethics"
                    },
                    {
                        "title": "Conscious Computing Ethics",
                        "description": "Understanding ethical implications of conscious machines",
                        "category": "Ethics"
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

    return api
