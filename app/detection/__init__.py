"""
Detection module for the Energy Anomaly Detection System
"""
from flask import Blueprint

detection = Blueprint('detection', __name__, url_prefix='/detection')

from . import routes