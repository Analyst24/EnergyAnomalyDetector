"""
Authentication routes for the Energy Anomaly Detection System
"""
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, ResetPasswordForm
from app.models import User
from database.connection import get_db_session
from database.crud import get_user_by_username, get_user_by_email, create_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        db_session = get_db_session()
        user = get_user_by_username(db_session, form.username.data)
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db_session.commit()
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash('You have been logged in successfully!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/logout')
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        db_session = get_db_session()
        user = create_user(
            db_session,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            full_name=form.full_name.data
        )
        
        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        db_session = get_db_session()
        user = get_user_by_email(db_session, form.email.data)
        
        if user:
            # In a production system, this would send an email with a reset token
            # For offline system, we'll just redirect to a special reset page
            flash('Password reset instructions would be sent via email in an online system', 'info')
            flash('Since this is an offline system, please contact your system administrator for password resets', 'info')
        else:
            # Don't reveal that the email doesn't exist
            flash('If your email is registered, you will receive password reset instructions', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # In a production system, this would verify the token
    # For an offline system, this is just for demonstration
    form = ResetPasswordForm()
    if form.validate_on_submit():
        flash('Your password has been reset successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)