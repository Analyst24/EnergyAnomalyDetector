"""
K-Means clustering anomaly detection algorithm for the Energy Anomaly Detection System.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist

def run_kmeans(df, params=None):
    """
    Run K-Means clustering algorithm on the dataset.
    
    Args:
        df (pandas.DataFrame): The dataset to analyze
        params (dict, optional): Algorithm parameters
        
    Returns:
        tuple: (anomaly_indices, anomaly_scores)
    """
    # Set default parameters if not provided
    if params is None:
        params = {
            'n_clusters': 5,
            'threshold_percentile': 95
        }
    
    n_clusters = params.get('n_clusters', 5)
    threshold_percentile = params.get('threshold_percentile', 95)
    
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
    
    # Ensure we don't have more clusters than data points
    n_clusters = min(n_clusters, len(X_scaled) - 1)
    
    # If we have very few data points, reduce to a simple approach
    if n_clusters < 2:
        n_clusters = 2
    
    # Train the model
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )
    kmeans.fit(X_scaled)
    
    # Get cluster assignments
    clusters = kmeans.predict(X_scaled)
    
    # Calculate distance to assigned cluster center
    distances = np.zeros(len(X_scaled))
    for i in range(len(X_scaled)):
        cluster_idx = clusters[i]
        distances[i] = np.linalg.norm(X_scaled[i] - kmeans.cluster_centers_[cluster_idx])
    
    # Determine threshold for anomalies
    threshold = np.percentile(distances, threshold_percentile)
    
    # Identify anomalies
    anomaly_mask = distances > threshold
    anomaly_indices = np.where(anomaly_mask)[0]
    
    return anomaly_indices, distances