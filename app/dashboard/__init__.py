"""
Dashboard blueprint for the main application dashboard.
"""
from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

from app.dashboard import routes