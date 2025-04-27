"""
Database models for the Energy Anomaly Detection System.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """
    User model for authentication.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="User")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    datasets = relationship("Dataset", back_populates="user")
    detection_results = relationship("DetectionResult", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Dataset(Base):
    """
    Energy consumption dataset.
    """
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String(255))  # Path to stored CSV or similar
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    row_count = Column(Integer)
    column_count = Column(Integer)
    time_period = Column(String(100))  # e.g., "Jan 2023 - Mar 2023"
    metadata = Column(JSON)  # Store additional metadata as JSON
    
    # Relationships
    user = relationship("User", back_populates="datasets")
    detection_results = relationship("DetectionResult", back_populates="dataset")
    
    def __repr__(self):
        return f"<Dataset {self.name}>"


class DetectionResult(Base):
    """
    Anomaly detection results.
    """
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    algorithm = Column(String(50), nullable=False)  # e.g., "Isolation Forest", "Autoencoder"
    parameters = Column(JSON)  # Algorithm parameters as JSON
    execution_time = Column(Float)  # Time taken to run the algorithm (seconds)
    anomaly_count = Column(Integer)  # Number of anomalies detected
    threshold = Column(Float)  # Threshold used for anomaly detection
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    result_file_path = Column(String(255))  # Path to stored results
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="detection_results")
    dataset = relationship("Dataset", back_populates="detection_results")
    anomalies = relationship("Anomaly", back_populates="detection_result")
    
    def __repr__(self):
        return f"<DetectionResult {self.id} ({self.algorithm})>"


class Anomaly(Base):
    """
    Individual anomaly records.
    """
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_result_id = Column(Integer, ForeignKey("detection_results.id"))
    timestamp = Column(DateTime)
    value = Column(Float)  # The anomalous value
    score = Column(Float)  # Anomaly score
    features = Column(JSON)  # Features used for detection as JSON
    is_confirmed = Column(Boolean, default=False)  # User-confirmed anomaly
    notes = Column(Text)
    
    # Relationships
    detection_result = relationship("DetectionResult", back_populates="anomalies")
    
    def __repr__(self):
        return f"<Anomaly {self.id} at {self.timestamp}>"


class SystemSettings(Base):
    """
    System-wide settings.
    """
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSettings {self.setting_key}>"