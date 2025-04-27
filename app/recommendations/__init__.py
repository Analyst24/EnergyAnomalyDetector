"""
Recommendations blueprint for energy efficiency recommendations.
"""
from flask import Blueprint

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')

from app.recommendations import routes