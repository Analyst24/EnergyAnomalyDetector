"""
Detection blueprint for anomaly detection algorithms.
"""
from flask import Blueprint

detection_bp = Blueprint('detection', __name__, url_prefix='/detection')

from app.detection import routes