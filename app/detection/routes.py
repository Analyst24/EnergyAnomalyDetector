"""
Routes for anomaly detection algorithms.
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.detection import detection_bp
from app.detection.forms import (
    SelectAlgorithmForm, IsolationForestForm, AutoEncoderForm, 
    KMeansForm, DBSCANForm
)
from app.models import Dataset, AnalysisResult, Anomaly


def load_dataset(dataset_id):
    """Load dataset from file."""
    # Get dataset from database
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure user owns this dataset
    if dataset.user_id != current_user.id:
        flash('You do not have permission to access this dataset.', 'danger')
        return None, None
    
    # Load the dataset
    try:
        _, ext = os.path.splitext(dataset.filename)
        ext = ext.lower()
        
        if ext == '.csv':
            df = pd.read_csv(dataset.file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(dataset.file_path)
        elif ext == '.json':
            df = pd.read_json(dataset.file_path)
        elif ext == '.txt':
            df = pd.read_csv(dataset.file_path, sep=None, engine='python')
        else:
            flash(f'Unsupported file format: {ext}', 'danger')
            return None, None
        
        # Return the dataframe and dataset
        return df, dataset
    
    except Exception as e:
        flash(f'Error loading dataset: {str(e)}', 'danger')
        return None, None


def detect_anomalies_isolation_forest(df, params):
    """Detect anomalies using Isolation Forest algorithm."""
    from sklearn.ensemble import IsolationForest
    
    # Select features (numeric columns only)
    numeric_columns = df.select_dtypes(include=['number']).columns
    
    # Include only the target column if specified
    features = df[numeric_columns].copy()
    
    # Handle missing values
    features = features.fillna(features.mean())
    
    # Configure model parameters
    model = IsolationForest(
        n_estimators=params.get('n_estimators', 100),
        contamination=params.get('contamination', 0.1),
        max_samples=params.get('max_samples', 256) if params.get('max_samples') else 'auto',
        random_state=params.get('random_state', 42),
        n_jobs=-1
    )
    
    # Fit the model
    model.fit(features)
    
    # Get anomaly predictions (-1 for anomalies, 1 for normal)
    anomaly_predictions = model.predict(features)
    
    # Convert to binary labels (0 for normal, 1 for anomaly)
    anomaly_labels = np.where(anomaly_predictions == -1, 1, 0)
    
    # Get anomaly scores
    anomaly_scores = -model.decision_function(features)
    
    # Create a dataframe with results
    result_df = df.copy()
    result_df['anomaly'] = anomaly_labels
    result_df['anomaly_score'] = anomaly_scores
    
    return result_df, anomaly_labels, anomaly_scores


def detect_anomalies_autoencoder(df, params):
    """Detect anomalies using Autoencoder algorithm."""
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        from sklearn.preprocessing import MinMaxScaler
    except ImportError:
        flash("TensorFlow not installed. Cannot use Autoencoder detection.", "danger")
        return None, None, None
    
    # Select features (numeric columns only)
    numeric_columns = df.select_dtypes(include=['number']).columns
    features = df[numeric_columns].copy()
    
    # Handle missing values
    features = features.fillna(features.mean())
    
    # Normalize the data
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Get parameters
    encoding_dim = params.get('encoding_dim', 8)
    epochs = params.get('epochs', 50)
    batch_size = params.get('batch_size', 32)
    threshold_percentile = params.get('threshold_percentile', 95)
    
    # Create and compile the autoencoder model
    input_dim = X_scaled.shape[1]
    model = Sequential([
        # Encoder
        Dense(input_dim, activation='relu', input_shape=(input_dim,)),
        Dense(encoding_dim * 2, activation='relu'),
        Dense(encoding_dim, activation='relu'),
        
        # Decoder
        Dense(encoding_dim * 2, activation='relu'),
        Dense(input_dim, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='mse')
    
    # Train the model
    model.fit(
        X_scaled, X_scaled,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        verbose=0
    )
    
    # Predict and calculate reconstruction error
    reconstructions = model.predict(X_scaled)
    reconstruction_errors = np.mean(np.square(X_scaled - reconstructions), axis=1)
    
    # Set a threshold for anomaly detection
    threshold = np.percentile(reconstruction_errors, threshold_percentile)
    anomaly_labels = np.where(reconstruction_errors > threshold, 1, 0)
    
    # Create a dataframe with results
    result_df = df.copy()
    result_df['anomaly'] = anomaly_labels
    result_df['anomaly_score'] = reconstruction_errors
    
    return result_df, anomaly_labels, reconstruction_errors


def detect_anomalies_kmeans(df, params):
    """Detect anomalies using K-Means algorithm."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    # Select features (numeric columns only)
    numeric_columns = df.select_dtypes(include=['number']).columns
    features = df[numeric_columns].copy()
    
    # Handle missing values
    features = features.fillna(features.mean())
    
    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Get parameters
    n_clusters = params.get('n_clusters', 8)
    distance_threshold = params.get('distance_threshold', 2.0)
    random_state = params.get('random_state', 42)
    
    # Train the model
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # Calculate distance from each point to its cluster center
    distances = np.zeros(X_scaled.shape[0])
    for i in range(X_scaled.shape[0]):
        cluster_center = kmeans.cluster_centers_[cluster_labels[i]]
        distances[i] = np.linalg.norm(X_scaled[i] - cluster_center)
    
    # Flag anomalies based on distance threshold
    anomaly_labels = np.where(distances > distance_threshold, 1, 0)
    
    # Create a dataframe with results
    result_df = df.copy()
    result_df['anomaly'] = anomaly_labels
    result_df['anomaly_score'] = distances
    result_df['cluster'] = cluster_labels
    
    return result_df, anomaly_labels, distances


