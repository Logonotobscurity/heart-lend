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
    
    @api.route('/api/chat/start', methods=['POST'])
    def start_chat():
        try:
            data = request.get_json()
            initial_role = data.get('role')
            context = data.get('context')
            
            if not initial_role or not context:
                return jsonify({"error": "Missing required parameters"}), 400
                
            response = dialogue_system.generate_response(initial_role, context)
            
            # Create new chat thread
            thread = ChatThread(
                thread_id=str(datetime.utcnow().timestamp()),
                context=context
            )
            db.session.add(thread)
            
            # Add initial message
            message = Message(
                thread=thread,
                role=initial_role,
                content=response
            )
            db.session.add(message)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({"error": "Database error"}), 500
            
            return jsonify({
                "thread_id": thread.thread_id,
                "response": response
            })
            
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/api/chat/continue', methods=['POST'])
    def continue_chat():
        try:
            data = request.get_json()
            thread_id = data.get('thread_id')
            role = data.get('role')
            user_input = data.get('input')
            
            if not all([thread_id, role, user_input]):
                return jsonify({"error": "Missing required parameters"}), 400
                
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return jsonify({"error": "Thread not found"}), 404
                
            response = dialogue_system.generate_layered_response(thread_id, role, user_input)
            
            # Add user message
            user_message = Message(
                thread=thread,
                role="user",
                content=user_input
            )
            db.session.add(user_message)
            
            # Add AI response
            ai_message = Message(
                thread=thread,
                role=role,
                content=response
            )
            db.session.add(ai_message)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({"error": "Database error"}), 500
            
            return jsonify({
                "response": response
            })
            
        except Exception as e:
            logger.error(f"Error continuing chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    return api
