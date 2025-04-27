"""
Initialize the database for the Energy Anomaly Detection System.
"""
import logging
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal, init_db
from database.models import User, Dataset, DetectionResult, Anomaly, SystemSettings
from database.crud import create_user, get_user_by_username
from database.db_utils import create_demo_data

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize the database and create initial data.
    """
    try:
        # Create all tables
        init_db()
        logger.info("Database tables created successfully")
        
        # Create default users if needed
        create_default_users()
        
        # Create demo data
        db = SessionLocal()
        create_demo_data(db)
        db.close()
        
        logger.info("Database initialization completed successfully")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return False

def create_default_users():
    """
    Create default admin and demo users if they don't exist.
    """
    try:
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = get_user_by_username(db, "admin")
        if not admin_user:
            # Create admin user
            create_user(
                db=db,
                username="admin",
                email="admin@example.com",
                password="admin123",  # In production, use a secure password
                full_name="System Administrator",
                role="Admin"
            )
            logger.info("Created default admin user")
        
        # Check if demo user exists
        demo_user = get_user_by_username(db, "demo")
        if not demo_user:
            # Create demo user
            create_user(
                db=db,
                username="demo",
                email="demo@example.com",
                password="demo123",
                full_name="Demo User",
                role="User"
            )
            logger.info("Created default demo user")
            
        db.close()
    except SQLAlchemyError as e:
        logger.error(f"Error creating default users: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating default users: {e}")
        raise

def migrate_session_users():
    """
    Migrate users from session state to the database.
    """
    if 'users' not in st.session_state:
        logger.info("No session users to migrate")
        return 0
    
    migrated_count = 0
    db = SessionLocal()
    
    try:
        # Get users from session state
        session_users = st.session_state.users
        
        for username, user_data in session_users.items():
            # Check if user already exists in DB
            existing_user = get_user_by_username(db, username)
            
            if not existing_user:
                # Create user in database
                create_user(
                    db=db,
                    username=username,
                    email=user_data.get('email', f"{username}@example.com"),
                    password=user_data.get('password', 'changeme'),
                    full_name=user_data.get('name', username),
                    role=user_data.get('role', 'User')
                )
                migrated_count += 1
                logger.info(f"Migrated user '{username}' from session to database")
                
        logger.info(f"Migrated {migrated_count} users from session to database")
        return migrated_count
    except SQLAlchemyError as e:
        logger.error(f"Error migrating users to database: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # When run as a script, initialize the database
    success = initialize_database()
    if success:
        print("Database initialization completed successfully")
    else:
        print("Database initialization failed")