def detect_anomalies_dbscan(df, params):
    """Detect anomalies using DBSCAN algorithm."""
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    
    # Select features (numeric columns only)
    numeric_columns = df.select_dtypes(include=['number']).columns
    features = df[numeric_columns].copy()
    
    # Handle missing values
    features = features.fillna(features.mean())
    
    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Get parameters
    eps = params.get('eps', 0.5)
    min_samples = params.get('min_samples', 5)
    
    # Apply DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = dbscan.fit_predict(X_scaled)
    
    # Points with label -1 are anomalies
    anomaly_labels = np.where(cluster_labels == -1, 1, 0)
    
    # Create anomaly scores based on distance to nearest core point
    # (This is a simplified approach using the cluster labels)
    anomaly_scores = np.ones(X_scaled.shape[0])
    for i in range(X_scaled.shape[0]):
        if cluster_labels[i] != -1:
            # Normal point - score is 0
            anomaly_scores[i] = 0
    
    # Create a dataframe with results
    result_df = df.copy()
    result_df['anomaly'] = anomaly_labels
    result_df['anomaly_score'] = anomaly_scores
    result_df['cluster'] = cluster_labels
    
    return result_df, anomaly_labels, anomaly_scores


def save_analysis_results(result_df, dataset, algorithm, params, target_column):
    """Save analysis results to database."""
    # Create AnalysisResult record
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    analysis_name = params.get('name', f"{algorithm.title()} Analysis {timestamp}")
    description = params.get('description', f"Anomaly detection using {algorithm}")
    
    # Count anomalies
    anomaly_count = int(result_df['anomaly'].sum())
    
    # Create JSON parameters
    algorithm_params = {
        'algorithm': algorithm,
        'target_column': target_column
    }
    
    # Add specific algorithm parameters
    if algorithm == 'isolation_forest':
        algorithm_params.update({
            'n_estimators': params.get('n_estimators', 100),
            'contamination': params.get('contamination', 0.1),
            'max_samples': params.get('max_samples', 256),
            'random_state': params.get('random_state', 42)
        })
    elif algorithm == 'autoencoder':
        algorithm_params.update({
            'encoding_dim': params.get('encoding_dim', 8),
            'epochs': params.get('epochs', 50),
            'batch_size': params.get('batch_size', 32),
            'threshold_percentile': params.get('threshold_percentile', 95)
        })
    elif algorithm == 'kmeans':
        algorithm_params.update({
            'n_clusters': params.get('n_clusters', 8),
            'distance_threshold': params.get('distance_threshold', 2.0),
            'random_state': params.get('random_state', 42)
        })
    elif algorithm == 'dbscan':
        algorithm_params.update({
            'eps': params.get('eps', 0.5),
            'min_samples': params.get('min_samples', 5)
        })
    
    # Create analysis result
    analysis_result = AnalysisResult(
        name=analysis_name,
        description=description,
        algorithm=algorithm,
        parameters=algorithm_params,
        anomaly_count=anomaly_count,
        dataset_id=dataset.id,
        user_id=current_user.id
    )
    
    # Add to database
    db.session.add(analysis_result)
    db.session.commit()
    
    # Create anomaly records for each detected anomaly
    anomalies = result_df[result_df['anomaly'] == 1]
    
    for _, row in anomalies.iterrows():
        # Create feature values JSON
        feature_values = {col: row[col] for col in result_df.columns if col not in ['anomaly', 'anomaly_score']}
        
        # Create timestamp if available
        timestamp = None
        for col in row.index:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    if isinstance(row[col], pd.Timestamp):
                        timestamp = row[col].to_pydatetime()
                    else:
                        timestamp = pd.to_datetime(row[col]).to_pydatetime()
                except:
                    pass
        
        # Create anomaly record
        anomaly = Anomaly(
            timestamp=timestamp,
            index=row.name,  # Use dataframe index
            score=row['anomaly_score'],
            feature_values=feature_values,
            analysis_result_id=analysis_result.id
        )
        
        db.session.add(anomaly)
    
    # Commit all anomalies
    db.session.commit()
    
    return analysis_result


