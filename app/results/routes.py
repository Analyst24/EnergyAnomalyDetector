"""
Results routes for the Energy Anomaly Detection System.
"""
import os
import pandas as pd
import json
import csv
from io import StringIO
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Dataset, AnalysisResult, Anomaly
from datetime import datetime, timedelta

# Create blueprint
results_bp = Blueprint('results', __name__)

@results_bp.route('/results')
@login_required
def index():
    """Render the results page."""
    # Get query parameters for filtering
    selected_dataset = request.args.get('dataset', type=int)
    selected_algorithm = request.args.get('algorithm')
    date_range = request.args.get('date_range')
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of results per page
    
    # Get all user datasets for the dropdown
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    
    # Base query for analysis results
    query = AnalysisResult.query.filter_by(user_id=current_user.id)
    
    # Apply filters if provided
    if selected_dataset:
        query = query.filter_by(dataset_id=selected_dataset)
    
    if selected_algorithm:
        query = query.filter_by(algorithm=selected_algorithm)
    
    # Apply date range filter
    if date_range:
        if date_range == 'today':
            since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(AnalysisResult.created_at >= since)
        elif date_range == 'yesterday':
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(AnalysisResult.created_at.between(yesterday_start, yesterday_end))
        elif date_range == '7days':
            since = datetime.now() - timedelta(days=7)
            query = query.filter(AnalysisResult.created_at >= since)
        elif date_range == '30days':
            since = datetime.now() - timedelta(days=30)
            query = query.filter(AnalysisResult.created_at >= since)
    
    # Sort by creation date, newest first
    query = query.order_by(AnalysisResult.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    analyses = pagination.items
    
    # Add dataset names to analysis results for display
    for analysis in analyses:
        dataset = Dataset.query.get(analysis.dataset_id)
        if dataset:
            analysis.dataset_name = dataset.name
        else:
            analysis.dataset_name = "Unknown"
        
        # Add execution time if available
        if analysis.result_metrics and 'execution_time' in analysis.result_metrics:
            analysis.execution_time = analysis.result_metrics['execution_time']
        else:
            analysis.execution_time = 'N/A'
    
    return render_template(
        'results/index.html',
        active_page='results',
        analyses=analyses,
        datasets=datasets,
        selected_dataset=selected_dataset,
        selected_algorithm=selected_algorithm,
        date_range=date_range,
        pagination=pagination
    )

@results_bp.route('/results/<int:id>')
@login_required
def view(id):
    """View a specific analysis result."""
    # Get the analysis
    analysis = AnalysisResult.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Add dataset name to analysis
    dataset = Dataset.query.get(analysis.dataset_id)
    if dataset:
        analysis.dataset_name = dataset.name
    else:
        analysis.dataset_name = "Unknown"
    
    # Get metrics if available
    metrics = None
    if analysis.result_metrics:
        metrics = {
            'precision': analysis.result_metrics.get('precision', 0),
            'recall': analysis.result_metrics.get('recall', 0),
            'f1_score': analysis.result_metrics.get('f1_score', 0),
            'auc': analysis.result_metrics.get('auc', 0),
            'execution_time': analysis.result_metrics.get('execution_time', 'N/A')
        }
    
    # Get anomalies with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of anomalies per page
    
    # Paginate anomalies
    pagination = Anomaly.query.filter_by(analysis_result_id=analysis.id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    anomalies = pagination.items
    
    # Process anomalies for display
    for anomaly in anomalies:
        # Extract key values for display
        if anomaly.feature_values:
            if 'consumption' in anomaly.feature_values:
                anomaly.value = anomaly.feature_values['consumption']
            else:
                # If consumption is not available, use the first value
                anomaly.value = next(iter(anomaly.feature_values.values()))
        else:
            anomaly.value = 'N/A'
    
    return render_template(
        'results/view.html',
        active_page='results',
        analysis=analysis,
        metrics=metrics,
        anomalies=anomalies,
        pagination=pagination
    )

@results_bp.route('/results/anomaly/<int:id>')
@login_required
def view_anomaly(id):
    """View a specific anomaly."""
    # Get the anomaly
    anomaly = Anomaly.query.filter_by(id=id).first_or_404()
    
    # Check if the user has access to this anomaly
    analysis = AnalysisResult.query.filter_by(id=anomaly.analysis_result_id, user_id=current_user.id).first_or_404()
    
    # Add dataset name to analysis
    dataset = Dataset.query.get(analysis.dataset_id)
    if dataset:
        analysis.dataset_name = dataset.name
    else:
        analysis.dataset_name = "Unknown"
    
    # Get the original data context if available
    context_data = None
    if dataset and os.path.exists(dataset.file_path):
        try:
            df = pd.read_csv(dataset.file_path)
            
            # Get the index of the anomaly in the original data
            anomaly_index = anomaly.index
            
            # Get a window of data around the anomaly
            start_idx = max(0, anomaly_index - 5)
            end_idx = min(len(df), anomaly_index + 6)
            
            context_data = df.iloc[start_idx:end_idx].to_dict('records')
            
            # Mark the anomaly row
            for i, row in enumerate(context_data):
                if start_idx + i == anomaly_index:
                    row['_is_anomaly'] = True
                else:
                    row['_is_anomaly'] = False
        except Exception as e:
            flash(f'Error loading context data: {str(e)}', 'warning')
    
    return render_template(
        'results/anomaly.html',
        active_page='results',
        anomaly=anomaly,
        analysis=analysis,
        context_data=context_data
    )

@results_bp.route('/results/validate/<int:id>', methods=['POST'])
@login_required
def validate_anomaly(id):
    """Validate an anomaly."""
    # Get the anomaly
    anomaly = Anomaly.query.filter_by(id=id).first_or_404()
    
    # Check if the user has access to this anomaly
    analysis = AnalysisResult.query.filter_by(id=anomaly.analysis_result_id, user_id=current_user.id).first_or_404()
    
    # Get validation status
    is_true_anomaly = request.form.get('is_true_anomaly') == 'true'
    
    # Update anomaly
    anomaly.is_validated = True
    anomaly.is_true_anomaly = is_true_anomaly
    
    # Save to database
    db.session.commit()
    
    # Return to the previous page
    flash('Anomaly validation saved', 'success')
    return redirect(url_for('results.view', id=analysis.id))

@results_bp.route('/results/download/<int:id>')
@login_required
def download_csv(id):
    """Download analysis results as CSV."""
    # Get the analysis
    analysis = AnalysisResult.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Get dataset name
    dataset = Dataset.query.get(analysis.dataset_id)
    dataset_name = dataset.name if dataset else "Unknown"
    
    # Get all anomalies for this analysis
    anomalies = Anomaly.query.filter_by(analysis_result_id=analysis.id).all()
    
    # Create CSV file in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['index', 'timestamp', 'score']
    
    # Add feature columns
    feature_columns = set()
    for anomaly in anomalies:
        if anomaly.feature_values:
            feature_columns.update(anomaly.feature_values.keys())
    
    header.extend(sorted(feature_columns))
    writer.writerow(header)
    
    # Write data rows
    for anomaly in anomalies:
        row = [anomaly.index]
        
        # Add timestamp
        if anomaly.timestamp:
            row.append(anomaly.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            row.append('')
        
        # Add score
        row.append(anomaly.score)
        
        # Add feature values
        for col in sorted(feature_columns):
            if anomaly.feature_values and col in anomaly.feature_values:
                row.append(anomaly.feature_values[col])
            else:
                row.append('')
        
        writer.writerow(row)
    
    # Prepare the response
    output.seek(0)
    
    # Generate filename
    filename = f"anomalies_{analysis.algorithm}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )

@results_bp.route('/results/data/<int:id>')
@login_required
def get_chart_data(id):
    """Get data for chart visualization."""
    # Get the analysis
    analysis = AnalysisResult.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Get dataset
    dataset = Dataset.query.get(analysis.dataset_id)
    if not dataset or not os.path.exists(dataset.file_path):
        return jsonify({'error': 'Dataset not found'}), 404
    
    try:
        # Load dataset
        df = pd.read_csv(dataset.file_path)
        
        # Parse timestamp if available
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get anomalies
        anomalies = Anomaly.query.filter_by(analysis_result_id=analysis.id).all()
        anomaly_indices = [a.index for a in anomalies]
        
        # Prepare data for chart
        data = {
            'timestamps': [],
            'consumption': [],
            'anomalies': []
        }
        
        # Extract timestamps and consumption
        if 'timestamp' in df.columns and 'consumption' in df.columns:
            data['timestamps'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
            data['consumption'] = df['consumption'].tolist()
            
            # Mark anomalies
            data['anomalies'] = [{'x': data['timestamps'][idx], 'y': data['consumption'][idx]} 
                               for idx in anomaly_indices if idx < len(df)]
            
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@results_bp.route('/results/delete/<int:id>')
@login_required
def delete(id):
    """Delete an analysis result."""
    # Get the analysis
    analysis = AnalysisResult.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete all associated anomalies
        Anomaly.query.filter_by(analysis_result_id=analysis.id).delete()
        
        # Delete the analysis
        db.session.delete(analysis)
        db.session.commit()
        
        flash('Analysis deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting analysis: {str(e)}', 'danger')
    
    return redirect(url_for('results.index'))