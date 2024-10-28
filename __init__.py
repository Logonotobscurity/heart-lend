from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy with no settings yet
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = "default_secret_key"  # You should use a proper secret key in production
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/postgres"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Import routes after app is created to avoid circular imports
        from . import routes
        from . import models
        
        # Create database tables
        db.create_all()
        
        return app
