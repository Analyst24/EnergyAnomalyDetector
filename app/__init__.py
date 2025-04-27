"""
Energy Anomaly Detection System - Flask Application
"""
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app(test_config=None):
    """
    Factory function to create the Flask application instance
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Set default configuration
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-for-energy-anomaly-detection'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///energy_anomaly_detection.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50 MB max upload
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Override config with test config if passed
    if test_config:
        app.config.update(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import User
    
    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.code_snippets import code_snippets as code_snippets_blueprint
    app.register_blueprint(code_snippets_blueprint)
    
    # These will be implemented as needed
    from app.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    from app.upload import upload as upload_blueprint
    app.register_blueprint(upload_blueprint)
    
    from app.detection import detection as detection_blueprint
    app.register_blueprint(detection_blueprint)
    
    from app.results import results as results_blueprint
    app.register_blueprint(results_blueprint)
    
    from app.insights import insights as insights_blueprint
    app.register_blueprint(insights_blueprint)
    
    from app.recommendations import recommendations as recommendations_blueprint
    app.register_blueprint(recommendations_blueprint)
    
    from app.settings import settings as settings_blueprint
    app.register_blueprint(settings_blueprint)
    
    @app.context_processor
    def utility_processor():
        """Make utility functions available to templates"""
        return dict(
            is_active=lambda endpoint: 'active' if request.endpoint and request.endpoint.startswith(endpoint) else ''
        )
    
    return app