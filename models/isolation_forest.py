"""
Isolation Forest anomaly detection algorithm for the Energy Anomaly Detection System.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def run_isolation_forest(df, params=None):
    """
    Run Isolation Forest algorithm on the dataset.
    
    Args:
        df (pandas.DataFrame): The dataset to analyze
        params (dict, optional): Algorithm parameters
        
    Returns:
        tuple: (anomaly_indices, anomaly_scores)
    """
    # Set default parameters if not provided
    if params is None:
        params = {
            'n_estimators': 100,
            'contamination': 0.05
        }
    
    n_estimators = params.get('n_estimators', 100)
    contamination = params.get('contamination', 0.05)
    
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
    if 'timestamp' in df.columns and isinstance(df['timestamp'].iloc[0], np.datetime64):
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
    
    # Train the model
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=42
    )
    model.fit(X_scaled)
    
    # Predict anomalies (-1 for anomaly, 1 for normal)
    predictions = model.predict(X_scaled)
    anomaly_mask = predictions == -1
    
    # Get decision function scores (negative for anomalies)
    scores = -model.decision_function(X_scaled)
    
    # Get indices of anomalies
    anomaly_indices = np.where(anomaly_mask)[0]
    
    return anomaly_indices, scores