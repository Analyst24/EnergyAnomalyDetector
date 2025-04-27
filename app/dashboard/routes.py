"""
Dashboard routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.dashboard import dashboard

@dashboard.route('/')
@login_required
def index():
    """Dashboard home page"""
    return render_template('dashboard/index.html', title='Dashboard')