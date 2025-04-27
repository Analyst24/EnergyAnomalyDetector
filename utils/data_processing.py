"""
Data processing utilities for the Energy Anomaly Detection System.
"""
import pandas as pd
import numpy as np
import os
import io
import csv
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Union, Any

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

def detect_csv_format(file_path: str) -> Dict[str, Any]:
    """
    Detect the format of an energy-related CSV file.
    
    Parameters:
        file_path (str): Path to the CSV file
        
    Returns:
        dict: Dictionary containing format information
    """
    try:
        # Read first few lines to detect format
        with open(file_path, 'r', encoding='utf-8') as f:
            sample_lines = [f.readline() for _ in range(10)]
        
        # Detect delimiter
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(''.join(sample_lines))
        delimiter = dialect.delimiter
        
        # Try to read the file with pandas to detect columns
        df_sample = pd.read_csv(file_path, nrows=5, delimiter=delimiter)
        
        # Analyze columns
        columns = df_sample.columns.tolist()
        
        # Detect timestamp column
        timestamp_col = None
        for col in columns:
            # Look for common timestamp column names
            if col.lower() in ['timestamp', 'time', 'date', 'datetime', 'time_stamp']:
                timestamp_col = col
                break
        
        # If no obvious timestamp column, try to detect based on content
        if timestamp_col is None:
            for col in columns:
                # Try to convert to datetime
                try:
                    pd.to_datetime(df_sample[col])
                    timestamp_col = col
                    break
                except:
                    continue
        
        # Detect energy consumption column
        consumption_col = None
        for col in columns:
            # Look for common energy consumption column names
            if any(keyword in col.lower() for keyword in ['consumption', 'energy', 'power', 'kwh', 'kw', 'usage']):
                consumption_col = col
                break
        
        # If no obvious consumption column, look for numeric columns that aren't timestamps
        if consumption_col is None:
            for col in columns:
                if col != timestamp_col and pd.api.types.is_numeric_dtype(df_sample[col]):
                    consumption_col = col
                    break
        
        # Detect other relevant columns
        temperature_col = next((col for col in columns if any(keyword in col.lower() 
                               for keyword in ['temperature', 'temp', 'celsius', 'fahrenheit'])), None)
        
        humidity_col = next((col for col in columns if any(keyword in col.lower() 
                            for keyword in ['humidity', 'rh', 'moisture'])), None)
        
        occupancy_col = next((col for col in columns if any(keyword in col.lower() 
                             for keyword in ['occupancy', 'occupied', 'presence', 'people'])), None)
        
        return {
            'delimiter': delimiter,
            'columns': columns,
            'timestamp_column': timestamp_col,
            'consumption_column': consumption_col,
            'temperature_column': temperature_col,
            'humidity_column': humidity_col,
            'occupancy_column': occupancy_col,
            'has_header': True  # Assuming all CSV files have headers
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'delimiter': ',',
            'columns': [],
            'timestamp_column': None,
            'consumption_column': None,
            'temperature_column': None,
            'humidity_column': None,
            'occupancy_column': None,
            'has_header': True
        }

def read_energy_csv(file_path: str, format_info: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Read an energy-related CSV file and convert it to a standardized format.
    
    Parameters:
        file_path (str): Path to the CSV file
        format_info (dict, optional): Format information from detect_csv_format
        
    Returns:
        tuple: (DataFrame with standardized columns, Format information dictionary)
    """
    try:
        # If format info wasn't provided, detect it
        if format_info is None:
            format_info = detect_csv_format(file_path)
            
        # If an error occurred during format detection
        if 'error' in format_info and not format_info['columns']:
            raise ValueError(f"Failed to detect CSV format: {format_info['error']}")
            
        # Read the CSV file
        df = pd.read_csv(file_path, delimiter=format_info['delimiter'])
        
        # Create a standardized DataFrame
        standardized_df = pd.DataFrame()
        
        # Process timestamp column
        if format_info['timestamp_column']:
            try:
                standardized_df['timestamp'] = pd.to_datetime(df[format_info['timestamp_column']])
            except Exception as e:
                raise ValueError(f"Failed to convert timestamp column: {str(e)}")
        else:
            # If no timestamp column, create an index-based one
            standardized_df['timestamp'] = pd.date_range(
                start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                periods=len(df),
                freq='H'
            )
            format_info['timestamp_column'] = 'Generated timestamp'
            
        # Process consumption column
        if format_info['consumption_column']:
            try:
                standardized_df['consumption'] = pd.to_numeric(df[format_info['consumption_column']])
            except Exception as e:
                raise ValueError(f"Failed to convert consumption column: {str(e)}")
        else:
            raise ValueError("No energy consumption column detected in the file")
            
        # Process optional columns
        if format_info['temperature_column']:
            standardized_df['temperature'] = pd.to_numeric(df[format_info['temperature_column']], errors='coerce')
            
        if format_info['humidity_column']:
            standardized_df['humidity'] = pd.to_numeric(df[format_info['humidity_column']], errors='coerce')
            
        if format_info['occupancy_column']:
            standardized_df['occupancy'] = pd.to_numeric(df[format_info['occupancy_column']], errors='coerce')
            
        return standardized_df, format_info
        
    except Exception as e:
        # Return an empty DataFrame and the error
        empty_df = pd.DataFrame(columns=['timestamp', 'consumption'])
        return empty_df, {'error': str(e)}

def list_energy_csv_files(directory: str) -> List[Dict[str, str]]:
    """
    List all CSV files in a directory that might contain energy-related data.
    
    Parameters:
        directory (str): Directory path to search
        
    Returns:
        list: List of dictionaries with file information
    """
    result = []
    
    try:
        for filename in os.listdir(directory):
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(directory, filename)
                
                # Get basic file info
                file_info = {
                    'filename': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Try to detect if it's an energy-related CSV
                try:
                    format_info = detect_csv_format(file_path)
                    
                    # If we found consumption and timestamp columns, it's likely energy data
                    if format_info['consumption_column'] and format_info['timestamp_column']:
                        file_info['is_energy_data'] = True
                        file_info['format_info'] = format_info
                    else:
                        file_info['is_energy_data'] = False
                        
                except Exception:
                    file_info['is_energy_data'] = False
                
                result.append(file_info)
    
    except Exception as e:
        # Return with error information
        return [{'error': str(e)}]
    
    return result

def save_processed_data(data: pd.DataFrame, file_path: str) -> bool:
    """
    Save processed data to a CSV file.
    
    Parameters:
        data (DataFrame): The data to save
        file_path (str): Path where to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the data
        data.to_csv(file_path, index=False)
        return True
    except Exception:
        return False
