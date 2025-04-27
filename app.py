import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
import time
import base64
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header
import streamlit.components.v1

# Ensure path is set correctly for imports to work in any environment
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from utils.auth import (
    login_user, create_user, verify_password, get_users, 
    is_authenticated, add_user, logout_user, get_user_role,
    get_current_user, get_user_id
)
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Energy Anomaly Detection System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto"
)

# This hides the default sidebar menu and "init" item from the beginning
st.markdown("""
<style>
/* Hide the default menu and make space for our custom menu */
section[data-testid="stSidebar"] > div.css-6qob1r {
    visibility: hidden !important;
    height: 0 !important;
    position: absolute !important;
    overflow: hidden !important;
}

/* Hide any "init" entries */
div[data-testid="stSidebarNav"] ul > li:first-child,
div[data-testid="stSidebarNav"] ul > li:has(a[href="/"]),
section[data-testid="stSidebar"] div > ul > li:has(a[href="/"]) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    position: absolute !important;
}
</style>
""", unsafe_allow_html=True)

# Apply custom styles
apply_custom_styles()

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = None
if 'selected_algorithm' not in st.session_state:
    st.session_state.selected_algorithm = "Isolation Forest"
if 'model_metrics' not in st.session_state:
    st.session_state.model_metrics = None
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

# Create a sample users dictionary if it doesn't exist (for backwards compatibility)
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin': {
            'password': 'admin123',
            'name': 'Administrator',
            'email': 'admin@example.com'
        },
        'demo': {
            'password': 'demo123',
            'name': 'Demo User',
            'email': 'demo@example.com'
        }
    }

# Initialize database if not already done
if not st.session_state.db_initialized:
    try:
        from database.connection import test_connection
        from init_database import initialize_database, migrate_session_users
        
        # Test database connection
        if test_connection():
            # Initialize database tables and default data
            initialize_database()
            
            # Migrate users from session state to database
            migrate_session_users()
            
            st.session_state.db_initialized = True
    except ImportError:
        st.warning("Database modules not available, running in session-only mode")
        st.session_state.db_initialized = False
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        st.session_state.db_initialized = False

# Function to display a background image
def add_bg_image():
    # Create a dark gradient background instead of loading an image
    bg_style = """
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        background-size: cover;
        background-position: center;
    }
    .auth-container {
        background-color: rgba(45, 52, 54, 0.85);
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        max-width: 450px;
        margin: 10vh auto;
    }
    .auth-header {
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .auth-button {
        width: 100%;
        margin-top: 15px;
    }
    .auth-link {
        text-align: center;
        margin-top: 20px;
        color: #4b7bec;
        cursor: pointer;
    }
    .auth-link:hover {
        text-decoration: underline;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# Function to convert image to base64
def image_to_base64(image):
    import io
    import base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Login page
def login_page():
    # Hide the sidebar completely
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none}
    section[data-testid="stSidebar"] {display: none}
    .stApp header {display: none}
    </style>
    """, unsafe_allow_html=True)
    
    # Add background image
    add_bg_image()
    
    # Add container for login form
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-header">⚡ Energy Anomaly Detection</h1>', unsafe_allow_html=True)
    
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    login_btn = st.button("Login", key="login_button")
    
    if login_btn:
        # Attempt to log in user with email and password
        if login_user(email, password):
            st.success(f"Welcome back, {st.session_state.username}!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid email or password. Please try again or sign up for a new account.")
    
    # Link to sign up page
    st.markdown('<div class="auth-link" id="signup-link">Don\'t have an account? Sign up</div>', unsafe_allow_html=True)
    
    # JavaScript to handle the sign up link click
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelector('#signup-link').addEventListener('click', function() {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: true}, '*');
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Check if signup link was clicked
    if st.button("Sign Up", key="goto_signup", help="Create a new account"):
        st.session_state.show_signup = True
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Get Started page
def get_started_page():
    st.title("⚡ Energy Anomaly Detection System")
    
    # Animated energy consumption visual
    st.markdown("## Real-time Energy Monitoring")
    
    # Generate sample data for an attractive visualization
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='h')  # Using 'h' instead of 'H' as per deprecation warning
    base_consumption = 100 + 30 * np.sin(np.linspace(0, 4*np.pi, 100))
    noise = np.random.normal(0, 5, 100)
    anomalies = np.zeros(100)
    anomalies[[20, 45, 68, 90]] = [40, 35, -30, 50]
    
    energy_data = pd.DataFrame({
        'Timestamp': dates,
        'Consumption': base_consumption + noise + anomalies,
        'IsAnomaly': [1 if x != 0 else 0 for x in anomalies]
    })
    
    # Create animated chart
    fig = px.line(energy_data, x='Timestamp', y='Consumption',
                title='Energy Consumption Pattern',
                labels={'Consumption': 'Energy Usage (kWh)', 'Timestamp': 'Time'},
                color_discrete_sequence=['#4b7bec'])
    
    # Add anomaly points
    anomaly_data = energy_data[energy_data['IsAnomaly'] == 1]
    fig.add_trace(go.Scatter(
        x=anomaly_data['Timestamp'],
        y=anomaly_data['Consumption'],
        mode='markers',
        marker=dict(size=12, color='red', symbol='circle'),
        name='Detected Anomalies'
    ))
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Features overview with icons
    st.markdown("## System Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Data Visualization")
        st.markdown("Interactive dashboards showing energy consumption patterns and anomalies.")
    
    with col2:
        st.markdown("### 🔍 Anomaly Detection")
        st.markdown("Advanced ML algorithms to identify unusual energy consumption patterns.")
    
    with col3:
        st.markdown("### 💡 Smart Recommendations")
        st.markdown("Get actionable insights to improve energy efficiency.")
    
    # Call-to-action
    st.markdown("## Ready to get started?")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Go to Dashboard", key="goto_dashboard", use_container_width=True):
            # Redirect to the Home page
            st.session_state.current_page = "Home"
            st.info("Please use the sidebar to navigate to Home or other pages.")
            time.sleep(1)

