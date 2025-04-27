"""
Dashboard routes for viewing and managing energy data.
"""
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.models import Dataset, AnalysisResult


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page with overview of user's data and analyses."""
    # Get user's datasets
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    
    # Get user's recent analysis results
    recent_analyses = AnalysisResult.query.filter_by(user_id=current_user.id) \
                                         .order_by(AnalysisResult.created_at.desc()) \
                                         .limit(5) \
                                         .all()
    
    # Statistics for dashboard widgets
    stats = {
        'dataset_count': Dataset.query.filter_by(user_id=current_user.id).count(),
        'analysis_count': AnalysisResult.query.filter_by(user_id=current_user.id).count(),
        'anomaly_count': sum(ar.anomaly_count for ar in 
                            AnalysisResult.query.filter_by(user_id=current_user.id).all())
    }
    
    return render_template('dashboard/index.html',
                          title='Dashboard',
                          datasets=datasets,
                          recent_analyses=recent_analyses,
                          stats=stats)


@dashboard_bp.route('/datasets')
@login_required
def datasets():
    """Page listing all user datasets."""
    user_datasets = Dataset.query.filter_by(user_id=current_user.id) \
                                 .order_by(Dataset.created_at.desc()) \
                                 .all()
    
    return render_template('dashboard/datasets.html',
                          title='My Datasets',
                          datasets=user_datasets)


@dashboard_bp.route('/analyses')
@login_required
def analyses():
    """Page listing all user analysis results."""
    user_analyses = AnalysisResult.query.filter_by(user_id=current_user.id) \
                                      .order_by(AnalysisResult.created_at.desc()) \
                                      .all()
    
    return render_template('dashboard/analyses.html',
                          title='My Analyses',
                          analyses=user_analyses)


@dashboard_bp.route('/dataset/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
    """View detailed information about a specific dataset."""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Ensure user owns this dataset
    if dataset.user_id != current_user.id:
        flash('You do not have permission to view this dataset.', 'danger')
        return redirect(url_for('dashboard.datasets'))
    
    # Get analyses for this dataset
    analyses = AnalysisResult.query.filter_by(dataset_id=dataset_id) \
                                  .order_by(AnalysisResult.created_at.desc()) \
                                  .all()
    
    return render_template('dashboard/view_dataset.html',
                          title=f'Dataset: {dataset.name}',
                          dataset=dataset,
                          analyses=analyses)


@dashboard_bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View detailed information about a specific analysis result."""
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to view this analysis.', 'danger')
        return redirect(url_for('dashboard.analyses'))
    
    # Get the anomalies for this analysis
    anomalies = analysis.anomalies.all()
    
    return render_template('dashboard/view_analysis.html',
                          title=f'Analysis: {analysis.name}',
                          analysis=analysis,
                          anomalies=anomalies)


@dashboard_bp.route('/widget_data/<widget_type>')
@login_required
def widget_data(widget_type):
    """API endpoint for dashboard widget data."""
    if widget_type == 'recent_activity':
        # Get latest datasets and analyses
        datasets = Dataset.query.filter_by(user_id=current_user.id) \
                               .order_by(Dataset.created_at.desc()) \
                               .limit(3) \
                               .all()
        
        analyses = AnalysisResult.query.filter_by(user_id=current_user.id) \
                                     .order_by(AnalysisResult.created_at.desc()) \
                                     .limit(3) \
                                     .all()
        
        data = {
            'datasets': [{'name': d.name, 'created_at': d.created_at.strftime('%Y-%m-%d %H:%M')} 
                        for d in datasets],
            'analyses': [{'name': a.name, 'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')} 
                        for a in analyses]
        }
        
        return jsonify(data)
    
    elif widget_type == 'anomaly_summary':
        # Get summary of anomalies by algorithm
        results = AnalysisResult.query.filter_by(user_id=current_user.id).all()
        
        algorithm_counts = {}
        for result in results:
            if result.algorithm in algorithm_counts:
                algorithm_counts[result.algorithm] += result.anomaly_count
            else:
                algorithm_counts[result.algorithm] = result.anomaly_count
        
        data = {
            'labels': list(algorithm_counts.keys()),
            'values': list(algorithm_counts.values())
        }
        
        return jsonify(data)
    
    # Default response for unknown widget type
    return jsonify({'error': 'Unknown widget type'}), 400