import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dialogue_system import CommunityDialogueSystem
import openai
import random
import json

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
    openai_api_key=os.environ.get("OPENAI_API_KEY")
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
    topics = query.order_by(Topic.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'category': t.category
    } for t in topics])

@app.route('/api/topics/suggest', methods=['POST'])
def suggest_topic():
    from models import Topic
    current_context = request.json.get('context', '')
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
        suggestions = json.loads(response.choices[0].message.content)
        new_topics = []
        
        for suggestion in suggestions.get('topics', []):
            if all(key in suggestion for key in ['title', 'description', 'category']):
                topic = Topic(
                    title=suggestion['title'],
                    description=suggestion['description'],
                    category=suggestion['category'],
                    suggested_by_ai=True
                )
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
            topic['id'] = Topic.query.filter_by(
                title=topic['title'],
                description=topic['description']
            ).first().id
        
        return jsonify({"status": "success", "topics": new_topics})
    
    except json.JSONDecodeError as e:
        return jsonify({"status": "error", "message": "Invalid response format"}), 500
    except Exception as e:
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
        
        # Generate initial response using the dialogue system with depth level 1
        response = dialogue_system.response_generator.generate_response(initial_role, context, 1)
        thread_id = str(random.randint(1000000, 9999999))
        
        if topic_id:
            from models import ChatThread
            thread = ChatThread(
                thread_id=thread_id,
                context=context,
                topic_id=topic_id
            )
            db.session.add(thread)
            db.session.commit()
        
        return jsonify({
            "status": "success",
            "thread_id": thread_id,
            "response": response
        })
        
    except Exception as e:
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
        
        from models import Message
        # Calculate depth level based on message count
        depth_level = min(1 + Message.query.filter_by(thread_id=thread_id).count() // 2, 3)
        
        # Generate response using the dialogue system
        previous_messages = Message.query.filter_by(thread_id=thread_id, role='assistant').all()
        previous_responses = [msg.content for msg in previous_messages]
        
        response = dialogue_system.response_generator.generate_layered_response(
            previous_responses,
            role,
            user_input,
            depth_level
        )
        
        # Save the message
        new_message = Message(thread_id=thread_id, role=role, content=response)
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "thread_id": thread_id,
            "response": response
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

with app.app_context():
    import models
    db.create_all()
    
    # Add some initial topics if none exist
    if models.Topic.query.count() == 0:
        initial_topics = [
            {
                'title': 'Consciousness and AI',
                'description': 'Exploring the nature of consciousness in artificial intelligence systems.',
                'category': 'Philosophy'
            },
            {
                'title': 'Digital Spirituality',
                'description': 'The intersection of technology and spiritual practices in the modern world.',
                'category': 'Spirituality'
            },
            {
                'title': 'Algorithmic Rituals',
                'description': 'Understanding how algorithms can mirror or enhance traditional spiritual rituals.',
                'category': 'Technology'
            }
        ]
        for topic in initial_topics:
            db.session.add(models.Topic(**topic))
        db.session.commit()
