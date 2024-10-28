# Add this import at the top with other imports
from visualization import ConversationVisualizer

# Add this new route after other routes
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
