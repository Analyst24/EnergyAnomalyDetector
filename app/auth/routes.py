"""
Authentication routes for the Energy Anomaly Detection System.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.auth.forms import LoginForm, SignupForm

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html', form=form)
        
        # Log in the user
        login_user(user, remember=form.remember.data)
        
        # Update last login timestamp
        user.last_login = db.func.now()
        db.session.commit()
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
            
        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different username.', 'danger')
            return render_template('auth/signup.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email or log in.', 'danger')
            return render_template('auth/signup.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))