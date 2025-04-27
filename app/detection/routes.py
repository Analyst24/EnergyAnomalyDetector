"""
Detection routes for the Energy Anomaly Detection System.
"""
import os
import time
import pandas as pd
import numpy as np
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Dataset, AnalysisResult, Anomaly
from app.detection.forms import DetectionForm
from models.isolation_forest import run_isolation_forest
from models.autoencoder import run_autoencoder
from models.kmeans import run_kmeans
from datetime import datetime

# Create blueprint
detection_bp = Blueprint('detection', __name__)

@detection_bp.route('/detection')
@login_required
def index():
    """Render the detection configuration page."""
    form = DetectionForm()
    
    # Get user's datasets for the dropdown
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    if not datasets:
        flash('You need to upload a dataset before running anomaly detection.', 'warning')
        return redirect(url_for('upload.index'))
    
    # Populate the dataset dropdown
    form.dataset_id.choices = [(d.id, d.name) for d in datasets]
    
    # Get recent analyses for the sidebar
    recent_analyses = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(
        AnalysisResult.created_at.desc()
    ).limit(5).all()
    
    # Add dataset names to recent analyses for display
    for analysis in recent_analyses:
        dataset = Dataset.query.get(analysis.dataset_id)
        if dataset:
            analysis.dataset_name = dataset.name
        else:
            analysis.dataset_name = "Unknown"
    
    return render_template(
        'detection/index.html',
        active_page='detection',
        form=form,
        recent_analyses=recent_analyses
    )

@detection_bp.route('/detection/new/<int:dataset_id>')
@login_required
def new(dataset_id):
    """Pre-fill the detection form with a specific dataset."""
    form = DetectionForm()
    
    # Get user's datasets for the dropdown
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    if not datasets:
        flash('You need to upload a dataset before running anomaly detection.', 'warning')
        return redirect(url_for('upload.index'))
    
    # Populate the dataset dropdown
    form.dataset_id.choices = [(d.id, d.name) for d in datasets]
    
    # Select the specified dataset
    form.dataset_id.data = dataset_id
    
    # Get default name from dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    form.name.data = f"Analysis of {dataset.name}"
    
    # Get recent analyses for the sidebar
    recent_analyses = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(
        AnalysisResult.created_at.desc()
    ).limit(5).all()
    
    # Add dataset names to recent analyses for display
    for analysis in recent_analyses:
        d = Dataset.query.get(analysis.dataset_id)
        if d:
            analysis.dataset_name = d.name
        else:
            analysis.dataset_name = "Unknown"
    
    return render_template(
        'detection/index.html',
        active_page='detection',
        form=form,
        recent_analyses=recent_analyses
    )

@detection_bp.route('/detection/run', methods=['POST'])
@login_required
def run_detection():
    """Run anomaly detection with the specified configuration."""
    form = DetectionForm()
    
    # Get user's datasets for validation
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    form.dataset_id.choices = [(d.id, d.name) for d in datasets]
    
    if form.validate_on_submit():
        # Get the selected dataset
        dataset_id = form.dataset_id.data
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
        
        try:
            # Load the dataset
            df = pd.read_csv(dataset.file_path)
            
            # Parse timestamp if available
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Select algorithm and parameters
            algorithm = form.algorithm.data
            parameters = {}
            
            # Track execution time
            start_time = time.time()
            
            if algorithm == 'isolation_forest':
                # Isolation Forest parameters
                parameters = {
                    'n_estimators': form.if_n_estimators.data,
                    'contamination': form.if_contamination.data
                }
                
                # Run Isolation Forest algorithm
                anomalies, scores = run_isolation_forest(df, parameters)
                
            elif algorithm == 'autoencoder':
                # AutoEncoder parameters
                parameters = {
                    'threshold_percentile': form.ae_threshold.data,
                    'components': form.ae_components.data
                }
                
                # Run AutoEncoder algorithm
                anomalies, scores = run_autoencoder(df, parameters)
                
            elif algorithm == 'kmeans':
                # K-Means parameters
                parameters = {
                    'n_clusters': form.km_clusters.data,
                    'threshold_percentile': form.km_threshold.data
                }
                
                # Run K-Means algorithm
                anomalies, scores = run_kmeans(df, parameters)
                
            else:
                flash('Invalid algorithm selected', 'danger')
                return redirect(url_for('detection.index'))
            
            # Calculate execution time
            execution_time = round(time.time() - start_time, 2)
            
            # Create analysis result record
            analysis_result = AnalysisResult(
                name=form.name.data,
                description=form.description.data,
                algorithm=algorithm,
                parameters=parameters,
                result_metrics={
                    'execution_time': execution_time,
                    'anomaly_count': len(anomalies),
                    'score_mean': float(np.mean(scores)) if len(scores) > 0 else 0,
                    'score_std': float(np.std(scores)) if len(scores) > 0 else 0
                },
                anomaly_count=len(anomalies),
                dataset_id=dataset.id,
                user_id=current_user.id
            )
            
            db.session.add(analysis_result)
            db.session.commit()
            
            # Create individual anomaly records
            for idx in anomalies:
                # Create a row with anomaly information
                row_data = df.iloc[idx].to_dict()
                
                # Convert timestamp to datetime if it exists
                timestamp = None
                if 'timestamp' in row_data:
                    if isinstance(row_data['timestamp'], pd.Timestamp):
                        timestamp = row_data['timestamp'].to_pydatetime()
                    else:
                        try:
                            timestamp = pd.to_datetime(row_data['timestamp']).to_pydatetime()
                        except:
                            timestamp = None
                
                # Create feature values dict, excluding timestamp
                feature_values = {k: float(v) if isinstance(v, (int, float, np.number)) else str(v) 
                                 for k, v in row_data.items() if k != 'timestamp'}
                
                # Create anomaly record
                anomaly = Anomaly(
                    timestamp=timestamp,
                    index=int(idx),
                    score=float(scores[idx]) if idx < len(scores) else 0.0,
                    feature_values=feature_values,
                    analysis_result_id=analysis_result.id
                )
                
                db.session.add(anomaly)
            
            db.session.commit()
            
            flash(f'Successfully detected {len(anomalies)} anomalies using {algorithm} in {execution_time} seconds.', 'success')
            
            # Redirect to the results page
            return redirect(url_for('results.view', id=analysis_result.id))
            
        except Exception as e:
            flash(f'Error running anomaly detection: {str(e)}', 'danger')
            return redirect(url_for('detection.index'))
    
    # If form validation failed
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('detection.index'))