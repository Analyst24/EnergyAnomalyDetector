"""
Database connection management for the Energy Anomaly Detection System.
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Always prefer SQLite for offline use
USE_SQLITE = True

if USE_SQLITE or not os.environ.get('DATABASE_URL'):
    # Use local SQLite database for offline mode
    DATABASE_URL = "sqlite:///./energy_anomaly_detection.db"
    logger.info("Using local SQLite database for offline mode")
else:
    # Use PostgreSQL if explicitly configured and available
    DATABASE_URL = os.environ.get('DATABASE_URL')
    logger.info("Using PostgreSQL database")

# Create engine
try:
    # For SQLite, we need to add check_same_thread=False for multiple threads access
    connect_args = {}
    if DATABASE_URL.startswith('sqlite'):
        connect_args = {"check_same_thread": False}
        
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection established successfully")
except SQLAlchemyError as e:
    logger.error(f"Error connecting to database: {e}")
    raise

def get_db_session():
    """
    Get a database session.
    
    Returns:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """
    Test the database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def init_db():
    """
    Initialize the database, creating all tables.
    """
    from database.models import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise