"""
User authentication utilities for the Energy Anomaly Detection System.
"""
import streamlit as st
import hashlib
import os
import json

def get_users():
    """
    Get the users dictionary from session state.
    """
    if 'users' not in st.session_state:
        # Initialize with default users
        st.session_state.users = {
            'admin': {
                'password': 'admin123',
                'name': 'Administrator',
                'role': 'Admin'
            },
            'demo': {
                'password': 'demo123',
                'name': 'Demo User',
                'role': 'User'
            }
        }
    
    return st.session_state.users

def hash_password(password):
    """
    Simple password hashing for demo purposes.
    In a production system, use a proper password hashing library like bcrypt.
    """
    # For simplicity, we're using a simple hash, but in production use a proper library
    return password  # In a real system, replace with proper hashing

def verify_password(stored_password, provided_password):
    """
    Verify the provided password against the stored password.
    """
    # For the demo, we're doing a simple comparison
    # In a real system, use a secure comparison
    return stored_password == provided_password

def login_user(username, password):
    """
    Attempt to log in a user.
    Returns True if login successful, False otherwise.
    """
    users = get_users()
    
    if username in users and verify_password(users[username]['password'], password):
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    
    return False

def add_user(username, password, name="", role="User"):
    """
    Add a new user to the system.
    """
    users = get_users()
    
    # Add the new user
    users[username] = {
        'password': password,  # In a real system, hash the password
        'name': name,
        'role': role
    }
    
    # Update the session state
    st.session_state.users = users
    
    return True

def create_user(username, password, name="", role="User"):
    """
    Create a new user if the username doesn't exist.
    Returns True if user created, False if username already exists.
    """
    users = get_users()
    
    if username in users:
        return False
    
    # Add the new user
    add_user(username, password, name, role)
    return True

def is_authenticated():
    """
    Check if the current user is authenticated.
    """
    return st.session_state.get('authenticated', False)

def get_current_user():
    """
    Get the current authenticated username.
    """
    return st.session_state.get('username', None)

def get_user_role(username=None):
    """
    Get the role of the specified user, or the current user if not specified.
    """
    if username is None:
        username = get_current_user()
    
    users = get_users()
    
    if username and username in users:
        return users[username].get('role', 'User')
    
    return None

def logout_user():
    """
    Log out the current user.
    """
    if 'authenticated' in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' in st.session_state:
        st.session_state.username = None
