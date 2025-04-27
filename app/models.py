"""
Energy Anomaly Detection System - Database Models
"""
import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User account model for authentication and user management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    datasets = db.relationship('Dataset', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        """Set the user password (hashed)."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """String representation of the user."""
        return f'<User {self.username}>'


class Dataset(db.Model):
    """Dataset model for storing user data files."""
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False, unique=True)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    file_type = db.Column(db.String(50), nullable=False)
    row_count = db.Column(db.Integer, nullable=True)
    column_count = db.Column(db.Integer, nullable=True)
    has_timestamps = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    analysis_results = db.relationship('AnalysisResult', backref='dataset', lazy='dynamic')
    
    def __repr__(self):
        """String representation of the dataset."""
        return f'<Dataset {self.name}>'


class AnalysisResult(db.Model):
    """Model for storing anomaly detection results."""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    algorithm = db.Column(db.String(100), nullable=False)
    parameters = db.Column(db.JSON, nullable=True)  # Algorithm parameters in JSON format
    result_metrics = db.Column(db.JSON, nullable=True)  # Results/metrics in JSON format
    anomaly_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Keys
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='analysis_results')
    anomalies = db.relationship('Anomaly', backref='analysis_result', lazy='dynamic')
    
    def __repr__(self):
        """String representation of the analysis result."""
        return f'<AnalysisResult {self.name} ({self.algorithm})>'


class Anomaly(db.Model):
    """Model for storing individual anomalies detected in the data."""
    __tablename__ = 'anomalies'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=True)  # Timestamp of the anomaly if available
    index = db.Column(db.Integer, nullable=False)  # Data index of the anomaly
    score = db.Column(db.Float, nullable=False)  # Anomaly score
    feature_values = db.Column(db.JSON, nullable=True)  # Feature values at the anomaly point
    is_validated = db.Column(db.Boolean, default=False)  # User verified this anomaly
    is_true_anomaly = db.Column(db.Boolean, nullable=True)  # User feedback: true/false anomaly
    notes = db.Column(db.Text, nullable=True)  # User notes about this anomaly
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Keys
    analysis_result_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id'), nullable=False)
    
    def __repr__(self):
        """String representation of the anomaly."""
        return f'<Anomaly {self.id} (Score: {self.score})>'


class UserPreference(db.Model):
    """User preference settings model."""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), default='dark')  # UI theme preference
    dashboard_layout = db.Column(db.JSON, nullable=True)  # Dashboard widget layout
    default_algorithm = db.Column(db.String(100), nullable=True)  # Default anomaly detection algorithm
    default_params = db.Column(db.JSON, nullable=True)  # Default algorithm parameters
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', uselist=False))
    
    def __repr__(self):
        """String representation of the user preferences."""
        return f'<UserPreference for User ID: {self.user_id}>'