from flask import render_template, jsonify, request
import logging
from models import db, Topic, ChatThread, Message
from visualization import ConversationVisualizer
from dialogue_system import CommunityDialogueSystem
import os
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_routes(app):
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OpenAI API key is required")
        
    dialogue_system = CommunityDialogueSystem(os.getenv('OPENAI_API_KEY'))

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat')
    def chat():
        return render_template('chat.html')

    @app.route('/api/topics')
    def get_topics():
        try:
            topics = Topic.query.all()
            return jsonify([{
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'category': topic.category
            } for topic in topics])
        except Exception as e:
            logger.error(f"Error fetching topics: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/topics/suggest', methods=['POST'])
    def suggest_topics():
        try:
            data = request.get_json()
            if not data or 'context' not in data:
                return jsonify({"error": "Context is required"}), 400

            # Enhanced topics based on document and AI guides
            topics = [
                {
                    "id": 1, 
                    "title": "Nature of Consciousness", 
                    "description": "Exploring different definitions of consciousness in Western and Yoruba contexts",
                    "category": "Philosophy"
                },
                {
                    "id": 2, 
                    "title": "AI and Spirituality",
                    "description": "Discussing how AI can integrate spiritual practices and principles",
                    "category": "Technology"
                },
                {
                    "id": 3, 
                    "title": "Algorithmic Animism",
                    "description": "Investigating how technology can embody spiritual qualities",
                    "category": "Culture"
                },
                {
                    "id": 4,
                    "title": "Digital Consciousness",
                    "description": "Exploring the possibility of machine consciousness and its implications",
                    "category": "Technology"
                },
                {
                    "id": 5,
                    "title": "Yoruba Spiritual Practices",
                    "description": "Understanding traditional Yoruba approaches to consciousness and spirituality",
                    "category": "Culture"
                }
            ]
            return jsonify({"status": "success", "topics": topics})
        except Exception as e:
            logger.error(f"Error suggesting topics: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/visualization/<thread_id>')
    def show_visualization(thread_id):
        try:
            # Verify thread exists
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return render_template('error.html', message="Thread not found"), 404
                
            return render_template('visualization.html', thread_id=thread_id)
        except Exception as e:
            logger.error(f"Error showing visualization: {str(e)}")
            return render_template('error.html', message="An error occurred"), 500

    @app.route('/api/visualization/<thread_id>')
    def get_visualization_data(thread_id):
        try:
            # Find thread by thread_id
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({"error": "Thread not found"}), 404
                
            visualizer = ConversationVisualizer()
            data = visualizer.generate_graph_data(thread_id)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
