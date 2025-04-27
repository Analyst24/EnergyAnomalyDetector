"""
Routes for energy efficiency recommendations.
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.recommendations import recommendations_bp
from app.models import Dataset, AnalysisResult


# Custom JSON encoder to handle timedelta objects
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles timedelta objects."""
    def default(self, o):
        if isinstance(o, timedelta):
            # Convert timedelta to dictionary with days, hours, minutes, seconds
            return {
                "_type": "timedelta",
                "days": o.days,
                "seconds": o.seconds,
                "microseconds": o.microseconds
            }
        return super().default(o)


# Function to convert serialized timedelta back to timedelta object
def timedelta_decoder(obj):
    """Convert serialized timedelta back to timedelta object."""
    if '_type' in obj and obj['_type'] == 'timedelta':
        return timedelta(
            days=obj.get('days', 0),
            seconds=obj.get('seconds', 0),
            microseconds=obj.get('microseconds', 0)
        )
    return obj


def generate_recommendations(dataset, analysis):
    """Generate energy efficiency recommendations based on analysis results."""
    recommendations = []
    
    # Basic recommendations based on anomaly patterns
    recommendations.append({
        "title": "Schedule Regular Maintenance",
        "description": "Schedule regular maintenance for energy systems to ensure peak efficiency.",
        "impact": "Medium",
        "cost": "Medium",
        "timeline": timedelta(days=30),
        "category": "Maintenance"
    })
    
    recommendations.append({
        "title": "Install Energy Monitoring System",
        "description": "Install real-time energy monitoring system to detect anomalies early.",
        "impact": "High",
        "cost": "Medium",
        "timeline": timedelta(days=60),
        "category": "Monitoring"
    })
    
    recommendations.append({
        "title": "Optimize Operation Hours",
        "description": "Adjust operating hours of equipment to match usage patterns and reduce idle energy consumption.",
        "impact": "Medium",
        "cost": "Low",
        "timeline": timedelta(days=7),
        "category": "Operations"
    })
    
    # Add more advanced recommendations based on anomaly patterns
    if analysis and hasattr(analysis, 'anomaly_count') and analysis.anomaly_count > 10:
        recommendations.append({
            "title": "Conduct Energy Audit",
            "description": "Conduct comprehensive energy audit to identify all inefficiencies.",
            "impact": "High",
            "cost": "High",
            "timeline": timedelta(days=90),
            "category": "Assessment"
        })
    
    # Convert timedelta to serializable format
    serializable_recommendations = []
    for rec in recommendations:
        serializable_rec = rec.copy()
        
        # Convert timedelta to a string representation (e.g., "30 days")
        if isinstance(rec['timeline'], timedelta):
            days = rec['timeline'].days
            hours = rec['timeline'].seconds // 3600
            
            if days > 0 and hours > 0:
                serializable_rec['timeline_str'] = f"{days} days, {hours} hours"
            elif days > 0:
                serializable_rec['timeline_str'] = f"{days} days"
            elif hours > 0:
                serializable_rec['timeline_str'] = f"{hours} hours"
            else:
                serializable_rec['timeline_str'] = "Less than a day"
        
        serializable_recommendations.append(serializable_rec)
    
    return serializable_recommendations


def generate_implementation_timeline(recommendations):
    """Generate implementation timeline for recommendations."""
    # Sort recommendations by timeline
    sorted_recs = sorted(recommendations, key=lambda x: x['timeline'].days if isinstance(x['timeline'], timedelta) else 0)
    
    timeline_data = []
    start_date = datetime.now()
    
    for i, rec in enumerate(sorted_recs):
        # Calculate start and end dates
        if i == 0:
            start = start_date
        else:
            # Start after the previous task
            prev_end = timeline_data[i-1]['end']
            start = prev_end + timedelta(days=3)  # 3 days buffer between tasks
        
        # Add the timeline
        if isinstance(rec['timeline'], timedelta):
            end = start + rec['timeline']
        else:
            end = start + timedelta(days=30)  # Default to 30 days if timeline is not a timedelta
        
        # Create timeline entry
        timeline_entry = {
            'task': rec['title'],
            'start': start,
            'end': end,
            'category': rec['category'],
            'impact': rec['impact'],
            'description': rec['description']
        }
        
        timeline_data.append(timeline_entry)
    
    # Convert dates to strings for JSON serialization
    serializable_timeline = []
    for entry in timeline_data:
        serializable_entry = {
            'task': entry['task'],
            'start': entry['start'].strftime('%Y-%m-%d'),
            'end': entry['end'].strftime('%Y-%m-%d'),
            'category': entry['category'],
            'impact': entry['impact'],
            'description': entry['description']
        }
        serializable_timeline.append(serializable_entry)
    
    return serializable_timeline


@recommendations_bp.route('/')
@login_required
def index():
    """Energy efficiency recommendations page."""
    # Get all user analyses
    analyses = AnalysisResult.query.filter_by(user_id=current_user.id) \
                                 .order_by(AnalysisResult.created_at.desc()) \
                                 .all()
    
    # Generate recommendations if there are analyses
    recommendations = []
    timeline_data = []
    
    if analyses:
        # Use the most recent analysis for recommendations
        latest_analysis = analyses[0]
        dataset = Dataset.query.get_or_404(latest_analysis.dataset_id)
        
        # Generate recommendations
        recommendations = generate_recommendations(dataset, latest_analysis)
        
        # Generate implementation timeline
        timeline_data = generate_implementation_timeline(recommendations)
    
    return render_template('recommendations/index.html',
                          title='Energy Efficiency Recommendations',
                          analyses=analyses,
                          recommendations=recommendations,
                          timeline_data=json.dumps(timeline_data, cls=CustomJSONEncoder),
                          latest_analysis=analyses[0] if analyses else None)


@recommendations_bp.route('/<int:analysis_id>')
@login_required
def for_analysis(analysis_id):
    """View recommendations for a specific analysis."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to view recommendations for this analysis.', 'danger')
        return redirect(url_for('recommendations.index'))
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(analysis.dataset_id)
    
    # Generate recommendations
    recommendations = generate_recommendations(dataset, analysis)
    
    # Generate implementation timeline
    timeline_data = generate_implementation_timeline(recommendations)
    
    return render_template('recommendations/for_analysis.html',
                          title=f'Recommendations for {analysis.name}',
                          analysis=analysis,
                          dataset=dataset,
                          recommendations=recommendations,
                          timeline_data=json.dumps(timeline_data, cls=CustomJSONEncoder))


@recommendations_bp.route('/api/timeline/<int:analysis_id>')
@login_required
def api_timeline(analysis_id):
    """API endpoint to get implementation timeline for a specific analysis."""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Ensure user owns this analysis
    if analysis.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(analysis.dataset_id)
    
    # Generate recommendations
    recommendations = generate_recommendations(dataset, analysis)
    
    # Generate implementation timeline
    timeline_data = generate_implementation_timeline(recommendations)
    
    # Use the custom encoder for the response
    return current_app.response_class(
        json.dumps({'timeline': timeline_data}, cls=CustomJSONEncoder),
        mimetype='application/json'
    )