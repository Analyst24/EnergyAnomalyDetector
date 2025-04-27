"""
Routes for user preferences and system settings.
"""
import os
import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.settings import settings_bp
from app.models import User, UserPreference


@settings_bp.route('/')
@login_required
def index():
    """User settings and preferences page."""
    # Get user preferences
    user_prefs = UserPreference.query.filter_by(user_id=current_user.id).first()
    
    # If no preferences exist, create default ones
    if not user_prefs:
        user_prefs = UserPreference(
            user_id=current_user.id,
            theme='dark',
            dashboard_layout=None,
            default_algorithm=None,
            default_params=None
        )
        db.session.add(user_prefs)
        db.session.commit()
    
    return render_template('settings/index.html',
                          title='Settings',
                          user=current_user,
                          prefs=user_prefs)


@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile settings."""
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        
        # Validate form data
        if not full_name or not email:
            flash('All fields are required.', 'danger')
            return redirect(url_for('settings.profile'))
        
        # Check if email is already in use by another user
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash('Email is already in use.', 'danger')
            return redirect(url_for('settings.profile'))
        
        # Update user profile
        current_user.full_name = full_name
        current_user.email = email
        
        # Save changes
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('settings.profile'))
    
    return render_template('settings/profile.html',
                          title='Profile Settings',
                          user=current_user)


@settings_bp.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    """Change password."""
    if request.method == 'POST':
        # Get form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('settings.password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('settings.password'))
        
        # Check current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('settings.password'))
        
        # Update password
        current_user.set_password(new_password)
        
        # Save changes
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('settings.password'))
    
    return render_template('settings/password.html',
                          title='Change Password')


@settings_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """User preferences settings."""
    # Get user preferences
    user_prefs = UserPreference.query.filter_by(user_id=current_user.id).first()
    
    # If no preferences exist, create default ones
    if not user_prefs:
        user_prefs = UserPreference(
            user_id=current_user.id,
            theme='dark',
            dashboard_layout=None,
            default_algorithm=None,
            default_params=None
        )
        db.session.add(user_prefs)
        db.session.commit()
    
    if request.method == 'POST':
        # Get form data
        theme = request.form.get('theme', 'dark')
        default_algorithm = request.form.get('default_algorithm')
        
        # Update preferences
        user_prefs.theme = theme
        user_prefs.default_algorithm = default_algorithm
        user_prefs.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('settings.preferences'))
    
    return render_template('settings/preferences.html',
                          title='Preferences',
                          prefs=user_prefs)


@settings_bp.route('/api/preferences', methods=['GET', 'PUT'])
@login_required
def api_preferences():
    """API endpoint for user preferences."""
    # Get user preferences
    user_prefs = UserPreference.query.filter_by(user_id=current_user.id).first()
    
    # If no preferences exist, create default ones
    if not user_prefs:
        user_prefs = UserPreference(
            user_id=current_user.id,
            theme='dark',
            dashboard_layout=None,
            default_algorithm=None,
            default_params=None
        )
        db.session.add(user_prefs)
        db.session.commit()
    
    if request.method == 'GET':
        # Return preferences as JSON
        prefs_data = {
            'theme': user_prefs.theme,
            'dashboard_layout': user_prefs.dashboard_layout,
            'default_algorithm': user_prefs.default_algorithm,
            'default_params': user_prefs.default_params
        }
        return jsonify(prefs_data)
    
    elif request.method == 'PUT':
        # Update preferences from JSON data
        data = request.get_json()
        
        if 'theme' in data:
            user_prefs.theme = data['theme']
        
        if 'dashboard_layout' in data:
            user_prefs.dashboard_layout = data['dashboard_layout']
        
        if 'default_algorithm' in data:
            user_prefs.default_algorithm = data['default_algorithm']
        
        if 'default_params' in data:
            user_prefs.default_params = data['default_params']
        
        user_prefs.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({'message': 'Preferences updated successfully'})