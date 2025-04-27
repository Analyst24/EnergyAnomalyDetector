"""
Results blueprint for viewing analysis results.
"""
from flask import Blueprint

results_bp = Blueprint('results', __name__, url_prefix='/results')

from app.results import routes