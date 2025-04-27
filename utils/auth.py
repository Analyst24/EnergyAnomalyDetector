"""
Authentication utilities for the Energy Anomaly Detection System
"""
import streamlit as st
import hashlib
import sys
import os
import json
from typing import Dict, List, Optional, Tuple, Any

# Add parent directory to path
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import get_db_session
from database.crud import (
    get_user_by_username, get_user_by_id, get_user_by_email,
    create_user as db_create_user, update_user, delete_user,
    verify_password as db_verify_password, hash_password as db_hash_password
)
from database.models import User

def hash_password(password: str) -> str:
    """
    Generate a secure hash for the password
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return db_hash_password(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        stored_hash: The stored hash
        password: The plaintext password to check
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return db_verify_password(stored_hash, password)

def check_credentials(username: str, password: str) -> bool:
    """
    Check if the provided credentials are valid.
    
    Args:
        username: The username to check
        password: The plaintext password to check
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        # Get database session
        db = get_db_session()
        
        # Get user by username
        user = get_user_by_username(db, username)
        
        if user and db_verify_password(user.hashed_password, password):
            return True
        return False
    except Exception as e:
        st.error(f"Error checking credentials: {str(e)}")
        return False

def create_user(username: str, email: str, password: str, full_name: str = None, role: str = "User") -> Optional[Dict]:
    """
    Create a new user in the database
    
    Args:
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: User's full name (optional)
        role: User role (default: "User")
        
    Returns:
        Optional[Dict]: User data dict if successful, None if error
    """
    try:
        db = get_db_session()
        
        # Check if username or email already exists
        if get_user_by_username(db, username):
            st.error(f"Username '{username}' already exists")
            return None
            
        if get_user_by_email(db, email):
            st.error(f"Email '{email}' already exists")
            return None
            
        # Create the user
        user = db_create_user(db, username, email, password, full_name, role)
        
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        return None
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return None

def add_user(username: str, email: str, password: str, full_name: str = None, role: str = "User") -> bool:
    """
    Alias for create_user, returns boolean success instead of user data
    
    Args:
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: User's full name (optional)
        role: User role (default: "User")
        
    Returns:
        bool: True if user was created, False otherwise
    """
    user = create_user(username, email, password, full_name, role)
    return user is not None

def get_users() -> List[Dict]:
    """
    Get a list of all users
    
    Returns:
        List[Dict]: List of user data dictionaries
    """
    try:
        db = get_db_session()
        users = db.query(User).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
            for user in users
        ]
    except Exception as e:
        st.error(f"Error getting users: {str(e)}")
        return []

def login_user(username_or_email: str, password: str = None) -> bool:
    """
    Log in the user by setting session state
    
    Args:
        username_or_email: The username or email to log in
        password: The password to check (if provided)
        
    Returns:
        bool: True if login was successful, False otherwise
    """
    try:
        db = get_db_session()
        
        # If password is provided, verify credentials
        if password:
            # Try to find user by email first
            user = get_user_by_email(db, username_or_email)
            
            # If not found by email, try username
            if not user:
                user = get_user_by_username(db, username_or_email)
                
            # Verify credentials
            if user and db_verify_password(user.hashed_password, password):
                # Set session state
                st.session_state['authenticated'] = True
                st.session_state['username'] = user.username
                st.session_state['user_id'] = user.id
                st.session_state['user_role'] = user.role
                st.session_state['user_full_name'] = user.full_name or ""
                return True
            else:
                return False
        else:
            # Direct login by username (used internally)
            user = get_user_by_username(db, username_or_email)
            
            if user:
                st.session_state['authenticated'] = True
                st.session_state['username'] = user.username
                st.session_state['user_id'] = user.id
                st.session_state['user_role'] = user.role
                st.session_state['user_full_name'] = user.full_name or ""
                return True
            else:
                st.error(f"User {username_or_email} not found")
                return False
    except Exception as e:
        st.error(f"Error logging in: {str(e)}")
        return False

def logout_user() -> None:
    """Log out the user by clearing session state"""
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['user_id'] = None
    st.session_state['user_role'] = None
    st.session_state['user_full_name'] = None

def is_authenticated() -> bool:
    """Check if a user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_username() -> Optional[str]:
    """Get the username of the currently logged in user"""
    return st.session_state.get('username', None)

def get_current_user() -> Optional[Dict]:
    """
    Get the current logged in user data
    
    Returns:
        Optional[Dict]: User data dict if logged in, None otherwise
    """
    if not is_authenticated():
        return None
        
    username = get_current_username()
    if not username:
        return None
        
    try:
        db = get_db_session()
        user = get_user_by_username(db, username)
        
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        return None
    except Exception as e:
        st.error(f"Error getting current user: {str(e)}")
        return None

def get_user_id() -> Optional[int]:
    """Get the user ID of the currently logged in user"""
    return st.session_state.get('user_id', None)

def get_user_role() -> Optional[str]:
    """Get the role of the currently logged in user"""
    return st.session_state.get('user_role', None)

def initialize_session_state() -> None:
    """Initialize the session state with default values"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = None
    if 'user_full_name' not in st.session_state:
        st.session_state['user_full_name'] = None
    if 'current_data' not in st.session_state:
        st.session_state['current_data'] = None
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = True