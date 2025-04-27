"""
Upload blueprint for handling file uploads and parsing.
"""
from flask import Blueprint

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

from app.upload import routes