@detection_bp.route('/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def index(dataset_id):
    """Anomaly detection configuration page."""
    # Load the dataset to ensure user has access
    df, dataset = load_dataset(dataset_id)
    
    if df is None:
        return redirect(url_for('dashboard.datasets'))
    
    form = SelectAlgorithmForm()
    
    if form.validate_on_submit():
        algorithm = form.algorithm.data
        
        # Store algorithm selection in session
        session['detection_algorithm'] = algorithm
        session['detection_dataset_id'] = dataset_id
        
        # Redirect to the algorithm's configuration page
        return redirect(url_for('detection.configure', dataset_id=dataset_id, algorithm=algorithm))
    
    # Dataset preview
    preview_data = df.head(5).to_dict('records')
    columns = df.columns.tolist()
    
    return render_template('detection/index.html',
                          title='Anomaly Detection',
                          form=form,
                          dataset=dataset,
                          preview_data=preview_data,
                          columns=columns)


@detection_bp.route('/<int:dataset_id>/configure/<algorithm>', methods=['GET', 'POST'])
@login_required
def configure(dataset_id, algorithm):
    """Configure anomaly detection algorithm."""
    # Verify algorithm is valid
    valid_algorithms = ['isolation_forest', 'autoencoder', 'kmeans', 'dbscan']
    if algorithm not in valid_algorithms:
        flash('Invalid algorithm selected.', 'danger')
        return redirect(url_for('detection.index', dataset_id=dataset_id))
    
    # Load the dataset
    df, dataset = load_dataset(dataset_id)
    
    if df is None:
        return redirect(url_for('dashboard.datasets'))
    
    # Get numerical columns for target selection
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    column_choices = [(col, col) for col in numeric_columns]
    
    # Select the appropriate form based on the algorithm
    if algorithm == 'isolation_forest':
        form = IsolationForestForm()
    elif algorithm == 'autoencoder':
        form = AutoEncoderForm()
    elif algorithm == 'kmeans':
        form = KMeansForm()
    elif algorithm == 'dbscan':
        form = DBSCANForm()
    
    # Update form choices
    form.target_column.choices = column_choices
    
    # Pre-populate with a default name
    if form.name.data is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        form.name.data = f"{algorithm.replace('_', ' ').title()} Analysis {timestamp}"
    
    if form.validate_on_submit():
        # Get form data as a dictionary for the detection function
        form_data = {
            'name': form.name.data,
            'description': form.description.data,
            'target_column': form.target_column.data
        }
        
        # Add algorithm-specific parameters
        if algorithm == 'isolation_forest':
            form_data.update({
                'n_estimators': form.n_estimators.data,
                'contamination': form.contamination.data,
                'max_samples': form.max_samples.data,
                'random_state': form.random_state.data
            })
        elif algorithm == 'autoencoder':
            form_data.update({
                'encoding_dim': form.encoding_dim.data,
                'epochs': form.epochs.data,
                'batch_size': form.batch_size.data,
                'threshold_percentile': form.threshold_percentile.data
            })
        elif algorithm == 'kmeans':
            form_data.update({
                'n_clusters': form.n_clusters.data,
                'distance_threshold': form.distance_threshold.data,
                'random_state': form.random_state.data
            })
        elif algorithm == 'dbscan':
            form_data.update({
                'eps': form.eps.data,
                'min_samples': form.min_samples.data
            })
        
        # Run the detection algorithm
        try:
            if algorithm == 'isolation_forest':
                result_df, anomaly_labels, anomaly_scores = detect_anomalies_isolation_forest(df, form_data)
            elif algorithm == 'autoencoder':
                result_df, anomaly_labels, anomaly_scores = detect_anomalies_autoencoder(df, form_data)
            elif algorithm == 'kmeans':
                result_df, anomaly_labels, anomaly_scores = detect_anomalies_kmeans(df, form_data)
            elif algorithm == 'dbscan':
                result_df, anomaly_labels, anomaly_scores = detect_anomalies_dbscan(df, form_data)
            
            if result_df is None:
                flash('Error running detection algorithm.', 'danger')
                return redirect(url_for('detection.configure', dataset_id=dataset_id, algorithm=algorithm))
            
            # Save results to database
            analysis_result = save_analysis_results(
                result_df, dataset, algorithm, form_data, form.target_column.data
            )
            
            flash('Anomaly detection completed successfully!', 'success')
            return redirect(url_for('results.view', analysis_id=analysis_result.id))
        
        except Exception as e:
            flash(f'Error running detection algorithm: {str(e)}', 'danger')
            return redirect(url_for('detection.configure', dataset_id=dataset_id, algorithm=algorithm))
    
    # Dataset preview
    preview_data = df.head(5).to_dict('records')
    
    return render_template('detection/configure.html',
                          title=f'Configure {algorithm.replace("_", " ").title()}',
                          form=form,
                          dataset=dataset,
                          algorithm=algorithm,
                          algorithm_name=algorithm.replace('_', ' ').title(),
                          preview_data=preview_data)