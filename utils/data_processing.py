"""
Data processing utilities for the Energy Anomaly Detection System.
"""
import pandas as pd
import numpy as np
from datetime import datetime

def validate_dataset(data):
    """
    Validate that the uploaded dataset has the required columns and structure.
    
    Parameters:
        data (DataFrame): The dataset to validate
    
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is a string
    """
    # Check if dataframe is empty
    if data.empty:
        return False, "The uploaded file is empty."
    
    # Check for required columns
    required_columns = ['timestamp', 'consumption']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return False, f"Missing required column(s): {', '.join(missing_columns)}"
    
    # Check data types and formatting
    try:
        # Attempt to convert timestamp column to datetime
        pd.to_datetime(data['timestamp'])
    except Exception as e:
        return False, f"Error parsing timestamp column: {str(e)}"
    
    # Check consumption column
    if not pd.api.types.is_numeric_dtype(data['consumption']):
        try:
            # Attempt to convert to numeric
            data['consumption'] = pd.to_numeric(data['consumption'])
        except Exception as e:
            return False, f"Consumption column must contain numeric values: {str(e)}"
    
    # Optional columns validation
    optional_columns = ['temperature', 'humidity', 'occupancy']
    for col in optional_columns:
        if col in data.columns and not pd.api.types.is_numeric_dtype(data[col]):
            try:
                # Attempt to convert to numeric
                data[col] = pd.to_numeric(data[col])
            except Exception as e:
                return False, f"Column '{col}' must contain numeric values: {str(e)}"
    
    # Check for duplicates in timestamp
    if data['timestamp'].duplicated().any():
        return True, "Warning: Duplicate timestamps found. Data will be aggregated."
    
    return True, "Dataset validation successful."

def preprocess_data(data):
    """
    Preprocess the dataset for anomaly detection.
    
    Parameters:
        data (DataFrame): The raw dataset
    
    Returns:
        DataFrame: The processed dataset
    """
    # Create a copy to avoid modifying the original
    processed_data = data.copy()
    
    # Convert timestamp to datetime
    processed_data['timestamp'] = pd.to_datetime(processed_data['timestamp'])
    
    # Sort by timestamp
    processed_data = processed_data.sort_values('timestamp')
    
    # Handle duplicates by aggregating
    if processed_data['timestamp'].duplicated().any():
        processed_data = processed_data.groupby('timestamp').agg({
            'consumption': 'mean',
            'temperature': 'mean' if 'temperature' in processed_data.columns else None,
            'humidity': 'mean' if 'humidity' in processed_data.columns else None,
            'occupancy': 'mean' if 'occupancy' in processed_data.columns else None
        }).reset_index()
    
    # Handle missing values
    numeric_columns = processed_data.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        # Fill missing values with the median
        processed_data[col] = processed_data[col].fillna(processed_data[col].median())
    
    # Add additional time-based features
    processed_data['hour'] = processed_data['timestamp'].dt.hour
    processed_data['day_of_week'] = processed_data['timestamp'].dt.dayofweek
    processed_data['is_weekend'] = processed_data['day_of_week'] >= 5
    processed_data['is_business_hours'] = ((processed_data['hour'] >= 8) & 
                                          (processed_data['hour'] <= 18) & 
                                          (~processed_data['is_weekend']))
    
    # Add indicator for missing values that were filled
    for col in numeric_columns:
        missing_indicator = f"{col}_was_missing"
        processed_data[missing_indicator] = data[col].isna().astype(int)
    
    # Set index to timestamp for time series analysis
    processed_data = processed_data.set_index('timestamp').reset_index()
    
    # Initialize is_anomaly column to 0 (false)
    processed_data['is_anomaly'] = 0
    
    return processed_data

def split_train_test(data, test_size=0.2):
    """
    Split the dataset into training and testing sets.
    
    Parameters:
        data (DataFrame): The processed dataset
        test_size (float): The proportion of data to use for testing
    
    Returns:
        tuple: (train_data, test_data)
    """
    # For time series data, we use the most recent data as test set
    n = len(data)
    train_size = int(n * (1 - test_size))
    
    train_data = data.iloc[:train_size].copy()
    test_data = data.iloc[train_size:].copy()
    
    return train_data, test_data

def normalize_features(train_data, test_data=None, columns=None):
    """
    Normalize feature columns to have zero mean and unit variance.
    
    Parameters:
        train_data (DataFrame): Training data
        test_data (DataFrame): Test data (optional)
        columns (list): Columns to normalize (if None, all numeric columns)
    
    Returns:
        tuple: (normalized_train, normalized_test, scaler)
    """
    from sklearn.preprocessing import StandardScaler
    
    # Clone the data
    train_normalized = train_data.copy()
    
    # If no columns specified, use all numeric columns except 'is_anomaly'
    if columns is None:
        columns = train_normalized.select_dtypes(include=[np.number]).columns.tolist()
        if 'is_anomaly' in columns:
            columns.remove('is_anomaly')
    
    # Initialize the scaler
    scaler = StandardScaler()
    
    # Fit and transform training data
    train_normalized[columns] = scaler.fit_transform(train_normalized[columns])
    
    # Transform test data if provided
    test_normalized = None
    if test_data is not None:
        test_normalized = test_data.copy()
        test_normalized[columns] = scaler.transform(test_normalized[columns])
    
    return train_normalized, test_normalized, scaler

def prepare_features(data, feature_columns=None):
    """
    Prepare the feature matrix for machine learning algorithms.
    
    Parameters:
        data (DataFrame): The dataset
        feature_columns (list): List of columns to use as features
    
    Returns:
        ndarray: Feature matrix X
    """
    if feature_columns is None:
        # Use all numeric columns except is_anomaly
        feature_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        if 'is_anomaly' in feature_columns:
            feature_columns.remove('is_anomaly')
    
    # Extract features
    X = data[feature_columns].values
    
    return X
