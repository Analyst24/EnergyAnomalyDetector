"""
Authentication forms for the Energy Anomaly Detection System.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """Login form."""
    email = StringField('Email', validators=[
        DataRequired(), 
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    """User registration form."""
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=100)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        """Validate that username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        """Validate that email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email.')