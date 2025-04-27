"""
Utility functions for database operations.
"""
import logging
import pandas as pd
import numpy as np
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.connection import get_db_session, SessionLocal
from database.models import User, Dataset, DetectionResult, Anomaly
from database.crud import create_user, create_dataset, create_detection_result, create_anomaly

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_session_users_to_db():
    """
    Migrate users from session state to the database.
    """
    import streamlit as st
    
    if 'users' not in st.session_state:
        return
    
    db = SessionLocal()
    try:
        # Get users from session state
        session_users = st.session_state.users
        
        for username, user_data in session_users.items():
            # Check if user already exists in DB
            from database.crud import get_user_by_username
            existing_user = get_user_by_username(db, username)
            
            if not existing_user:
                # Create user in database
                create_user(
                    db=db,
                    username=username,
                    email=user_data.get('email', f"{username}@example.com"),
                    password=user_data.get('password', 'default123'),
                    full_name=user_data.get('name', username),
                    role=user_data.get('role', 'User')
                )
                logger.info(f"Migrated user '{username}' from session to database")
            else:
                logger.info(f"User '{username}' already exists in database")
    except SQLAlchemyError as e:
        logger.error(f"Error migrating users to database: {e}")
        raise
    finally:
        db.close()


def create_demo_data(db: Session):
    """
    Create demonstration data for the Energy Anomaly Detection System.
    
    Args:
        db: Database session
    """
    try:
        # Create a demo user if not exists
        from database.crud import get_user_by_username
        demo_user = get_user_by_username(db, "demo")
        
        if not demo_user:
            demo_user = create_user(
                db=db,
                username="demo",
                email="demo@example.com",
                password="demo123",
                full_name="Demo User",
                role="User"
            )
            logger.info("Created demo user")
        
        # Check if demo dataset already exists
        existing_datasets = db.query(Dataset).filter(
            Dataset.user_id == demo_user.id,
            Dataset.name == "Demo Energy Consumption"
        ).count()
        
        if existing_datasets > 0:
            logger.info("Demo data already exists, skipping creation")
            return
        
        # Create a demo dataset
        demo_dataset = create_dataset(
            db=db,
            user_id=demo_user.id,
            name="Demo Energy Consumption",
            description="Sample energy consumption data for demonstration",
            row_count=1000,
            column_count=5,
            time_period="Jan 2023 - Feb 2023",
            metadata={
                "source": "system-generated",
                "units": "kWh",
                "building_type": "Office Building",
                "location": "New York, NY"
            }
        )
        
        # Create a demo detection result
        demo_result = create_detection_result(
            db=db,
            user_id=demo_user.id,
            dataset_id=demo_dataset.id,
            algorithm="Isolation Forest",
            parameters={
                "contamination": 0.05,
                "n_estimators": 100,
                "max_samples": "auto"
            },
            execution_time=2.45,
            anomaly_count=12,
            threshold=0.65,
            notes="Demo detection result using Isolation Forest"
        )
        
        # Create some sample anomalies
        base_date = datetime.datetime(2023, 1, 1)
        
        # Create a few anomalies
        for i in range(12):
            # Create anomaly at random dates
            anomaly_date = base_date + datetime.timedelta(days=i*5, hours=i*2)
            anomaly_value = 100 + np.random.normal(0, 20) * 3  # Higher anomaly values
            
            create_anomaly(
                db=db,
                detection_result_id=demo_result.id,
                timestamp=anomaly_date,
                value=anomaly_value,
                score=0.75 + np.random.random() * 0.2,  # High anomaly scores
                features={
                    "temperature": 22 + np.random.normal(0, 3),
                    "occupancy": int(np.random.randint(5, 50)),
                    "is_weekend": anomaly_date.weekday() >= 5
                },
                is_confirmed=i < 5,  # Some confirmed, some not
                notes=f"Sample anomaly {i+1}" if i < 3 else None
            )
        
        logger.info(f"Created demo dataset with {demo_result.anomaly_count} anomalies")
        
    except SQLAlchemyError as e:
        logger.error(f"Error creating demo data: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating demo data: {e}")
        db.rollback()
        raise