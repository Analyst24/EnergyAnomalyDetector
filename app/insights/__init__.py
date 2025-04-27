"""
Insights module for the Energy Anomaly Detection System
"""
from flask import Blueprint

insights = Blueprint('insights', __name__, url_prefix='/insights')

from . import routes