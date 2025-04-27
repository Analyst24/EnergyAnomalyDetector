"""
AutoEncoder anomaly detection algorithm for the Energy Anomaly Detection System.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
import logging

def run_autoencoder(df, params=None):
    """
    Run AutoEncoder algorithm on the dataset.
    
    Args:
        df (pandas.DataFrame): The dataset to analyze
        params (dict, optional): Algorithm parameters
        
    Returns:
        tuple: (anomaly_indices, anomaly_scores)
    """
    # Set default parameters if not provided
    if params is None:
        params = {
            'threshold_percentile': 95,
            'components': 2,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        }
    
    threshold_percentile = params.get('threshold_percentile', 95)
    components = params.get('components', 2)
    epochs = params.get('epochs', 50)
    batch_size = params.get('batch_size', 32)
    learning_rate = params.get('learning_rate', 0.001)
    
    # Extract features for anomaly detection
    feature_cols = []
    
    # Use consumption as a feature
    if 'consumption' in df.columns:
        feature_cols.append('consumption')
    
    # Use temperature as a feature if available
    if 'temperature' in df.columns:
        feature_cols.append('temperature')
    
    # Use humidity as a feature if available
    if 'humidity' in df.columns:
        feature_cols.append('humidity')
    
    # If we have timestamp, add time-based features
    if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        # Extract hour of day
        df['hour'] = df['timestamp'].dt.hour
        feature_cols.append('hour')
        
        # Extract day of week
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        feature_cols.append('day_of_week')
    
    # Ensure we have at least one feature
    if not feature_cols:
        # If no specific features, use all numeric columns
        feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Prepare features
    X = df[feature_cols].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Input dimension
    input_dim = X_scaled.shape[1]
    
    # Limit component dimension
    encoding_dim = min(components, input_dim)
    
    # Build the model
    try:
        # Suppress TensorFlow info and warning messages
        tf.get_logger().setLevel('ERROR')
        logging.getLogger('tensorflow').setLevel(logging.ERROR)
        
        # Build the autoencoder model
        model = Sequential([
            Input(shape=(input_dim,)),
            Dense(input_dim, activation='relu'),
            Dense(encoding_dim, activation='relu'),
            Dense(input_dim, activation='sigmoid')
        ])
        
        # Compile the model
        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mean_squared_error')
        
        # Train the model
        model.fit(
            X_scaled, X_scaled,
            epochs=epochs,
            batch_size=batch_size,
            shuffle=True,
            verbose=0
        )
        
        # Get reconstruction error
        reconstructions = model.predict(X_scaled, verbose=0)
        mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
        
        # Determine threshold for anomalies
        threshold = np.percentile(mse, threshold_percentile)
        
        # Identify anomalies
        anomaly_mask = mse > threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        return anomaly_indices, mse
        
    except Exception as e:
        # In case of TF errors, fall back to a simpler approach
        logging.error(f"AutoEncoder error: {str(e)}")
        
        # Fall back to a simpler approach
        from sklearn.decomposition import PCA
        
        # Use PCA as a fallback
        pca = PCA(n_components=min(encoding_dim, input_dim))
        X_pca = pca.fit_transform(X_scaled)
        X_reconstructed = pca.inverse_transform(X_pca)
        
        # Calculate reconstruction error
        mse = np.mean(np.power(X_scaled - X_reconstructed, 2), axis=1)
        
        # Determine threshold for anomalies
        threshold = np.percentile(mse, threshold_percentile)
        
        # Identify anomalies
        anomaly_mask = mse > threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        return anomaly_indices, mse