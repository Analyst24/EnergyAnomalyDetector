"""
Main blueprint for home page and general navigation.
"""
from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.main import routes