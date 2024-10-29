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
            DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///app.db'),
            OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
            DEBUG=os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true'),
            TESTING=os.getenv('FLASK_TESTING', '0').lower() in ('1', 'true')
        )

class DatabaseConfig:
    """Database configuration settings"""
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {
            "SQLALCHEMY_DATABASE_URI": AppConfig.from_env().DATABASE_URL,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30
            }
        }

def configure_app(app: Flask, config: AppConfig) -> None:
    """Configure Flask application"""
    # Basic configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    app.config['TESTING'] = config.TESTING

    # Database configuration
    app.config.update(DatabaseConfig.get_config())

    # Additional security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

def initialize_extensions(app: Flask) -> None:
    """Initialize Flask extensions"""
    # Initialize database
    db.init_app(app)

    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('CORS_ORIGINS', '*').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

def create_app(config: AppConfig = None) -> Flask:
    """Application factory function"""
    try:
        # Initialize Flask app
        app = Flask(__name__)

        # Load configuration
        if config is None:
            config = AppConfig.from_env()

        # Configure application
        configure_app(app, config)

        # Initialize extensions
        initialize_extensions(app)

        # Verify required environment variables
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")

        # Initialize dialogue system
        dialogue_system = CommunityDialogueSystem(config.OPENAI_API_KEY)

        # Register blueprints
        api_blueprint = create_api_blueprint(dialogue_system)
        app.register_blueprint(api_blueprint, url_prefix='/api')

        # Create database tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")

        return app

    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise

def init_database(app: Flask) -> None:
    """Initialize database with retry mechanism"""
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
                logger.info("Database tables created successfully")
                break
        except Exception as e:
            retry_count += 1
            logger.error(f"Database initialization attempt {retry_count} failed: {str(e)}")
            if retry_count == max_retries:
                raise
            time.sleep(2 ** retry_count)  # Exponential backoff

if __name__ == "__main__":
    try:
        # Create and configure application
        config = AppConfig.from_env()
        app = create_app(config)

        # Initialize database with retry mechanism
        init_database(app)

        # Run application
        app.run(
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            debug=config.DEBUG
        )

    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        raise
