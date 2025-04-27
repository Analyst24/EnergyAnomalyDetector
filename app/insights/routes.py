"""
Routes for energy data visualization and insights.
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.insights import insights_bp
from app.models import Dataset, AnalysisResult, Anomaly


@insights_bp.route('/')
@login_required
def index():
    """Energy data visualization and insights dashboard."""
    # Get all user datasets
    datasets = Dataset.query.filter_by(user_id=current_user.id) \
                          .order_by(Dataset.created_at.desc()) \
                          .all()
    
    # Get all user analyses
    analyses = AnalysisResult.query.filter_by(user_id=current_user.id) \
                                 .order_by(AnalysisResult.created_at.desc()) \
                                 .all()
    
    return render_template('insights/index.html',
                          title='Energy Insights',
                          datasets=datasets,
                          analyses=analyses)


@insights_bp.route('/dataset/<int:dataset_id>')
@login_required
def dataset_insights(dataset_id):
    """View insights for a specific dataset."""
    # Get the dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure user owns this dataset
    if dataset.user_id != current_user.id:
        flash('You do not have permission to view this dataset.', 'danger')
        return redirect(url_for('insights.index'))
    
    # Load dataset
    try:
        if not os.path.exists(dataset.file_path):
            flash('Dataset file not found.', 'danger')
            return redirect(url_for('insights.index'))
        
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
        else:
            flash(f'Unsupported file format: {ext}', 'danger')
            return redirect(url_for('insights.index'))
        
        # Basic dataset statistics
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'missing_values': df.isna().sum().sum(),
            'memory_usage': df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
        }
        
        # Numeric column summary
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_summary = {}
        for col in numeric_cols:
            numeric_summary[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std())
            }
        
        # Generate distribution plot for numeric columns
        distribution_plots = {}
        for col in numeric_cols[:5]:  # Limit to first 5 columns
            fig = px.histogram(df, x=col, title=f'Distribution of {col}',
                              histnorm='probability density',
                              labels={col: col},
                              color_discrete_sequence=['#4b7bec'])
            
            fig.update_layout(
                plot_bgcolor='rgba(30, 39, 46, 0.8)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            distribution_plots[col] = json.dumps(fig.to_dict())
        
        # Check for timestamp columns
        timestamp_cols = []
        time_series_plots = {}
        
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    # Convert to datetime and check if successful
                    df[col] = pd.to_datetime(df[col])
                    timestamp_cols.append(col)
                except:
                    pass
        
        # Generate time series plots for numeric columns with timestamp
        if timestamp_cols and numeric_cols:
            timestamp_col = timestamp_cols[0]  # Use first timestamp column
            
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                fig = px.line(df.sort_values(timestamp_col), x=timestamp_col, y=col,
                             title=f'Time Series of {col}',
                             labels={col: col, timestamp_col: 'Time'},
                             color_discrete_sequence=['#4b7bec'])
                
                fig.update_layout(
                    plot_bgcolor='rgba(30, 39, 46, 0.8)',
                    paper_bgcolor='rgba(30, 39, 46, 0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                time_series_plots[col] = json.dumps(fig.to_dict())
        
        # Get associated analyses
        analyses = AnalysisResult.query.filter_by(dataset_id=dataset_id) \
                                    .order_by(AnalysisResult.created_at.desc()) \
                                    .all()
        
        return render_template('insights/dataset.html',
                              title=f'Insights: {dataset.name}',
                              dataset=dataset,
                              stats=stats,
                              numeric_cols=numeric_cols,
                              numeric_summary=numeric_summary,
                              distribution_plots=distribution_plots,
                              timestamp_cols=timestamp_cols,
                              time_series_plots=time_series_plots,
                              analyses=analyses)
    
    except Exception as e:
        flash(f'Error generating insights: {str(e)}', 'danger')
        return redirect(url_for('insights.index'))


@insights_bp.route('/analysis/<int:analysis_id>')
@login_required
def analysis_insights(analysis_id):
    """View insights for a specific analysis result."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to view this analysis.', 'danger')
        return redirect(url_for('insights.index'))
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(analysis.dataset_id)
    
    # Get anomalies
    anomalies = Anomaly.query.filter_by(analysis_result_id=analysis_id) \
                           .order_by(Anomaly.score.desc()) \
                           .all()
    
    # Load dataset
    try:
        if not os.path.exists(dataset.file_path):
            flash('Dataset file not found.', 'danger')
            return redirect(url_for('insights.index'))
        
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
        else:
            flash(f'Unsupported file format: {ext}', 'danger')
            return redirect(url_for('insights.index'))
        
        # Add anomaly column to dataframe
        df['anomaly'] = 0
        df['anomaly_score'] = 0
        
        # Set anomaly flags and scores
        for anomaly in anomalies:
            if 0 <= anomaly.index < len(df):
                df.loc[anomaly.index, 'anomaly'] = 1
                df.loc[anomaly.index, 'anomaly_score'] = anomaly.score
        
        # Generate insights
        
        # 1. Anomaly percentage
        anomaly_count = len(anomalies)
        anomaly_percentage = anomaly_count / len(df) * 100 if len(df) > 0 else 0
        
        # 2. Anomaly score distribution
        anomaly_scores = [anomaly.score for anomaly in anomalies]
        
        # 3. Timestamp patterns
        timestamp_cols = []
        time_series_plot = None
        anomaly_timeline_plot = None
        
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    # Convert to datetime and check if successful
                    df[col] = pd.to_datetime(df[col])
                    timestamp_cols.append(col)
                except:
                    pass
        
        # Generate time series with anomalies highlighted
        if timestamp_cols and analysis.parameters and 'target_column' in analysis.parameters:
            timestamp_col = timestamp_cols[0]  # Use first timestamp column
            target_col = analysis.parameters['target_column']
            
            if target_col in df.columns:
                # Create filtered dataframes
                normal_df = df[df['anomaly'] == 0]
                anomaly_df = df[df['anomaly'] == 1]
                
                # Create figure
                fig = go.Figure()
                
                # Add normal points
                fig.add_trace(go.Scatter(
                    x=normal_df[timestamp_col],
                    y=normal_df[target_col],
                    mode='lines',
                    name='Normal Data',
                    line=dict(color='#4b7bec')
                ))
                
                # Add anomaly points
                fig.add_trace(go.Scatter(
                    x=anomaly_df[timestamp_col],
                    y=anomaly_df[target_col],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(size=10, color='red', symbol='circle')
                ))
                
                # Update layout
                fig.update_layout(
                    title=f'Time Series of {target_col} with Anomalies',
                    xaxis_title='Time',
                    yaxis_title=target_col,
                    plot_bgcolor='rgba(30, 39, 46, 0.8)',
                    paper_bgcolor='rgba(30, 39, 46, 0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                    margin=dict(l=20, r=20, t=50, b=20),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                time_series_plot = json.dumps(fig.to_dict())
                
                # Generate timeline of anomalies if there are anomalies
                if anomaly_count > 0:
                    # Count anomalies by day
                    anomaly_df['date'] = anomaly_df[timestamp_col].dt.date
                    anomaly_counts = anomaly_df.groupby('date').size().reset_index(name='count')
                    anomaly_counts['date'] = pd.to_datetime(anomaly_counts['date'])
                    
                    fig = px.bar(anomaly_counts, x='date', y='count',
                                title='Anomaly Frequency by Day',
                                labels={'count': 'Number of Anomalies', 'date': 'Date'},
                                color_discrete_sequence=['#e74c3c'])
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(30, 39, 46, 0.8)',
                        paper_bgcolor='rgba(30, 39, 46, 0)',
                        font=dict(color='white'),
                        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    
                    anomaly_timeline_plot = json.dumps(fig.to_dict())
        
        # 4. Score histogram
        score_histogram = None
        if anomaly_scores:
            fig = px.histogram(anomaly_scores, title='Anomaly Score Distribution',
                              labels={'value': 'Anomaly Score', 'count': 'Frequency'},
                              color_discrete_sequence=['#e74c3c'])
            
            fig.update_layout(
                plot_bgcolor='rgba(30, 39, 46, 0.8)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            score_histogram = json.dumps(fig.to_dict())
        
        return render_template('insights/analysis.html',
                              title=f'Insights: {analysis.name}',
                              analysis=analysis,
                              dataset=dataset,
                              anomaly_count=anomaly_count,
                              anomaly_percentage=anomaly_percentage,
                              time_series_plot=time_series_plot,
                              anomaly_timeline_plot=anomaly_timeline_plot,
                              score_histogram=score_histogram)
    
    except Exception as e:
        flash(f'Error generating insights: {str(e)}', 'danger')
        return redirect(url_for('insights.index'))


@insights_bp.route('/api/dataset/<int:dataset_id>/summary')
@login_required
def api_dataset_summary(dataset_id):
    """API endpoint to get summary statistics for a dataset."""
    # Get the dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure user owns this dataset
    if dataset.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        if not os.path.exists(dataset.file_path):
            return jsonify({'error': 'Dataset file not found'}), 404
        
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
        else:
            return jsonify({'error': f'Unsupported file format: {ext}'}), 400
        
        # Numeric column summary
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_summary = {}
        for col in numeric_cols:
            numeric_summary[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std())
            }
        
        # Basic dataset statistics
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'numeric_columns': len(numeric_cols),
            'missing_values': int(df.isna().sum().sum()),
            'memory_usage': float(df.memory_usage(deep=True).sum() / (1024 * 1024)),  # MB
            'columns': df.columns.tolist(),
            'numeric_cols': numeric_cols,
            'numeric_summary': numeric_summary
        }
        
        return jsonify(summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500