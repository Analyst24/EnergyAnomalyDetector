"""
Recommendations module for the Energy Anomaly Detection System
"""
from flask import Blueprint

recommendations = Blueprint('recommendations', __name__, url_prefix='/recommendations')

from . import routes