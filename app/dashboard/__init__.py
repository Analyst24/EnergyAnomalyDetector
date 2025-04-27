"""
Dashboard module for the Energy Anomaly Detection System
"""
from flask import Blueprint

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

from . import routes