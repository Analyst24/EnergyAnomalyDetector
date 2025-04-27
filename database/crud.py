"""
CRUD operations for the Energy Anomaly Detection System.
"""
import hashlib
import logging
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional, Union

from database.models import User, Dataset, DetectionResult, Anomaly, SystemSettings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User operations
def hash_password(password: str) -> str:
    """
    Hash a password for storage.
    
    Note: In a production system, use a proper password hashing library like bcrypt.
    
    Args:
        password: The plaintext password
        
    Returns:
        str: The hashed password
    """
    # Simple password hashing for demonstration
    # In a real system, use a proper library
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        stored_hash: The stored hash
        password: The plaintext password to check
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return stored_hash == hash_password(password)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User: The user object, or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.
    
    Args:
        db: Database session
        username: Username to search for
        
    Returns:
        User: The user object, or None if not found
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        db: Database session
        email: Email to search for
        
    Returns:
        User: The user object, or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, email: str, password: str, full_name: str = None, role: str = "User") -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        username: Username
        email: Email address
        password: Password (will be hashed)
        full_name: Full name (optional)
        role: Role (default: "User")
        
    Returns:
        User: The created user
    """
    hashed_password = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """
    Update a user's information.
    
    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update
        
    Returns:
        User: The updated user, or None if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Handle password separately if provided
    if 'password' in kwargs:
        kwargs['hashed_password'] = hash_password(kwargs.pop('password'))
    
    for key, value in kwargs.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating user: {e}")
        raise


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    try:
        db.delete(db_user)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user: {e}")
        raise


# Dataset operations
def get_dataset_by_id(db: Session, dataset_id: int) -> Optional[Dataset]:
    """
    Get a dataset by ID.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        Dataset: The dataset object, or None if not found
    """
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def get_datasets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Dataset]:
    """
    Get datasets owned by a user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Dataset]: List of datasets
    """
    return db.query(Dataset).filter(Dataset.user_id == user_id).offset(skip).limit(limit).all()


def create_dataset(db: Session, user_id: int, name: str, description: str = None, 
                  file_path: str = None, row_count: int = None, column_count: int = None,
                  time_period: str = None, metadata: Dict = None) -> Dataset:
    """
    Create a new dataset.
    
    Args:
        db: Database session
        user_id: User ID
        name: Dataset name
        description: Dataset description
        file_path: Path to the dataset file
        row_count: Number of rows in the dataset
        column_count: Number of columns in the dataset
        time_period: Time period covered by the dataset
        metadata: Additional metadata
        
    Returns:
        Dataset: The created dataset
    """
    db_dataset = Dataset(
        user_id=user_id,
        name=name,
        description=description,
        file_path=file_path,
        row_count=row_count,
        column_count=column_count,
        time_period=time_period,
        metadata=metadata or {}
    )
    try:
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        return db_dataset
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating dataset: {e}")
        raise


def update_dataset(db: Session, dataset_id: int, **kwargs) -> Optional[Dataset]:
    """
    Update a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        **kwargs: Fields to update
        
    Returns:
        Dataset: The updated dataset, or None if not found
    """
    db_dataset = get_dataset_by_id(db, dataset_id)
    if not db_dataset:
        return None
    
    for key, value in kwargs.items():
        if hasattr(db_dataset, key):
            setattr(db_dataset, key, value)
    
    try:
        db.commit()
        db.refresh(db_dataset)
        return db_dataset
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating dataset: {e}")
        raise


