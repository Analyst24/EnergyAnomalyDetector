"""
Insights routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.insights import insights

@insights.route('/')
@login_required
def index():
    """Model insights page"""
    return render_template('insights/index.html', title='Model Insights')