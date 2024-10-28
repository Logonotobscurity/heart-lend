from flask import Flask
import os
import logging
from models import db
import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

    # Initialize routes
    routes.init_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
