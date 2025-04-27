"""
Insights blueprint for energy data visualization and insights.
"""
from flask import Blueprint

insights_bp = Blueprint('insights', __name__, url_prefix='/insights')

from app.insights import routes