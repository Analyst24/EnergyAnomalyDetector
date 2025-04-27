"""
Authentication routes for user login, registration, and password management.
"""
import datetime
import secrets
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import auth_bp
from app.auth.forms import (
    LoginForm, RegistrationForm, RequestPasswordResetForm,
    ResetPasswordForm, ChangePasswordForm, ProfileUpdateForm
)
from app.models import User, UserPreference


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # First check if input is username
        user = User.query.filter_by(username=form.username.data.lower()).first()
        
        # If not found, check if input is email
        if user is None:
            user = User.query.filter_by(email=form.username.data.lower()).first()
        
        # If user not found or password is wrong
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username/email or password', 'danger')
            return render_template('auth/login.html', title='Sign In', form=form)
        
        # Log in the user
        login_user(user, remember=form.remember_me.data)
        
        # Update last login time
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
        # Redirect to the page the user wanted to access
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        flash('You have been logged in successfully!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        # Create default user preferences
        preferences = UserPreference(user_id=user.id)
        db.session.add(preferences)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # Generate reset token (in production you would send email)
            reset_token = secrets.token_urlsafe(32)
            # Store token information in session or temporary storage
            
            # In this offline app, just show the token for demonstration
            flash(f'Password reset requested for {user.email}. Use this token: {reset_token}', 'info')
            return redirect(url_for('auth.reset_password', token=reset_token))
        else:
            # For security, don't reveal that the email doesn't exist
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # In a real app, validate the token here
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # In a real app, find the user associated with this token
        user = User.query.filter_by(id=1).first()  # Placeholder
        
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form, token=token)


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route for logged-in users."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('auth/change_password.html', title='Change Password', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page."""
    form = ProfileUpdateForm(current_user.email)
    
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data.lower()
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', title='Profile', form=form)