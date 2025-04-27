"""
Main routes for home page and general navigation.
"""
from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main_bp


@main_bp.route('/')
def index():
    """Home page route."""
    # If user is logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    return render_template('main/index.html', title='Home')


@main_bp.route('/about')
def about():
    """About page with information about the system."""
    return render_template('main/about.html', title='About')


@main_bp.route('/features')
def features():
    """Features page showcasing the capabilities of the system."""
    return render_template('main/features.html', title='Features')


@main_bp.route('/help')
def help():
    """Help page with documentation and user guides."""
    return render_template('main/help.html', title='Help & Documentation')