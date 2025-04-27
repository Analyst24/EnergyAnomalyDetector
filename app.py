import streamlit as st
import os
import pandas as pd
import numpy as np
import time
import base64
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page

from utils.auth import login_user, create_user, verify_password, get_users, is_authenticated
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Energy Anomaly Detection System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto"
)

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

# Create a sample users dictionary if it doesn't exist
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin': {
            'password': 'admin123',
            'name': 'Administrator'
        },
        'demo': {
            'password': 'demo123',
            'name': 'Demo User'
        }
    }

# Login page
def login_page():
    st.title("⚡ Energy Anomaly Detection System")
    
    # Two columns layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        login_btn = st.button("Login")
        
        if login_btn:
            if username in st.session_state.users and st.session_state.users[username]['password'] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome back, {st.session_state.users[username]['name']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with col2:
        # Energy-related animation/visualization
        st.markdown("### Energy Monitoring System")
        
        # Sample energy consumption data for animation
        dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
        energy_consumption = np.random.normal(100, 15, 30)
        energy_df = pd.DataFrame({
            'Date': dates,
            'Consumption': energy_consumption
        })
        
        # Create an animated line chart
        fig = px.line(energy_df, x='Date', y='Consumption',
                      title='Real-time Energy Consumption',
                      labels={'Consumption': 'Energy Usage (kWh)', 'Date': 'Time'},
                      color_discrete_sequence=['#4b7bec'])
        
        # Add anomaly points for visual effect
        anomaly_indices = [5, 12, 22]
        anomaly_dates = energy_df.iloc[anomaly_indices]['Date']
        anomaly_values = energy_df.iloc[anomaly_indices]['Consumption']
        
        fig.add_trace(go.Scatter(
            x=anomaly_dates,
            y=anomaly_values,
            mode='markers',
            marker=dict(size=12, color='red', symbol='circle'),
            name='Potential Anomalies'
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
        
        st.info("This system helps detect energy consumption anomalies using advanced machine learning algorithms.")

# Get Started page
def get_started_page():
    st.title("⚡ Energy Anomaly Detection System")
    
    # Animated energy consumption visual
    st.markdown("## Real-time Energy Monitoring")
    
    # Generate sample data for an attractive visualization
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
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
            switch_page("Home")

# Main app logic
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        # Create sidebar
        with st.sidebar:
            st.markdown(f"### Welcome, {st.session_state.username}")
            st.markdown("---")
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.rerun()
        
        # Main content
        get_started_page()
    
    # Footer with copyright
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
