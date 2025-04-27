"""
Energy Anomaly Detection System - Flask Application
"""
import os
from app import create_app, db
from app.models import User, Dataset, AnalysisResult, Anomaly, UserPreference
from database.connection import init_db
from database.db_utils import create_demo_data

app = create_app()

# Initialize database with app context
with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("Database tables created successfully")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user")
        
        # Check if demo user exists
        demo = User.query.filter_by(username='demo').first()
        if not demo:
            # Create demo user
            demo = User(
                username='demo',
                email='demo@example.com',
                full_name='Demo User'
            )
            demo.set_password('demo123')
            db.session.add(demo)
            db.session.commit()
            print("Created default demo user")
        
        # Create demo data
        create_demo_data(db.session)
        print("Demo data created successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)