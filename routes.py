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

    @app.route('/api/update_conversation_style', methods=['POST'])
    def update_conversation_style():
        try:
            data = request.get_json()
            if not data or 'thread_id' not in data:
                return jsonify({"error": "Thread ID is required"}), 400

            thread = ChatThread.query.filter_by(thread_id=data['thread_id']).first()
            if not thread:
                return jsonify({"error": "Thread not found"}), 404

            thread.metadata = {
                'direction': data.get('direction', 'balanced'),
                'focus': data.get('focus', 2)
            }
            db.session.commit()

            return jsonify({"status": "success"})
        except Exception as e:
            logger.error(f"Error updating conversation style: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/start_dialogue', methods=['POST'])
    def start_dialogue():
        try:
            data = request.get_json()
            thread_id = str(uuid.uuid4())
            
            thread = ChatThread(
                thread_id=thread_id,
                context=data.get('context'),
                topic_id=data.get('topic_id'),
                metadata={
                    'direction': data.get('direction', 'balanced'),
                    'focus': data.get('focus', 2)
                }
            )
            db.session.add(thread)
            
            response = dialogue_system.generate_response(
                data['role'],
                data['context'],
                conversation_style={
                    'direction': data.get('direction', 'balanced'),
                    'focus': data.get('focus', 2)
                }
            )
            
            message = Message(
                thread_id=thread.id,
                role=data['role'],
                content=response
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "thread_id": thread_id,
                "response": response
            })
        except Exception as e:
            logger.error(f"Error starting dialogue: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/continue_dialogue', methods=['POST'])
    def continue_dialogue():
        try:
            data = request.get_json()
            thread = ChatThread.query.filter_by(thread_id=data['thread_id']).first()
            
            if not thread:
                return jsonify({"error": "Thread not found"}), 404
            
            if 'direction' in data or 'focus' in data:
                thread.metadata = {
                    'direction': data.get('direction', thread.metadata.get('direction', 'balanced')),
                    'focus': data.get('focus', thread.metadata.get('focus', 2))
                }
            
            response = dialogue_system.generate_layered_response(
                thread.id,
                data['role'],
                data['message'],
                conversation_style=thread.metadata
            )
            
            message = Message(
                thread_id=thread.id,
                role=data['role'],
                content=response
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "response": response
            })
        except Exception as e:
            logger.error(f"Error continuing dialogue: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/visualization/<thread_id>')
    def show_visualization(thread_id):
        try:
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
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({"error": "Thread not found"}), 404
                
            visualizer = ConversationVisualizer()
            data = visualizer.generate_graph_data(thread_id)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return app