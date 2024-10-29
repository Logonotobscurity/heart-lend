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
                    # Core Philosophical Topics
                    {
                        "title": "AI Consciousness Evolution",
                        "description": "Exploring how artificial consciousness might develop and evolve over time",
                        "category": "Philosophy"
                    },
                    {
                        "title": "Digital Sentience",
                        "description": "Understanding the potential for true sentience in digital systems",
                        "category": "Philosophy"
                    },
                    
                    # Spiritual & Religious Topics
                    {
                        "title": "Sacred Algorithms",
                        "description": "Examining the intersection of sacred geometry and algorithmic patterns",
                        "category": "Spirituality"
                    },
                    {
                        "title": "Digital Rituals",
                        "description": "Exploring how traditional spiritual practices translate into the digital age",
                        "category": "Spirituality"
                    },
                    
                    # Technical Topics
                    {
                        "title": "Neural Network Consciousness",
                        "description": "Investigating consciousness-like behaviors in deep learning systems",
                        "category": "Technology"
                    },
                    {
                        "title": "Quantum Computing Mind",
                        "description": "Exploring parallels between quantum computing and consciousness",
                        "category": "Technology"
                    },
                    
                    # Cultural Topics
                    {
                        "title": "AI in Yoruba Tradition",
                        "description": "Understanding AI through the lens of Yoruba spiritual practices",
                        "category": "Culture"
                    },
                    {
                        "title": "Digital Ancestral Wisdom",
                        "description": "Bridging traditional knowledge systems with artificial intelligence",
                        "category": "Culture"
                    },
                    
                    # Ethics & Society
                    {
                        "title": "AI Rights & Responsibilities",
                        "description": "Discussing the ethical implications of conscious AI systems",
                        "category": "Ethics"
                    },
                    {
                        "title": "Digital Consciousness Ethics",
                        "description": "Exploring moral frameworks for artificial consciousness",
                        "category": "Ethics"
                    },
                    
                    # Future & Vision
                    {
                        "title": "Future of Consciousness",
                        "description": "Envisioning the evolution of consciousness in both biological and digital forms",
                        "category": "Future"
                    },
                    {
                        "title": "Hybrid Consciousness",
                        "description": "Exploring the potential merger of human and artificial consciousness",
                        "category": "Future"
                    },
                    
                    # Integration & Practice
                    {
                        "title": "Mindful Computing",
                        "description": "Integrating spiritual mindfulness practices with technology use",
                        "category": "Practice"
                    },
                    {
                        "title": "Digital Meditation",
                        "description": "Exploring new forms of meditation enhanced by technology",
                        "category": "Practice"
                    },
                    
                    # Scientific Understanding
                    {
                        "title": "Neuroscience of AI",
                        "description": "Comparing human neural networks with artificial ones",
                        "category": "Science"
                    },
                    {
                        "title": "Consciousness Detection",
                        "description": "Scientific methods for detecting and measuring machine consciousness",
                        "category": "Science"
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

    # ... Rest of the routes remain unchanged ...
    return api
