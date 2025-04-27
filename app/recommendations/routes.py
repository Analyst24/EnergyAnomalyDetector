"""
Recommendations routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.recommendations import recommendations

@recommendations.route('/')
@login_required
def index():
    """Recommendations page"""
    return render_template('recommendations/index.html', title='Recommendations')