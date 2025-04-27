"""
Upload module for the Energy Anomaly Detection System
"""
from flask import Blueprint

upload = Blueprint('upload', __name__, url_prefix='/upload')

from . import routes