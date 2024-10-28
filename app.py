import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dialogue_system import CommunityDialogueSystem
import openai
import random
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

dialogue_system = CommunityDialogueSystem(
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/topics', methods=['GET'])
def get_topics():
    from models import Topic
    category = request.args.get('category')
    query = Topic.query
    if category:
        query = query.filter_by(category=category)
    topics = query.order_by(Topic.created_at.desc()).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'category': t.category
    } for t in topics])

@app.route('/api/topics/suggest', methods=['POST'])
def suggest_topic():
    from models import Topic
    current_context = request.json.get('context')
    if not current_context:
        return jsonify({"status": "error", "message": "Context is required"}), 400
    
    try:
        # Generate topic suggestions using OpenAI
        prompt = """Based on the conversation context, suggest 3 related discussion topics.
        Each topic should include:
        - A clear, engaging title
        - A brief description explaining the topic
        - A category (Philosophy, Technology, Spirituality, Ethics, or Culture)
        
        Format the response as a JSON object with this structure:
        {
            "topics": [
                {
                    "title": "Topic Title",
                    "description": "Topic description",
                    "category": "Category"
                }
            ]
        }"""
        
        response = dialogue_system.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Context: {current_context}"}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        if response.choices and response.choices[0].message:
            suggestions = json.loads(response.choices[0].message.content)
            new_topics = []
            
            for suggestion in suggestions.get('topics', []):
                if all(key in suggestion for key in ['title', 'description', 'category']):
                    topic = Topic()
                    topic.title = suggestion['title']
                    topic.description = suggestion['description']
                    topic.category = suggestion['category']
                    topic.suggested_by_ai = True
                    db.session.add(topic)
                    new_topics.append({
                        'id': None,  # Will be set after commit
                        'title': suggestion['title'],
                        'description': suggestion['description'],
                        'category': suggestion['category']
                    })
            
            db.session.commit()
            
            # Update topic IDs after commit
            for i, topic in enumerate(new_topics):
                topic_obj = Topic.query.filter_by(
                    title=topic['title'],
                    description=topic['description']
                ).first()
                if topic_obj:
                    topic['id'] = topic_obj.id
            
            return jsonify({"status": "success", "topics": new_topics})
        else:
            return jsonify({"status": "error", "message": "Failed to generate suggestions"}), 500
    
    except Exception as e:
        logger.error(f"Error suggesting topics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/start_dialogue', methods=['POST'])
def start_dialogue():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        initial_role = data.get('role')
        context = data.get('context')
        topic_id = data.get('topic_id')
        
        if not all([initial_role, context]):
            return jsonify({"status": "error", "message": "Role and context are required"}), 400
        
        # Get topic if provided
        topic_context = ""
        if topic_id:
            from models import Topic
            topic = Topic.query.get(topic_id)
            if topic:
                topic_context = f"{topic.title}: {topic.description}"
        
        # Generate initial response using the dialogue system
        full_context = f"{topic_context}\n{context}" if topic_context else context
        response = dialogue_system.generate_response(initial_role, full_context)
        thread_id = str(random.randint(1000000, 9999999))
        
        # Save thread if topic provided
        if topic_id:
            from models import ChatThread
            thread = ChatThread()
            thread.thread_id = thread_id
            thread.context = context
            thread.topic_id = topic_id
            db.session.add(thread)
            db.session.commit()
        
        return jsonify({
            "status": "success",
            "thread_id": thread_id,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error starting dialogue: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/continue_dialogue', methods=['POST'])
def continue_dialogue():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        thread_id = data.get('thread_id')
        role = data.get('role')
        user_input = data.get('message')
        
        if not all([thread_id, role, user_input]):
            return jsonify({"status": "error", "message": "Thread ID, role, and message are required"}), 400
        
        from models import Message, ChatThread
        thread = ChatThread.query.filter_by(thread_id=thread_id).first()
        if not thread:
            return jsonify({"status": "error", "message": "Thread not found"}), 404
            
        # Calculate depth level based on message count
        depth_level = min(1 + Message.query.filter_by(thread_id=thread.id).count() // 2, 3)
        
        # Generate response using the dialogue system
        previous_messages = Message.query.filter_by(thread_id=thread.id, role='assistant').all()
        previous_responses = [msg.content for msg in previous_messages]
        
        response = dialogue_system.generate_layered_response(
            thread_id=thread_id,
            role=role,
            user_input=user_input,
            previous_responses=previous_responses,
            depth_level=depth_level
        )
        
        # Save the message
        message = Message()
        message.thread_id = thread.id
        message.role = role
        message.content = response
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "thread_id": thread_id,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error continuing dialogue: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Initialize database and add themes
with app.app_context():
    import models
    db.create_all()
    
    # Add initial themes if none exist
    if models.Topic.query.count() == 0:
        themes = [
            {
                'title': 'The Nature of Consciousness',
                'description': 'Exploring different definitions and understandings of consciousness in both Western and Yoruba contexts.',
                'category': 'Philosophy'
            },
            {
                'title': 'Intersection of AI and Spirituality',
                'description': 'Discussing how artificial intelligence can integrate spiritual practices and principles from various cultures.',
                'category': 'Spirituality'
            },
            {
                'title': 'Olugbohun as a Framework',
                'description': 'Analyzing the concept of Olugbohun in Yoruba spiritual practices and its parallels with AI functionalities.',
                'category': 'Technology'
            },
            {
                'title': 'Algorithmic Animism',
                'description': 'Investigating how technology can embody spiritual qualities and the ethical implications of attributing spirit to algorithms.',
                'category': 'Ethics'
            },
            {
                'title': 'Indigenous Knowledge and AI',
                'description': 'Exploring how indigenous African knowledge systems can inform AI design to create culturally safe technology.',
                'category': 'Technology'
            },
            {
                'title': 'Sentient Intelligence',
                'description': 'Discussing the characteristics that differentiate sentient intelligence from conventional AI and incorporating spiritual dimensions.',
                'category': 'Philosophy'
            },
            {
                'title': 'Communication between Human and Machine',
                'description': 'Analyzing how AI systems facilitate communication and understanding in spiritual and ethical contexts.',
                'category': 'Technology'
            },
            {
                'title': 'The Role of the Spoken Word',
                'description': 'Investigating the significance of verbal expression in both Yoruba spirituality and computational algorithms.',
                'category': 'Culture'
            },
            {
                'title': 'Spiritual Practices in Technology',
                'description': 'Exploring ways to include spiritual methodologies in technological advancements and practices.',
                'category': 'Spirituality'
            },
            {
                'title': 'The Concept of the Self',
                'description': 'Analyzing the implications of self-awareness in both AI and spiritual practices, particularly in relation to Olugbohun.',
                'category': 'Philosophy'
            }
        ]
        
        for theme in themes:
            topic = models.Topic()
            topic.title = theme['title']
            topic.description = theme['description']
            topic.category = theme['category']
            db.session.add(topic)
        
        db.session.commit()
