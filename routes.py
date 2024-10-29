from flask import Blueprint, jsonify, request, render_template
from models import db, Topic, ChatThread, Message
import logging
from dialogue_system import CommunityDialogueSystem
from datetime import datetime

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

    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "No data provided"}), 400

            initial_role = data.get('role')
            context = data.get('context')
            selected_personas = data.get('selected_personas', [])
            
            if not initial_role or not context:
                return jsonify({"status": "error", "message": "Missing required fields"}), 400

            # Start dialogue thread with selected personas
            thread = ChatThread(
                thread_id=str(datetime.utcnow().timestamp()),
                context=context
            )
            db.session.add(thread)
            
            # Generate initial response
            response = dialogue_system.generate_response(
                initial_role, 
                context,
                conversation_style={
                    "direction": "balanced",
                    "focus": 2.0
                }
            )
            
            # Store message
            message = Message(
                thread_id=thread.id,
                role=initial_role,
                content=response
            )
            db.session.add(message)
            db.session.commit()

            return jsonify({
                "status": "success",
                "data": {
                    "thread_id": thread.thread_id,
                    "response": response
                }
            })

        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to start chat thread"
            }), 500

    @api.route('/api/chat/continue', methods=['POST'])
    def continue_chat():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "No data provided"}), 400

            thread_id = data.get('thread_id')
            role = data.get('role')
            user_input = data.get('input')
            selected_personas = data.get('selected_personas', [])
            conversation_style = data.get('style')

            if not all([thread_id, role, user_input]):
                return jsonify({"status": "error", "message": "Missing required fields"}), 400

            # Get thread
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({"status": "error", "message": "Thread not found"}), 404

            # Store user message
            user_message = Message(
                thread_id=thread.id,
                role="user",
                content=user_input
            )
            db.session.add(user_message)

            # Generate AI response
            response = dialogue_system.generate_layered_response(
                thread_id,
                role,
                user_input,
                conversation_style
            )

            # Store AI response
            ai_message = Message(
                thread_id=thread.id,
                role=role,
                content=response
            )
            db.session.add(ai_message)
            db.session.commit()

            return jsonify({
                "status": "success",
                "data": {
                    "response": response
                }
            })

        except Exception as e:
            logger.error(f"Error continuing chat: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to continue chat"
            }), 500

    # ... [rest of the routes remain unchanged] ...
    
    return api
