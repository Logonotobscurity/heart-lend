from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from models import db
from visualization import ConversationVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

    # Configure database using environment variables
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # Register routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat')
    def chat():
        return render_template('chat.html')

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

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
