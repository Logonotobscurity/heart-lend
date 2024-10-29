from flask import Flask
from flask_cors import CORS
import os
import logging
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path
import yaml
from dotenv import load_dotenv
from models import db
from routes import create_api_blueprint
from dialogue_system import CommunityDialogueSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Application configuration container"""
    SECRET_KEY: str
    DATABASE_URL: str
    OPENAI_API_KEY: str
    DEBUG: bool = False
    TESTING: bool = False

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'default_secret_key'),
            DATABASE_URL=os.getenv('DATABASE_URL'),
            OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
            DEBUG=os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true'),
            TESTING=os.getenv('FLASK_TESTING', '0').lower() in ('1', 'true')
        )

def create_app(config: AppConfig = None) -> Flask:
    """Application factory function"""
    try:
        # Initialize Flask app
        app = Flask(__name__)

        # Load configuration
        if config is None:
            config = AppConfig.from_env()

        # Basic configuration
        app.config['SECRET_KEY'] = config.SECRET_KEY
        app.config['DEBUG'] = config.DEBUG
        app.config['TESTING'] = config.TESTING
        app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "pool_recycle": 300,
            "pool_pre_ping": True
        }

        # Initialize CORS
        CORS(app)

        # Initialize database
        db.init_app(app)

        # Initialize dialogue system
        dialogue_system = CommunityDialogueSystem(config.OPENAI_API_KEY)

        # Register blueprints
        api_blueprint = create_api_blueprint(dialogue_system)
        app.register_blueprint(api_blueprint)  # Remove url_prefix to serve routes at root

        # Create database tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")

        return app

    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Create and configure application
        config = AppConfig.from_env()
        app = create_app(config)

        # Run application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=config.DEBUG
        )

    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        raise
