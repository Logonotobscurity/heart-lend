from flask import render_template, jsonify, request
import logging
from models import db, Topic, ChatThread, Message
from visualization import ConversationVisualizer
from dialogue_system import CommunityDialogueSystem
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_routes(app):
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

            # For now, return predefined topics based on the document
            topics = [
                {"id": 1, "title": "Nature of Consciousness", 
                 "description": "Exploring different definitions of consciousness in Western and Yoruba contexts",
                 "category": "Philosophy"},
                {"id": 2, "title": "AI and Spirituality",
                 "description": "Discussing how AI can integrate spiritual practices and principles",
                 "category": "Technology"},
                {"id": 3, "title": "Algorithmic Animism",
                 "description": "Investigating how technology can embody spiritual qualities",
                 "category": "Culture"}
            ]
            return jsonify({"status": "success", "topics": topics})
        except Exception as e:
            logger.error(f"Error suggesting topics: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/start_dialogue', methods=['POST'])
    def start_dialogue():
        try:
            data = request.get_json()
            if not data or not all(k in data for k in ['role', 'context']):
                return jsonify({"error": "Missing required fields"}), 400

            # Create new thread
            thread = ChatThread()
            thread.context = data['context']
            thread.topic_id = data.get('topic_id')
            db.session.add(thread)
            db.session.flush()
            
            # Generate initial response
            response = dialogue_system.generate_response(data['role'], data['context'])
            
            # Store message
            message = Message()
            message.thread_id = thread.id
            message.role = data['role']
            message.content = response
            db.session.add(message)
            db.session.commit()

            return jsonify({
                "status": "success",
                "thread_id": thread.id,
                "response": response
            })
        except Exception as e:
            logger.error(f"Error starting dialogue: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/continue_dialogue', methods=['POST'])
    def continue_dialogue():
        try:
            data = request.get_json()
            if not data or not all(k in data for k in ['thread_id', 'role', 'message']):
                return jsonify({"error": "Missing required fields"}), 400

            # Get thread
            thread = ChatThread.query.get(data['thread_id'])
            if not thread:
                return jsonify({"error": "Thread not found"}), 404

            # Get previous messages
            previous_messages = [msg.content for msg in 
                Message.query.filter_by(thread_id=thread.id).order_by(Message.timestamp).all()]

            # Generate response
            response = dialogue_system.generate_layered_response(
                str(thread.id),
                data['role'],
                data['message'],
                previous_messages
            )

            # Store message
            message = Message()
            message.thread_id = thread.id
            message.role = data['role']
            message.content = response
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
        return render_template('visualization.html', thread_id=thread_id)

    @app.route('/api/visualization/<thread_id>')
    def get_visualization_data(thread_id):
        try:
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
