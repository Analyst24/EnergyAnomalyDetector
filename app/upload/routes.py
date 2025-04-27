"""
Upload routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.upload import upload

@upload.route('/')
@login_required
def index():
    """Upload data page"""
    return render_template('upload/index.html', title='Upload Data')