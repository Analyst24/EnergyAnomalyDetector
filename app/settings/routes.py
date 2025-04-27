"""
Settings routes for the Energy Anomaly Detection System
"""
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app.settings import settings

@settings.route('/')
@login_required
def index():
    """Settings home page"""
    return render_template('settings/index.html', title='Settings')

@settings.route('/profile')
@login_required
def profile():
    """User profile settings page"""
    return render_template('settings/profile.html', title='Profile Settings')

@settings.route('/admin')
@login_required
def admin():
    """Admin settings page (admin access only)"""
    if not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('settings/admin.html', title='Admin Settings')