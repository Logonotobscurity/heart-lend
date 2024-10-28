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
async def suggest_topic():
    from models import Topic
    current_context = request.json.get('context', '')
    
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
    
    try:
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
            # Validate required fields
            if all(key in suggestion for key in ['title', 'description', 'category']):
                topic = Topic(
                    title=suggestion['title'],
                    description=suggestion['description'],
                    category=suggestion['category'],
                    suggested_by_ai=True
                )
                db.session.add(topic)
                new_topics.append({
                    'title': suggestion['title'],
                    'description': suggestion['description'],
                    'category': suggestion['category']
                })
        
        db.session.commit()
        return jsonify({"status": "success", "topics": new_topics})
    
    except json.JSONDecodeError as e:
        return jsonify({"status": "error", "message": "Invalid response format"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/start_dialogue', methods=['POST'])
async def start_dialogue():
    data = request.json
    initial_role = data.get('role')
    context = data.get('context')
    topic_id = data.get('topic_id')
    
    response = await dialogue_system.start_dialogue_thread(
        channel_id="web",
        initial_role=initial_role,
        context=context
    )
    
    if topic_id:
        from models import ChatThread
        thread = ChatThread.query.filter_by(thread_id=response['thread_id']).first()
        if thread:
            thread.topic_id = topic_id
            db.session.commit()
    
    return jsonify(response)

@app.route('/api/continue_dialogue', methods=['POST'])
async def continue_dialogue():
    data = request.json
    thread_id = data.get('thread_id')
    role = data.get('role')
    user_input = data.get('message')
    
    response = await dialogue_system.continue_dialogue(
        channel_id="web",
        thread_ts=thread_id,
        responding_role=role,
        user_input=user_input
    )
    
    return jsonify(response)

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
