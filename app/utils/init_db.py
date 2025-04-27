"""
Initialize the database for the Energy Anomaly Detection System.
"""
import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Dataset, DetectionResult, Anomaly, SystemSettings

logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize the database schema and create initial data.
    """
    try:
        # Create default admin user if no users exist
        create_default_admin_user()
        
        # Create demo data if needed
        create_demo_data()
        
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def create_default_admin_user():
    """
    Create a default admin user if no users exist.
    """
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            full_name='System Administrator',
            role='Admin'
        )
        admin_user.set_password('admin123')
        
        demo_user = User(
            username='demo',
            email='demo@example.com',
            full_name='Demo User',
            role='User'
        )
        demo_user.set_password('demo123')
        
        db.session.add(admin_user)
        db.session.add(demo_user)
        db.session.commit()
        
        logger.info("Created default admin user")
        logger.info("Created default demo user")

def create_demo_data():
    """
    Create demonstration data for the Energy Anomaly Detection System.
    """
    # Check if demo data already exists
    if Dataset.query.count() > 0:
        logger.info("Demo data already exists, skipping creation")
        return
    
    try:
        # Get demo user
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            logger.error("Demo user not found, cannot create demo data")
            return
        
        # Create a demo dataset
        demo_dataset = Dataset(
            user_id=demo_user.id,
            name='Energy Consumption Demo Data',
            description='Hourly energy consumption data with simulated anomalies for demonstration purposes.',
            file_path='demo_energy_data.csv',
            row_count=24*30,  # 30 days of hourly data
            column_count=2,
            time_period='Last 30 Days',
            metadata={
                'columns': ['timestamp', 'consumption'],
                'units': 'kWh',
                'source': 'Simulated Data'
            }
        )
        db.session.add(demo_dataset)
        db.session.commit()
        
        # Create detection result using this dataset
        demo_result = DetectionResult(
            user_id=demo_user.id,
            dataset_id=demo_dataset.id,
            algorithm='Isolation Forest',
            parameters={
                'n_estimators': 100,
                'contamination': 0.05,
                'random_state': 42
            },
            execution_time=1.25,
            anomaly_count=12,
            threshold=0.2,
            notes='Automated anomaly detection using Isolation Forest algorithm.'
        )
        db.session.add(demo_result)
        db.session.commit()
        
        # Create anomalies
        base_time = datetime.now() - timedelta(days=30)
        anomaly_dates = [5, 8, 12, 16, 18, 19, 21, 22, 23, 24, 27, 29]  # Days with anomalies
        
        for day in anomaly_dates:
            # Create an anomaly record
            hour = np.random.randint(0, 24)
            anomaly = Anomaly(
                detection_result_id=demo_result.id,
                timestamp=base_time + timedelta(days=day, hours=hour),
                value=np.random.uniform(15, 25),  # Higher than normal consumption
                score=np.random.uniform(-0.8, -0.5),  # Anomaly score (negative for Isolation Forest)
                features={
                    'hour_of_day': hour,
                    'day_of_week': (base_time + timedelta(days=day)).weekday(),
                    'is_weekend': 1 if (base_time + timedelta(days=day)).weekday() >= 5 else 0
                },
                is_confirmed=np.random.choice([True, False], p=[0.3, 0.7])
            )
            db.session.add(anomaly)
        
        db.session.commit()
        logger.info(f"Created demo dataset with {len(anomaly_dates)} anomalies")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating demo data: {str(e)}")
        raise