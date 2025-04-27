"""
Code Snippets routes for the Energy Anomaly Detection System
"""
from flask import render_template
from flask_login import login_required

from app.code_snippets import code_snippets
from app.code_snippets.snippets import (
    data_loading_snippets,
    preprocessing_snippets,
    anomaly_detection_snippets,
    visualization_snippets
)

@code_snippets.route('/')
@login_required
def index():
    """Code snippets library page"""
    return render_template(
        'code_snippets/index.html',
        title='Code Snippets Library',
        data_loading_snippets=data_loading_snippets,
        preprocessing_snippets=preprocessing_snippets,
        anomaly_detection_snippets=anomaly_detection_snippets,
        visualization_snippets=visualization_snippets
    )