"""
Authentication routes for the Energy Anomaly Detection System
"""
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, ResetPasswordForm
from app.models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, send reset email
            # For this offline version, we'll just redirect with a message
            flash('If an account exists with that email, a password reset link would be sent.', 'info')
        else:
            # Don't reveal if user exists or not
            flash('If an account exists with that email, a password reset link would be sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # In a real application, verify the token
    # For this offline version, we'll just show a message
    flash('Password reset functionality is disabled in offline mode.', 'warning')
    return redirect(url_for('auth.login'))