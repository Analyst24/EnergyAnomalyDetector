"""
Energy Anomaly Detection System - Flask Application Package
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize database
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_for_development_only'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///energy_anomaly_detection.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16 MB max upload size
    )
    
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.upload import upload_bp
    app.register_blueprint(upload_bp)
    
    from app.detection import detection_bp
    app.register_blueprint(detection_bp)
    
    from app.results import results_bp
    app.register_blueprint(results_bp)
    
    from app.insights import insights_bp
    app.register_blueprint(insights_bp)
    
    from app.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)
    
    from app.settings import settings_bp
    app.register_blueprint(settings_bp)
    
    from app.code_snippets import code_snippets_bp
    app.register_blueprint(code_snippets_bp)
    
    # Import models to register them with SQLAlchemy
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login user loader."""
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app