def delete_dataset(db: Session, dataset_id: int) -> bool:
    """
    Delete a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    db_dataset = get_dataset_by_id(db, dataset_id)
    if not db_dataset:
        return False
    
    try:
        db.delete(db_dataset)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting dataset: {e}")
        raise


# Detection result operations
def get_detection_result_by_id(db: Session, result_id: int) -> Optional[DetectionResult]:
    """
    Get a detection result by ID.
    
    Args:
        db: Database session
        result_id: Result ID
        
    Returns:
        DetectionResult: The result object, or None if not found
    """
    return db.query(DetectionResult).filter(DetectionResult.id == result_id).first()


def get_detection_results_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DetectionResult]:
    """
    Get detection results for a user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[DetectionResult]: List of detection results
    """
    return db.query(DetectionResult).filter(DetectionResult.user_id == user_id).offset(skip).limit(limit).all()


def get_detection_results_by_dataset(db: Session, dataset_id: int, skip: int = 0, limit: int = 100) -> List[DetectionResult]:
    """
    Get detection results for a dataset.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[DetectionResult]: List of detection results
    """
    return db.query(DetectionResult).filter(DetectionResult.dataset_id == dataset_id).offset(skip).limit(limit).all()


def create_detection_result(db: Session, user_id: int, dataset_id: int, algorithm: str,
                           parameters: Dict = None, execution_time: float = None,
                           anomaly_count: int = None, threshold: float = None,
                           result_file_path: str = None, notes: str = None) -> DetectionResult:
    """
    Create a new detection result.
    
    Args:
        db: Database session
        user_id: User ID
        dataset_id: Dataset ID
        algorithm: Algorithm name
        parameters: Algorithm parameters
        execution_time: Execution time in seconds
        anomaly_count: Number of anomalies detected
        threshold: Threshold used for detection
        result_file_path: Path to result file
        notes: Notes about the result
        
    Returns:
        DetectionResult: The created detection result
    """
    db_result = DetectionResult(
        user_id=user_id,
        dataset_id=dataset_id,
        algorithm=algorithm,
        parameters=parameters or {},
        execution_time=execution_time,
        anomaly_count=anomaly_count,
        threshold=threshold,
        result_file_path=result_file_path,
        notes=notes
    )
    try:
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating detection result: {e}")
        raise


# Anomaly operations
def get_anomaly_by_id(db: Session, anomaly_id: int) -> Optional[Anomaly]:
    """
    Get an anomaly by ID.
    
    Args:
        db: Database session
        anomaly_id: Anomaly ID
        
    Returns:
        Anomaly: The anomaly object, or None if not found
    """
    return db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()


def get_anomalies_by_result(db: Session, result_id: int, skip: int = 0, limit: int = 100) -> List[Anomaly]:
    """
    Get anomalies for a detection result.
    
    Args:
        db: Database session
        result_id: Result ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Anomaly]: List of anomalies
    """
    return db.query(Anomaly).filter(Anomaly.detection_result_id == result_id).offset(skip).limit(limit).all()


def create_anomaly(db: Session, detection_result_id: int, timestamp: datetime.datetime,
                  value: float, score: float, features: Dict = None,
                  is_confirmed: bool = False, notes: str = None) -> Anomaly:
    """
    Create a new anomaly record.
    
    Args:
        db: Database session
        detection_result_id: Detection result ID
        timestamp: Timestamp of the anomaly
        value: Anomalous value
        score: Anomaly score
        features: Features used for detection
        is_confirmed: Whether the anomaly is confirmed by a user
        notes: Notes about the anomaly
        
    Returns:
        Anomaly: The created anomaly
    """
    db_anomaly = Anomaly(
        detection_result_id=detection_result_id,
        timestamp=timestamp,
        value=value,
        score=score,
        features=features or {},
        is_confirmed=is_confirmed,
        notes=notes
    )
    try:
        db.add(db_anomaly)
        db.commit()
        db.refresh(db_anomaly)
        return db_anomaly
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating anomaly: {e}")
        raise


def confirm_anomaly(db: Session, anomaly_id: int, notes: str = None) -> Optional[Anomaly]:
    """
    Confirm an anomaly.
    
    Args:
        db: Database session
        anomaly_id: Anomaly ID
        notes: Optional notes about the confirmation
        
    Returns:
        Anomaly: The updated anomaly, or None if not found
    """
    db_anomaly = get_anomaly_by_id(db, anomaly_id)
    if not db_anomaly:
        return None
    
    db_anomaly.is_confirmed = True
    if notes:
        db_anomaly.notes = notes
    
    try:
        db.commit()
        db.refresh(db_anomaly)
        return db_anomaly
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error confirming anomaly: {e}")
        raise


# System settings operations
def get_setting(db: Session, key: str) -> Optional[str]:
    """
    Get a system setting value.
    
    Args:
        db: Database session
        key: Setting key
        
    Returns:
        str: Setting value, or None if not found
    """
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()
    return setting.setting_value if setting else None


def set_setting(db: Session, key: str, value: str, description: str = None) -> SystemSettings:
    """
    Set a system setting.
    
    Args:
        db: Database session
        key: Setting key
        value: Setting value
        description: Setting description
        
    Returns:
        SystemSettings: The created or updated setting
    """
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()
    
    if setting:
        setting.setting_value = value
        if description:
            setting.description = description
    else:
        setting = SystemSettings(
            setting_key=key,
            setting_value=value,
            description=description
        )
        db.add(setting)
    
    try:
        db.commit()
        db.refresh(setting)
        return setting
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error setting system setting: {e}")
        raise