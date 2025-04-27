"""
Run script for the Flask version of the Energy Anomaly Detection System
"""
from app import create_app
from app.models import User
from database.connection import init_db
from database.db_utils import create_demo_data

app = create_app()

# Initialize database with app context
with app.app_context():
    init_db()
    
    # Create demo data for testing
    try:
        create_demo_data(app.db.session)
    except Exception as e:
        app.logger.warning(f"Error creating demo data: {e}")
        app.logger.info("Demo data may already exist, continuing...")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)