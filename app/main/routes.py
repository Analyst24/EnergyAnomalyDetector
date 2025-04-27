"""
Main routes for the Energy Anomaly Detection System.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Dataset, AnalysisResult

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Render the home page."""
    # Get user's datasets count
    dataset_count = Dataset.query.filter_by(user_id=current_user.id).count()
    
    # Get recent analyses
    recent_analyses = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(
        AnalysisResult.created_at.desc()
    ).limit(5).all()
    
    # Get total anomalies count
    total_anomalies = 0
    for analysis in AnalysisResult.query.filter_by(user_id=current_user.id).all():
        total_anomalies += analysis.anomaly_count
    
    # Render home page with data
    return render_template(
        'home.html',
        active_page='home',
        dataset_count=dataset_count,
        recent_analyses=recent_analyses,
        total_anomalies=total_anomalies
    )