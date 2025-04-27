"""
Dashboard routes for the Energy Anomaly Detection System.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app import db
from app.models import Dataset, AnalysisResult, Anomaly
from datetime import datetime, timedelta
import pandas as pd
import json

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Render the dashboard page."""
    # Get query parameters for filtering
    selected_dataset = request.args.get('dataset', type=int)
    timeframe = request.args.get('timeframe', 'month')
    algorithm = request.args.get('algorithm')
    
    # Get all user datasets for the dropdown
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    
    # Base query for analysis results
    query = AnalysisResult.query.filter_by(user_id=current_user.id)
    
    # Apply filters if provided
    if selected_dataset:
        query = query.filter_by(dataset_id=selected_dataset)
    
    if algorithm:
        query = query.filter_by(algorithm=algorithm)
    
    # Apply timeframe filter
    if timeframe == 'day':
        since = datetime.now() - timedelta(days=1)
        query = query.filter(AnalysisResult.created_at >= since)
    elif timeframe == 'week':
        since = datetime.now() - timedelta(weeks=1)
        query = query.filter(AnalysisResult.created_at >= since)
    elif timeframe == 'month':
        since = datetime.now() - timedelta(days=30)
        query = query.filter(AnalysisResult.created_at >= since)
    elif timeframe == 'year':
        since = datetime.now() - timedelta(days=365)
        query = query.filter(AnalysisResult.created_at >= since)
    
    # Get analysis results
    analysis_results = query.all()
    
    # Calculate summary metrics
    total_consumption = 0
    anomaly_count = 0
    time_period = "N/A"
    
    if analysis_results:
        # Sum up anomalies
        for result in analysis_results:
            anomaly_count += result.anomaly_count
        
        # Time period
        if timeframe == 'day':
            time_period = "Last 24 Hours"
        elif timeframe == 'week':
            time_period = "Last Week"
        elif timeframe == 'month':
            time_period = "Last 30 Days"
        elif timeframe == 'year':
            time_period = "Last Year"
        else:
            time_period = "All Time"
        
        # Get total consumption from datasets if available
        # This would require accessing the actual data files and summing consumption values
        # For now, we'll use a placeholder
        total_consumption = 15000.0  # Example value
    
    # Calculate percentage if we have anomalies and total consumption
    anomaly_percentage = 0.0
    if anomaly_count > 0 and total_consumption > 0:
        # This is a simplification - in a real system we would calculate what percentage of
        # energy consumption is attributed to anomalies
        anomaly_percentage = round((anomaly_count / 1000) * 100, 1)
    
    # Get recent anomalies for the table
    recent_anomalies = Anomaly.query.join(AnalysisResult).filter(
        AnalysisResult.user_id == current_user.id
    ).order_by(Anomaly.created_at.desc()).limit(10).all()
    
    # Prepare anomalies for display
    for anomaly in recent_anomalies:
        # Add the algorithm name and dataset name for display
        anomaly.algorithm = anomaly.analysis_result.algorithm
        anomaly.dataset_name = anomaly.analysis_result.dataset.name
    
    # Render the dashboard template with data
    return render_template(
        'dashboard/index.html',
        active_page='dashboard',
        datasets=datasets,
        selected_dataset=selected_dataset,
        timeframe=timeframe,
        algorithm=algorithm,
        total_consumption=total_consumption,
        anomaly_count=anomaly_count,
        anomaly_percentage=anomaly_percentage,
        time_period=time_period,
        recent_anomalies=recent_anomalies
    )