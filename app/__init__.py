"""
Energy Anomaly Detection System - Flask Application
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(test_config=None):
    """
    Factory function to create the Flask application instance
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(os.getcwd(), "energy_anomaly_detection.db")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Flask extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

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
    
    from app.code_snippets import code_snippets as code_snippets_blueprint
    app.register_blueprint(code_snippets_blueprint)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Import models to ensure they're registered with SQLAlchemy
        from app.models import User, Dataset, DetectionResult, Anomaly, SystemSettings
        
        # Initialize database with default values if needed
        from app.utils.init_db import initialize_database
        initialize_database()

    return app