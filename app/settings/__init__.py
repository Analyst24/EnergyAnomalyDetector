"""
Settings blueprint for user preferences and system settings.
"""
from flask import Blueprint

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

from app.settings import routes