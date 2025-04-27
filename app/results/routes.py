"""
Results routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.results import results

@results.route('/')
@login_required
def index():
    """Results page to view detection results"""
    return render_template('results/index.html', title='Detection Results')

@results.route('/detail/<int:result_id>')
@login_required
def detail(result_id):
    """Detailed view for a specific detection result"""
    return render_template('results/detail.html', title='Result Details', result_id=result_id)