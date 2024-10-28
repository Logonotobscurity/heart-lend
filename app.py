import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dialogue_system import CommunityDialogueSystem
import openai

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

@app.route('/api/start_dialogue', methods=['POST'])
async def start_dialogue():
    data = request.json
    initial_role = data.get('role')
    context = data.get('context')
    
    response = await dialogue_system.start_dialogue_thread(
        channel_id="web",
        initial_role=initial_role,
        context=context
    )
    
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