# Sign up page
def signup_page():
    # Hide the sidebar completely
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none}
    section[data-testid="stSidebar"] {display: none}
    .stApp header {display: none}
    </style>
    """, unsafe_allow_html=True)
    
    # Add background image
    add_bg_image()
    
    # Add container for signup form
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-header">⚡ Create Account</h1>', unsafe_allow_html=True)
    
    full_name = st.text_input("Full Name", key="signup_name")
    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    
    signup_btn = st.button("Sign Up", key="signup_button")
    
    if signup_btn:
        # Validate form
        if not (full_name and email and username and password and confirm_password):
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Create the new user with database support
            try:
                if create_user(username, email, password, full_name, role="User"):
                    st.success("Account created successfully! You can now log in.")
                    st.session_state.show_signup = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Username or email already exists. Please choose different ones.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")
    
    # Link to login page
    st.markdown('<div class="auth-link" id="login-link">Already have an account? Log In</div>', unsafe_allow_html=True)
    
    # Button to go back to login
    if st.button("Back to Login", key="goto_login"):
        st.session_state.show_signup = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main app logic
def main():
    if not st.session_state.authenticated:
        if st.session_state.show_signup:
            signup_page()
        else:
            login_page()
    else:
        # Create sidebar
        with st.sidebar:
            # Professional sidebar with user info section
            # User profile section
            user_col1, user_col2 = st.columns([1, 3])
            
            with user_col1:
                # User avatar/icon
                st.markdown("""
                <div style="width:50px;height:50px;border-radius:50%;background:linear-gradient(135deg, #4b7bec 0%, #3867d6 100%);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;font-weight:bold;">
                    {}
                </div>
                """.format(st.session_state.username[0].upper()), unsafe_allow_html=True)
                
            with user_col2:
                st.markdown(f"### {st.session_state.username}")
                st.markdown("<span style='color:#a5b1c2;font-size:14px;'>Energy Analyst</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Professional sidebar styling
            st.markdown("""
            <style>
            /* Hide default elements */
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            .stDeployButton {display: none !important;}
            
            /* Hide any default navigation including "init" */
            div[data-testid="stSidebarNav"] {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                position: absolute !important;
            }
            
            /* Professional menu styling */
            .sidebar-menu {
                margin-bottom: 20px;
            }
            
            .menu-title {
                font-size: 14px;
                color: #a5b1c2;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
                font-weight: 500;
            }
            
            .menu-item {
                display: flex;
                align-items: center;
                padding: 8px 12px;
                margin: 4px 0;
                border-radius: 5px;
                color: #f0f0f0;
                text-decoration: none;
                transition: background-color 0.2s;
                cursor: pointer;
            }
            
            .menu-item:hover {
                background-color: rgba(75, 123, 236, 0.2);
            }
            
            .menu-item.active {
                background-color: rgba(75, 123, 236, 0.3);
                font-weight: 500;
            }
            
            .menu-icon {
                margin-right: 10px;
                width: 20px;
                text-align: center;
                font-size: 18px;
            }
            
            .logout-button {
                margin-top: 30px;
                text-align: center;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Main navigation menu
            st.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
            st.markdown('<div class="menu-title">MAIN NAVIGATION</div>', unsafe_allow_html=True)
            
            # Navigation menu items
            menu_items = [
                {"name": "Dashboard", "icon": "📊", "url": "/pages/02_Dashboard.py"},
                {"name": "Upload Data", "icon": "📤", "url": "/pages/03_Upload_Data.py"},
                {"name": "Run Detection", "icon": "🔍", "url": "/pages/04_Run_Detection.py"}
            ]
            
            for item in menu_items:
                st.markdown(f"""
                <a href="{item['url']}" target="_self" class="menu-item">
                    <div class="menu-icon">{item['icon']}</div>
                    <div>{item['name']}</div>
                </a>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analysis & Reports section
            st.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
            st.markdown('<div class="menu-title">ANALYSIS & REPORTS</div>', unsafe_allow_html=True)
            
            # Analysis menu items
            analysis_items = [
                {"name": "Results", "icon": "📈", "url": "/pages/05_Results.py"},
                {"name": "Model Insights", "icon": "💡", "url": "/pages/06_Model_Insights.py"},
                {"name": "Recommendations", "icon": "📋", "url": "/pages/07_Recommendations.py"}
            ]
            
            for item in analysis_items:
                st.markdown(f"""
                <a href="{item['url']}" target="_self" class="menu-item">
                    <div class="menu-icon">{item['icon']}</div>
                    <div>{item['name']}</div>
                </a>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # System section
            st.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
            st.markdown('<div class="menu-title">SYSTEM</div>', unsafe_allow_html=True)
            
            # System menu items
            st.markdown(f"""
            <a href="/pages/08_Settings.py" target="_self" class="menu-item">
                <div class="menu-icon">⚙️</div>
                <div>Settings</div>
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Logout button (using Streamlit's button for functionality)
            st.markdown('<div class="logout-button">', unsafe_allow_html=True)
            if st.button("📤 Logout", use_container_width=True):
                logout_user()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
                
            # Force hide the default sidebar nav via JavaScript
            js_code = """
            <script>
            function hideInitAndDefaultNav() {
                // Hide the default Streamlit sidebar navigation
                const sidebarNavs = document.querySelectorAll('[data-testid="stSidebarNav"]');
                if (sidebarNavs.length > 0) {
                    sidebarNavs.forEach(nav => {
                        nav.style.display = 'none';
                        nav.style.visibility = 'hidden';
                        nav.style.opacity = '0';
                        nav.style.height = '0';
                        nav.style.position = 'absolute';
                        nav.setAttribute('aria-hidden', 'true');
                    });
                }
            }
            
            // Run immediately and periodically
            hideInitAndDefaultNav();
            setInterval(hideInitAndDefaultNav, 200);
            
            // Monitor DOM changes
            const observer = new MutationObserver(hideInitAndDefaultNav);
            observer.observe(document.body, { childList: true, subtree: true });
            </script>
            """
            st.components.v1.html(js_code, height=0)
        
        # Main content
        get_started_page()
    
    # Only show footer when authenticated
    if st.session_state.authenticated:
        st.markdown("---")
        st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
