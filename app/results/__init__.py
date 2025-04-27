"""
Results module for the Energy Anomaly Detection System
"""
from flask import Blueprint

results = Blueprint('results', __name__, url_prefix='/results')

from . import routes