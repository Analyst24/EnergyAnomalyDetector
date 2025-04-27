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
from streamlit.runtime.scriptrunner import add_script_run_ctx
try:
    # For Streamlit >= 1.18.0
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    def switch_page(page_name):
        from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
        from streamlit.source_util import get_pages
        
        current_page = None
        ctx = get_script_run_ctx()
        if ctx:
            current_page = ctx.page_script_hash
        
        pages = get_pages("streamlit_app.py")
        
        for page_hash, page_info in pages.items():
            if page_info["page_name"] == page_name:
                st.session_state["STREAMLIT_REDIRECT"] = {"page_hash": page_hash, "page_name": page_name}
                st.rerun()
                break
except ImportError:
    # For Streamlit < 1.18.0
    def switch_page(page_name):
        from streamlit.runtime import Runtime
        runtime = Runtime.instance()
        root_script_run_ctx = runtime._active_script_run_ctx
        if root_script_run_ctx is None:
            raise RuntimeError("No script is currently running")
        
        st.session_state["STREAMLIT_REDIRECT"] = page_name
        st.rerun()

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
    
    /* Moving energy background animation styles */
    .stApp {
        background-color: #040f2d !important;
        background-image: none !important;
        position: relative;
        overflow: hidden;
    }
    
    .energy-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        background: linear-gradient(135deg, 
                    rgba(7, 15, 40, 0.97),
                    rgba(16, 42, 94, 0.9),
                    rgba(10, 50, 110, 0.9),
                    rgba(5, 25, 55, 0.95));
        background-size: 400% 400%;
        animation: flow 15s ease infinite;
    }
    
    @keyframes flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Grid overlay for smart grid visualization */
    .grid-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background-image: 
            linear-gradient(rgba(40, 130, 220, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(40, 130, 220, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Energy flow lines */
    .flow-line {
        position: absolute;
        height: 2px;
        background: linear-gradient(to right, 
                    rgba(0, 212, 255, 0), 
                    rgba(0, 212, 255, 0.5), 
                    rgba(0, 212, 255, 0));
        animation: flow-animation linear infinite;
    }
    
    @keyframes flow-animation {
        0% { transform: translateX(-100%); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateX(100vw); opacity: 0; }
    }
    
    /* Energy nodes */
    .energy-node {
        position: absolute;
        width: 4px;
        height: 4px;
        background-color: rgba(40, 130, 220, 0.7);
        border-radius: 50%;
        box-shadow: 0 0 8px 2px rgba(40, 130, 220, 0.4);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.4); opacity: 1; }
        100% { transform: scale(1); opacity: 0.7; }
    }
    
    .auth-container {
        background-color: rgba(15, 25, 55, 0.8);
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
        max-width: 450px;
        margin: 10vh auto;
        border: 1px solid rgba(72, 126, 176, 0.2);
        backdrop-filter: blur(8px);
    }
    
    .auth-header {
        color: white;
        text-align: center;
        margin-bottom: 25px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .auth-button {
        width: 100%;
        margin-top: 15px;
        background-color: #3498db;
        border: none;
        color: white;
        padding: 10px;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    
    .auth-button:hover {
        background-color: #2980b9;
    }
    
    .auth-link {
        text-align: center;
        margin-top: 20px;
        color: #5ca1e1;
        cursor: pointer;
    }
    
    .auth-link:hover {
        text-decoration: underline;
        color: #3498db;
    }
    
    .stButton button {
        background-color: #3498db !important;
        color: white !important;
        border: none !important;
        padding: 10px !important;
        font-weight: 500 !important;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #2980b9 !important;
    }
    
    .stTextInput label, .stTextInput label p, .stPasswordInput label {
        color: #e0e0e0 !important;
    }
    
    .stTextInput input, .stPasswordInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(72, 126, 176, 0.3) !important;
    }
    
    .stTextInput input:focus, .stPasswordInput input:focus {
        border: 1px solid rgba(72, 126, 176, 0.8) !important;
        box-shadow: 0 0 0 1px rgba(72, 126, 176, 0.3) !important;
    }
    </style>
    
    <!-- Animated energy background elements -->
    <div class="energy-background"></div>
    <div class="grid-overlay"></div>
    <div id="energy-animation-container"></div>
    
    <script>
    // Create animated energy flow lines and nodes
    document.addEventListener('DOMContentLoaded', function() {
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.zIndex = '-1';
        container.style.overflow = 'hidden';
        container.id = 'energy-animation-container';
        document.body.appendChild(container);
        
        // Create flow lines
        for (let i = 0; i < 15; i++) {
            createFlowLine(container);
        }
        
        // Create energy nodes
        for (let i = 0; i < 30; i++) {
            createEnergyNode(container);
        }
        
        setInterval(() => {
            if (Math.random() > 0.7) {
                createFlowLine(container);
            }
        }, 2000);
    });
    
    function createFlowLine(container) {
        const line = document.createElement('div');
        line.className = 'flow-line';
        
        // Random position and properties
        const yPos = Math.random() * 100;
        const width = Math.random() * 100 + 50;
        const duration = Math.random() * 5 + 5;
        const opacity = Math.random() * 0.5 + 0.2;
        
        line.style.top = `${yPos}vh`;
        line.style.width = `${width}px`;
        line.style.opacity = opacity;
        line.style.animationDuration = `${duration}s`;
        
        container.appendChild(line);
        
        // Remove after animation completes
        setTimeout(() => {
            line.remove();
        }, duration * 1000);
    }
    
    function createEnergyNode(container) {
        const node = document.createElement('div');
        node.className = 'energy-node';
        
        // Random position and properties
        const xPos = Math.random() * 100;
        const yPos = Math.random() * 100;
        const duration = Math.random() * 3 + 2;
        const delay = Math.random() * 2;
        const size = Math.random() * 3 + 2;
        
        node.style.left = `${xPos}vw`;
        node.style.top = `${yPos}vh`;
        node.style.width = `${size}px`;
        node.style.height = `${size}px`;
        node.style.animationDuration = `${duration}s`;
        node.style.animationDelay = `${delay}s`;
        
        container.appendChild(node);
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Add container for login form with animated energy background
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
    
    /* Moving energy background animation styles */
    .stApp {
        background-color: #040f2d !important;
        background-image: none !important;
        position: relative;
        overflow: hidden;
    }
    
    .energy-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        background: linear-gradient(135deg, 
                    rgba(7, 15, 40, 0.97),
                    rgba(16, 42, 94, 0.9),
                    rgba(10, 50, 110, 0.9),
                    rgba(5, 25, 55, 0.95));
        background-size: 400% 400%;
        animation: flow 15s ease infinite;
    }
    
    @keyframes flow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Grid overlay for smart grid visualization */
    .grid-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background-image: 
            linear-gradient(rgba(40, 130, 220, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(40, 130, 220, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Energy flow lines */
    .flow-line {
        position: absolute;
        height: 2px;
        background: linear-gradient(to right, 
                    rgba(0, 212, 255, 0), 
                    rgba(0, 212, 255, 0.5), 
                    rgba(0, 212, 255, 0));
        animation: flow-animation linear infinite;
    }
    
    @keyframes flow-animation {
        0% { transform: translateX(-100%); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateX(100vw); opacity: 0; }
    }
    
    /* Energy nodes */
    .energy-node {
        position: absolute;
        width: 4px;
        height: 4px;
        background-color: rgba(40, 130, 220, 0.7);
        border-radius: 50%;
        box-shadow: 0 0 8px 2px rgba(40, 130, 220, 0.4);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.4); opacity: 1; }
        100% { transform: scale(1); opacity: 0.7; }
    }
    
    .auth-container {
        background-color: rgba(15, 25, 55, 0.8);
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
        max-width: 450px;
        margin: 5vh auto;
        border: 1px solid rgba(72, 126, 176, 0.2);
        backdrop-filter: blur(8px);
    }
    
    .auth-header {
        color: white;
        text-align: center;
        margin-bottom: 25px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .auth-link {
        text-align: center;
        margin-top: 20px;
        color: #5ca1e1;
        cursor: pointer;
    }
    
    .auth-link:hover {
        text-decoration: underline;
        color: #3498db;
    }
    
    .stButton button {
        background-color: #3498db !important;
        color: white !important;
        border: none !important;
        padding: 10px !important;
        font-weight: 500 !important;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #2980b9 !important;
    }
    
    .stTextInput label, .stTextInput label p, .stPasswordInput label {
        color: #e0e0e0 !important;
    }
    
    .stTextInput input, .stPasswordInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(72, 126, 176, 0.3) !important;
    }
    
    .stTextInput input:focus, .stPasswordInput input:focus {
        border: 1px solid rgba(72, 126, 176, 0.8) !important;
        box-shadow: 0 0 0 1px rgba(72, 126, 176, 0.3) !important;
    }
    
    /* Signup title */
    .signup-title {
        color: white;
        text-align: center;
        margin-bottom: 20px;
        padding-top: 40px;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
    }
    </style>
    
    <!-- Animated energy background elements -->
    <div class="energy-background"></div>
    <div class="grid-overlay"></div>
    <div id="energy-animation-container-signup"></div>
    
    <script>
    // Create animated energy flow lines and nodes
    document.addEventListener('DOMContentLoaded', function() {
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.zIndex = '-1';
        container.style.overflow = 'hidden';
        container.id = 'energy-animation-container-signup';
        document.body.appendChild(container);
        
        // Create flow lines
        for (let i = 0; i < 15; i++) {
            createFlowLine(container);
        }
        
        // Create energy nodes
        for (let i = 0; i < 30; i++) {
            createEnergyNode(container);
        }
        
        setInterval(() => {
            if (Math.random() > 0.7) {
                createFlowLine(container);
            }
        }, 2000);
    });
    
    function createFlowLine(container) {
        const line = document.createElement('div');
        line.className = 'flow-line';
        
        // Random position and properties
        const yPos = Math.random() * 100;
        const width = Math.random() * 100 + 50;
        const duration = Math.random() * 5 + 5;
        const opacity = Math.random() * 0.5 + 0.2;
        
        line.style.top = `${yPos}vh`;
        line.style.width = `${width}px`;
        line.style.opacity = opacity;
        line.style.animationDuration = `${duration}s`;
        
        container.appendChild(line);
        
        // Remove after animation completes
        setTimeout(() => {
            line.remove();
        }, duration * 1000);
    }
    
    function createEnergyNode(container) {
        const node = document.createElement('div');
        node.className = 'energy-node';
        
        // Random position and properties
        const xPos = Math.random() * 100;
        const yPos = Math.random() * 100;
        const duration = Math.random() * 3 + 2;
        const delay = Math.random() * 2;
        const size = Math.random() * 3 + 2;
        
        node.style.left = `${xPos}vw`;
        node.style.top = `${yPos}vh`;
        node.style.width = `${size}px`;
        node.style.height = `${size}px`;
        node.style.animationDuration = `${duration}s`;
        node.style.animationDelay = `${delay}s`;
        
        container.appendChild(node);
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Page title with animated background
    st.markdown("<h1 class='signup-title'>⚡ Energy Anomaly Detection</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='signup-title' style='font-size: 1.5rem;'>Create Your Account</h3>", unsafe_allow_html=True)
    
    # Add container for signup form
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Form fields with placeholders
    full_name = st.text_input("Full Name", key="signup_name", placeholder="Enter your full name")
    email = st.text_input("Email", key="signup_email", placeholder="Enter your email address")
    username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
    password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password", placeholder="Confirm your password")
    
    # Create account button
    signup_btn = st.button("Create Account", key="signup_button")
    
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
        # Basic sidebar
        with st.sidebar:
            # Simple welcome text
            st.write(f"Welcome, {st.session_state.username}")
            st.write("---")
            
            # Logout button
            if st.button("Logout"):
                logout_user()
                st.rerun()
                
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
