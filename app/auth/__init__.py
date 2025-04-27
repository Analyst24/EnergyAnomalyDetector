"""
Authentication module for the Energy Anomaly Detection System
"""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes