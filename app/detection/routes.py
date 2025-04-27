"""
Detection routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.detection import detection

@detection.route('/')
@login_required
def index():
    """Anomaly detection page"""
    return render_template('detection/index.html', title='Run Detection')