"""
Routes for viewing analysis results.
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.results import results_bp
from app.models import Dataset, AnalysisResult, Anomaly


@results_bp.route('/')
@login_required
def index():
    """View all analysis results."""
    # Get all user analyses
    analyses = AnalysisResult.query.filter_by(user_id=current_user.id) \
                                 .order_by(AnalysisResult.created_at.desc()) \
                                 .all()
    
    return render_template('results/index.html',
                          title='Analysis Results',
                          analyses=analyses)


@results_bp.route('/<int:analysis_id>')
@login_required
def view(analysis_id):
    """View a specific analysis result."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to view this analysis.', 'danger')
        return redirect(url_for('results.index'))
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(analysis.dataset_id)
    
    # Get anomalies
    anomalies = Anomaly.query.filter_by(analysis_result_id=analysis_id) \
                           .order_by(Anomaly.score.desc()) \
                           .all()
    
    # Load dataset preview if available
    preview_data = None
    columns = []
    try:
        if os.path.exists(dataset.file_path):
            # Get file extension
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
            
            # Get preview data
            preview_data = df.head(10).to_dict('records')
            columns = df.columns.tolist()
    except Exception as e:
        flash(f'Error loading dataset preview: {str(e)}', 'warning')
    
    # Convert parameters to display format
    algorithm_params = {}
    if analysis.parameters:
        algorithm_params = analysis.parameters
    
    return render_template('results/view.html',
                          title=f'Analysis: {analysis.name}',
                          analysis=analysis,
                          dataset=dataset,
                          anomalies=anomalies,
                          preview_data=preview_data,
                          columns=columns,
                          algorithm_params=algorithm_params)


@results_bp.route('/<int:analysis_id>/anomaly/<int:anomaly_id>')
@login_required
def view_anomaly(analysis_id, anomaly_id):
    """View details of a specific anomaly."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to view this analysis.', 'danger')
        return redirect(url_for('results.index'))
    
    # Get the anomaly
    anomaly = Anomaly.query.get_or_404(anomaly_id)
    
    # Ensure anomaly belongs to this analysis
    if anomaly.analysis_result_id != analysis_id:
        flash('Anomaly does not belong to this analysis.', 'danger')
        return redirect(url_for('results.view', analysis_id=analysis_id))
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(analysis.dataset_id)
    
    # Load dataset if available to get context
    context_data = None
    try:
        if os.path.exists(dataset.file_path):
            # Get file extension
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
            
            # Try to get context around the anomaly
            anomaly_index = anomaly.index
            
            # Get rows before and after the anomaly
            start_idx = max(0, anomaly_index - 2)
            end_idx = min(len(df), anomaly_index + 3)
            
            # Extract context rows
            context_df = df.iloc[start_idx:end_idx]
            context_data = context_df.to_dict('records')
            
            # Highlight the anomaly row
            anomaly_row_idx = anomaly_index - start_idx
    except Exception as e:
        flash(f'Error loading context data: {str(e)}', 'warning')
    
    # Convert feature values to display format
    feature_values = {}
    if anomaly.feature_values:
        feature_values = anomaly.feature_values
    
    return render_template('results/view_anomaly.html',
                          title=f'Anomaly Details',
                          anomaly=anomaly,
                          analysis=analysis,
                          dataset=dataset,
                          feature_values=feature_values,
                          context_data=context_data,
                          anomaly_index=anomaly_index if 'anomaly_index' in locals() else None,
                          anomaly_row_idx=anomaly_row_idx if 'anomaly_row_idx' in locals() else None)


@results_bp.route('/<int:analysis_id>/export')
@login_required
def export(analysis_id):
    """Export analysis results."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to export this analysis.', 'danger')
        return redirect(url_for('results.index'))
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(analysis.dataset_id)
    
    # Get anomalies
    anomalies = Anomaly.query.filter_by(analysis_result_id=analysis_id).all()
    
    # Export format can be CSV, JSON, or Excel
    export_format = request.args.get('format', 'csv')
    
    try:
        # Load original dataset
        if not os.path.exists(dataset.file_path):
            flash('Original dataset file not found.', 'danger')
            return redirect(url_for('results.view', analysis_id=analysis_id))
        
        # Get file extension
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
        
        # Add anomaly column
        df['anomaly'] = 0
        df['anomaly_score'] = 0
        
        # Set anomaly flags and scores
        for anomaly in anomalies:
            if 0 <= anomaly.index < len(df):
                df.loc[anomaly.index, 'anomaly'] = 1
                df.loc[anomaly.index, 'anomaly_score'] = anomaly.score
        
        # Generate export filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f"anomaly_results_{timestamp}"
        
        # Set content type and file extension based on format
        if export_format == 'csv':
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{export_filename}.csv")
            df.to_csv(file_path, index=False)
            return send_file(file_path, as_attachment=True, download_name=f"{export_filename}.csv")
        
        elif export_format == 'excel':
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{export_filename}.xlsx")
            df.to_excel(file_path, index=False)
            return send_file(file_path, as_attachment=True, download_name=f"{export_filename}.xlsx")
        
        elif export_format == 'json':
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{export_filename}.json")
            df.to_json(file_path, orient='records')
            return send_file(file_path, as_attachment=True, download_name=f"{export_filename}.json")
        
        else:
            flash('Invalid export format.', 'danger')
            return redirect(url_for('results.view', analysis_id=analysis_id))
    
    except Exception as e:
        flash(f'Error exporting results: {str(e)}', 'danger')
        return redirect(url_for('results.view', analysis_id=analysis_id))


@results_bp.route('/<int:analysis_id>/delete', methods=['POST'])
@login_required
def delete(analysis_id):
    """Delete an analysis result."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to delete this analysis.', 'danger')
        return redirect(url_for('results.index'))
    
    try:
        # Delete all associated anomalies
        Anomaly.query.filter_by(analysis_result_id=analysis_id).delete()
        
        # Delete the analysis
        db.session.delete(analysis)
        db.session.commit()
        
        flash('Analysis deleted successfully.', 'success')
        return redirect(url_for('results.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting analysis: {str(e)}', 'danger')
        return redirect(url_for('results.view', analysis_id=analysis_id))


@results_bp.route('/<int:analysis_id>/api/anomalies')
@login_required
def api_anomalies(analysis_id):
    """API endpoint to get anomalies for a specific analysis."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get anomalies
    anomalies = Anomaly.query.filter_by(analysis_result_id=analysis_id).all()
    
    # Convert to JSON
    anomalies_data = []
    for anomaly in anomalies:
        # Convert datetime to string to ensure JSON serializable
        timestamp_str = None
        if anomaly.timestamp:
            timestamp_str = anomaly.timestamp.isoformat()
        
        anomalies_data.append({
            'id': anomaly.id,
            'timestamp': timestamp_str,
            'index': anomaly.index,
            'score': float(anomaly.score),
            'is_validated': anomaly.is_validated,
            'is_true_anomaly': anomaly.is_true_anomaly
        })
    
    return jsonify({'anomalies': anomalies_data})