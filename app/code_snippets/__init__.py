"""
Code Snippets module for the Energy Anomaly Detection System
"""
from flask import Blueprint

code_snippets = Blueprint('code_snippets', __name__, url_prefix='/code_snippets')

from . import routes