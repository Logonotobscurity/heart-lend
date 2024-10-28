import os
import uuid
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
import logging
import jinja2
from dialogue_system import CommunityDialogueSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    try:
        return render_template('chat.html')
    except jinja2.exceptions.TemplateNotFound as e:
        logger.error(f"Template not found error: {str(e)}")
        return render_template('error.html', 
            error="We're experiencing technical difficulties. Please try again later."), 500
    except Exception as e:
        logger.error(f"Unexpected error in chat route: {str(e)}")
        return render_template('error.html', 
            error="An unexpected error occurred. Please try again later."), 500

@app.route('/api/start_dialogue', methods=['POST'])
def start_dialogue():
    try:
        from models import ChatThread, Message
        
        role = request.json.get('role')
        topic_id = request.json.get('topic_id')
        context = request.json.get('context')
        
        if not role or not context:
            return jsonify({
                "status": "error",
                "message": "Role and context are required"
            }), 400
        
        # Create new chat thread
        thread = ChatThread(
            thread_id=str(uuid.uuid4()),
            context=context,
            topic_id=topic_id
        )
        db.session.add(thread)
        db.session.commit()
        
        # Generate initial response
        dialogue_system = CommunityDialogueSystem(os.environ.get('OPENAI_API_KEY'))
        response = dialogue_system.generate_response(role, context)
        
        # Save message
        message = Message(
            thread_id=thread.id,
            role=role,
            content=response
        )
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "thread_id": thread.thread_id,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error in start_dialogue: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/topics', methods=['GET'])
def get_topics():
    try:
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
    except Exception as e:
        logger.error(f"Error fetching topics: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to fetch topics"}), 500

@app.route('/api/topics/suggest', methods=['POST'])
def suggest_topic():
    try:
        from models import Topic
        context = request.json.get('context')
        if not context:
            return jsonify({"status": "error", "message": "Context is required"}), 400

        # Create OpenAI client with API key from environment
        openai_client = openai.OpenAI()
        
        prompt = f"""Based on the conversation context: '{context}', suggest 3 related discussion topics.
        Each topic should be relevant to the themes of consciousness, AI, and Yoruba spiritual practices.
        For each topic include:
        - A clear, engaging title
        - A brief description explaining the topic
        - A category (Philosophy, Technology, Spirituality, Ethics, or Culture)
        
        Format your response as a JSON object exactly like this example:
        {{
            "topics": [
                {{
                    "title": "Digital Consciousness",
                    "description": "Exploring parallels between AI awareness and spiritual consciousness",
                    "category": "Philosophy"
                }}
            ]
        }}"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates discussion topics in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        if not response.choices or not response.choices[0].message:
            raise ValueError("No response from OpenAI")
            
        suggestions = response.choices[0].message.content
        if not suggestions:
            raise ValueError("Empty response from OpenAI")

        # Parse the JSON response
        import json
        topic_data = json.loads(suggestions)
        if not isinstance(topic_data, dict) or 'topics' not in topic_data:
            raise ValueError("Invalid response format")

        # Save suggested topics
        new_topics = []
        for suggestion in topic_data['topics']:
            if all(key in suggestion for key in ['title', 'description', 'category']):
                topic = Topic(
                    title=suggestion['title'],
                    description=suggestion['description'],
                    category=suggestion['category'],
                    suggested_by_ai=True
                )
                db.session.add(topic)
                new_topics.append({
                    'id': None,  # Will be updated after commit
                    'title': suggestion['title'],
                    'description': suggestion['description'],
                    'category': suggestion['category']
                })
        
        # Commit to database
        db.session.commit()
        
        # Update topic IDs
        for topic in new_topics:
            topic_obj = Topic.query.filter_by(
                title=topic['title'],
                description=topic['description']
            ).first()
            if topic_obj:
                topic['id'] = topic_obj.id

        return jsonify({"status": "success", "topics": new_topics})
        
    except ValueError as e:
        logger.error(f"Value error in topic suggestion: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error suggesting topics: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to suggest topics"}), 500

# Initialize database tables
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add initial topics if none exist
        from models import Topic
        if Topic.query.count() == 0:
            initial_topics = [
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
                }
            ]
            
            for topic_data in initial_topics:
                topic = Topic(**topic_data)
                db.session.add(topic)
            
            try:
                db.session.commit()
                logger.info("Successfully initialized database with initial topics")
            except Exception as e:
                logger.error(f"Error initializing database: {str(e)}")
                db.session.rollback()

# Initialize database on startup
init_db()
