"""
Main routes for the Energy Anomaly Detection System
"""
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.main import main

@main.route('/')
def index():
    """Home page route"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    return render_template('main/index.html', title='Home')

@main.route('/about')
def about():
    """About page route"""
    return render_template('main/about.html', title='About')