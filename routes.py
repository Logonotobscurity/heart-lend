from flask import render_template, jsonify
from . import db, logger
from .visualization import ConversationVisualizer

def init_routes(app):
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
