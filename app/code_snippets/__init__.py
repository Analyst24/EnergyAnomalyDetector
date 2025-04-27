"""
Code snippets blueprint for sharing code examples with users.
"""
from flask import Blueprint

code_snippets_bp = Blueprint('code_snippets', __name__, url_prefix='/code-snippets')

from app.code_snippets import routes