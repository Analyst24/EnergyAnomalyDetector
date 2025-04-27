"""
User authentication utilities for the Energy Anomaly Detection System.
"""
import streamlit as st
import hashlib
import os
import json
import logging
from typing import Optional, Dict, Any, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag to determine whether to use database or session storage
# This can be set to True once the database is fully integrated
USE_DATABASE = True

try:
    # Try to import database modules
    from database.connection import SessionLocal
    from database.crud import (
        get_user_by_username, 
        get_user_by_email, 
        create_user as db_create_user,
        verify_password as db_verify_password
    )
    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Database modules not available, falling back to session state for authentication")
    DATABASE_AVAILABLE = False

def get_users():
    """
    Get the users dictionary from session state.
    Used as fallback when database is not available.
    """
    if 'users' not in st.session_state:
        # Initialize with default users
        st.session_state.users = {
            'admin': {
                'password': 'admin123',
                'name': 'Administrator',
                'role': 'Admin',
                'email': 'admin@example.com'
            },
            'demo': {
                'password': 'demo123',
                'name': 'Demo User',
                'role': 'User',
                'email': 'demo@example.com'
            }
        }
    
    return st.session_state.users

def hash_password(password: str) -> str:
    """
    Simple password hashing.
    In a production system, use a proper password hashing library like bcrypt.
    """
    # For simplicity, we're using a simple hash, but in production use a proper library
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify the provided password against the stored password.
    """
    if USE_DATABASE and DATABASE_AVAILABLE:
        # Database implementation handles this internally
        return stored_password == provided_password
    else:
        # Session state implementation (simple comparison)
        return stored_password == provided_password

def login_user(username_or_email: str, password: str) -> bool:
    """
    Attempt to log in a user.
    Works with either username or email.
    
    Args:
        username_or_email: Username or email address
        password: Password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    # First, try database authentication if enabled
    if USE_DATABASE and DATABASE_AVAILABLE:
        try:
            db = SessionLocal()
            # Check if input is email
            if '@' in username_or_email:
                user = get_user_by_email(db, username_or_email)
            else:
                user = get_user_by_username(db, username_or_email)
                
            if user and db_verify_password(user.hashed_password, password):
                st.session_state.authenticated = True
                st.session_state.username = user.username
                st.session_state.user_id = user.id
                st.session_state.user_role = user.role
                db.close()
                return True
            
            db.close()
            return False
        except Exception as e:
            logger.error(f"Database login error: {e}")
            # Fall back to session state if database fails
    
    # Fallback to session state authentication
    users = get_users()
    
    # Check if input is email
    if '@' in username_or_email:
        # Find user with matching email
        for username, user_data in users.items():
            if user_data.get('email') == username_or_email:
                if verify_password(user_data['password'], password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    return True
        return False
    else:
        # Standard username login
        if username_or_email in users and verify_password(users[username_or_email]['password'], password):
            st.session_state.authenticated = True
            st.session_state.username = username_or_email
            return True
    
    return False

def add_user(username: str, password: str, name: str = "", role: str = "User") -> bool:
    """
    Add a new user to the system.
    
    Args:
        username: Username
        password: Password (will be hashed in DB mode)
        name: Full name
        role: User role
        
    Returns:
        bool: True if successful
    """
    if USE_DATABASE and DATABASE_AVAILABLE:
        try:
            db = SessionLocal()
            # Create email from username if not provided
            email = f"{username}@example.com"
            
            # Create user in database
            db_create_user(
                db=db,
                username=username,
                email=email,
                password=password,  # Will be hashed in the database function
                full_name=name,
                role=role
            )
            db.close()
            return True
        except Exception as e:
            logger.error(f"Database add user error: {e}")
            # Fall back to session state if database fails
    
    # Fallback to session state
    users = get_users()
    
    # Add the new user
    users[username] = {
        'password': password,  # Session state version doesn't hash
        'name': name,
        'role': role,
        'email': f"{username}@example.com"  # Default email
    }
    
    # Update the session state
    st.session_state.users = users
    
    return True

def create_user(username: str, password: str, name: str = "", role: str = "User", email: str = None) -> bool:
    """
    Create a new user if the username doesn't exist.
    
    Args:
        username: Username
        password: Password
        name: Full name
        role: User role
        email: Email address (optional)
        
    Returns:
        bool: True if user created, False if username already exists
    """
    if USE_DATABASE and DATABASE_AVAILABLE:
        try:
            db = SessionLocal()
            # Check if user exists
            existing_user = get_user_by_username(db, username)
            
            if existing_user:
                db.close()
                return False
            
            # If email not provided, create one from username
            if not email:
                email = f"{username}@example.com"
                
            # Check if email exists
            existing_email = get_user_by_email(db, email)
            if existing_email:
                db.close()
                return False
            
            # Create user in database
            db_create_user(
                db=db,
                username=username,
                email=email,
                password=password,
                full_name=name,
                role=role
            )
            db.close()
            return True
        except Exception as e:
            logger.error(f"Database create user error: {e}")
            # Fall back to session state if database fails
    
    # Fallback to session state
    users = get_users()
    
    if username in users:
        return False
    
    # Add the new user
    add_user(username, password, name, role)
    return True

def is_authenticated() -> bool:
    """
    Check if the current user is authenticated.
    
    Returns:
        bool: True if authenticated
    """
    return st.session_state.get('authenticated', False)

def get_current_user() -> Optional[str]:
    """
    Get the current authenticated username.
    
    Returns:
        str: Username, or None if not authenticated
    """
    return st.session_state.get('username', None)

def get_user_id() -> Optional[int]:
    """
    Get the current authenticated user ID.
    
    Returns:
        int: User ID, or None if not authenticated or in session mode
    """
    return st.session_state.get('user_id', None)

def get_user_role(username: Optional[str] = None) -> Optional[str]:
    """
    Get the role of the specified user, or the current user if not specified.
    
    Args:
        username: Username (optional, defaults to current user)
        
    Returns:
        str: User role, or None if not found
    """
    if USE_DATABASE and DATABASE_AVAILABLE and username is None:
        # For current user, we can use the cached role
        return st.session_state.get('user_role', None)
    
    if username is None:
        username = get_current_user()
    
    if USE_DATABASE and DATABASE_AVAILABLE:
        try:
            db = SessionLocal()
            user = get_user_by_username(db, username)
            db.close()
            if user:
                return user.role
            return None
        except Exception as e:
            logger.error(f"Database get user role error: {e}")
            # Fall back to session state if database fails
    
    # Fallback to session state
    users = get_users()
    
    if username and username in users:
        return users[username].get('role', 'User')
    
    return None

def logout_user() -> None:
    """
    Log out the current user.
    """
    if 'authenticated' in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' in st.session_state:
        st.session_state.username = None
        
    if 'user_id' in st.session_state:
        st.session_state.user_id = None
        
    if 'user_role' in st.session_state:
        st.session_state.user_role = None
    
    # Clear any other user-specific session data
    for key in list(st.session_state.keys()):
        if key.startswith('user_'):
            del st.session_state[key]
