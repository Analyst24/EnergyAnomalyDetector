"""
Settings module for the Energy Anomaly Detection System
"""
from flask import Blueprint

settings = Blueprint('settings', __name__, url_prefix='/settings')

from . import routes