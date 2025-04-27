"""
Energy Anomaly Detection System - Database Models
"""
from datetime import datetime
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120))
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='User')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    datasets = db.relationship('Dataset', backref='owner', lazy='dynamic')
    detection_results = db.relationship('DetectionResult', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'Admin'

class Dataset(db.Model):
    """Model for uploaded datasets"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    row_count = db.Column(db.Integer)
    column_count = db.Column(db.Integer)
    time_period = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    _metadata = db.Column('metadata', db.Text)
    
    # Relationships
    detection_results = db.relationship('DetectionResult', backref='dataset', lazy='dynamic')
    
    @property
    def metadata(self):
        if self._metadata:
            return json.loads(self._metadata)
        return {}
    
    @metadata.setter
    def metadata(self, value):
        self._metadata = json.dumps(value)
    
    def __repr__(self):
        return f'<Dataset {self.name}>'

class DetectionResult(db.Model):
    """Model for anomaly detection results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)
    _parameters = db.Column('parameters', db.Text)
    execution_time = db.Column(db.Float)  # in seconds
    anomaly_count = db.Column(db.Integer)
    threshold = db.Column(db.Float)
    result_file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    anomalies = db.relationship('Anomaly', backref='detection_result', lazy='dynamic')
    
    @property
    def parameters(self):
        if self._parameters:
            return json.loads(self._parameters)
        return {}
    
    @parameters.setter
    def parameters(self, value):
        self._parameters = json.dumps(value)
    
    def __repr__(self):
        return f'<DetectionResult {self.id}: {self.algorithm}>'

class Anomaly(db.Model):
    """Model for detected anomalies"""
    id = db.Column(db.Integer, primary_key=True)
    detection_result_id = db.Column(db.Integer, db.ForeignKey('detection_result.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
    score = db.Column(db.Float)  # Anomaly score
    _features = db.Column('features', db.Text)
    is_confirmed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def features(self):
        if self._features:
            return json.loads(self._features)
        return {}
    
    @features.setter
    def features(self, value):
        self._features = json.dumps(value)
    
    def __repr__(self):
        return f'<Anomaly {self.id}: {self.timestamp}>'

class SystemSettings(db.Model):
    """Model for system-wide settings"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'