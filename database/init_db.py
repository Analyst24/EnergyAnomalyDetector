"""
Initialize the database for the Energy Anomaly Detection System.
"""
import logging
from sqlalchemy.exc import SQLAlchemyError
from database.connection import init_db
from database.crud import create_user

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize the database schema and create initial data.
    """
    try:
        # Create all tables
        init_db()
        logger.info("Database tables created successfully")
        
        # You can add initialization of default data here
        # For example:
        # create_default_admin_user()
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        return False


def create_default_admin_user(db_session):
    """
    Create a default admin user if no users exist.
    """
    try:
        # Check if any users exist
        from database.models import User
        user_count = db_session.query(User).count()
        
        if user_count == 0:
            # Create default admin user
            admin_user = create_user(
                db=db_session,
                username="admin",
                email="admin@example.com",
                password="admin123",  # In production, use a secure password
                full_name="System Administrator",
                role="Admin"
            )
            logger.info(f"Created default admin user: {admin_user.username}")
        else:
            logger.info("Users already exist, skipping default admin creation")
    except SQLAlchemyError as e:
        logger.error(f"Error creating default admin user: {e}")
        raise


if __name__ == "__main__":
    # When run as a script, initialize the database
    success = initialize_database()
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")