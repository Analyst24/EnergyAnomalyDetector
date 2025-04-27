import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from streamlit_extras.colored_header import colored_header

from utils.auth import is_authenticated, get_users, add_user
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Settings | Energy Anomaly Detection",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Check authentication
if not is_authenticated():
    st.warning("Please login to access this page")
    st.stop()

def main():
    st.title("⚡ System Settings")
    
    colored_header(
        label="Configuration",
        description="Configure system settings and user preferences",
        color_name="blue-70"
    )
    
    # Create tabs for different settings
    tab1, tab2, tab3, tab4 = st.tabs(["General Settings", "User Management", "Algorithm Settings", "System Information"])
    
    # Tab 1: General Settings
    with tab1:
        st.markdown("### General Settings")
        
        # Theme settings
        st.markdown("#### Theme Settings")
        theme_option = st.selectbox(
            "Application Theme",
            ["Dark (Default)", "Light", "Custom"],
            index=0
        )
        
        if theme_option == "Custom":
            col1, col2 = st.columns(2)
            
            with col1:
                primary_color = st.color_picker("Primary Color", "#4b7bec")
                background_color = st.color_picker("Background Color", "#1e272e")
            
            with col2:
                secondary_bg_color = st.color_picker("Secondary Background", "#2d3436")
                text_color = st.color_picker("Text Color", "#ffffff")
        
        # Visualization settings
        st.markdown("#### Visualization Settings")
        
        default_chart_lib = st.selectbox(
            "Default Chart Library",
            ["Plotly", "Seaborn", "Matplotlib"],
            index=0
        )
        
        chart_animation = st.checkbox("Enable Chart Animations", value=True)
        
        color_palette = st.selectbox(
            "Chart Color Palette",
            ["Blues", "Reds", "Greens", "Viridis", "Magma", "Cividis"],
            index=0
        )
        
        # Notification settings
        st.markdown("#### Notification Settings")
        
        email_notifications = st.checkbox("Enable Email Notifications", value=False)
        
        if email_notifications:
            email_address = st.text_input("Email Address")
            notification_frequency = st.selectbox(
                "Notification Frequency",
                ["Real-time", "Daily", "Weekly"],
                index=1
            )
        
        # Save button
        if st.button("Save General Settings"):
            st.success("Settings saved successfully!")
    
    # Tab 2: User Management
    with tab2:
        st.markdown("### User Management")
        
        # Display existing users
        st.markdown("#### Current Users")
        
        users = get_users()
        
        if users:
            user_list = []
            for username, user_data in users.items():
                user_list.append({
                    "Username": username,
                    "Name": user_data.get("name", ""),
                    "Role": user_data.get("role", "User")
                })
            
            user_df = pd.DataFrame(user_list)
            st.dataframe(user_df, use_container_width=True)
        else:
            st.info("No users found in the system.")
        
        # Add new user
        st.markdown("#### Add New User")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_name = st.text_input("Full Name")
            new_role = st.selectbox("Role", ["Admin", "User", "Viewer"])
            
            submit_button = st.form_submit_button("Add User")
            
            if submit_button:
                if not new_username or not new_password:
                    st.error("Username and password are required")
                elif new_username in users:
                    st.error(f"User '{new_username}' already exists")
                else:
                    # Add the new user
                    add_user(new_username, new_password, new_name, new_role)
                    st.success(f"User '{new_username}' added successfully!")
    
    # Tab 3: Algorithm Settings
    with tab3:
        st.markdown("### Algorithm Settings")
        
        # Default algorithm
        st.markdown("#### Default Algorithm")
        
        default_algorithm = st.selectbox(
            "Default Anomaly Detection Algorithm",
            ["Isolation Forest", "AutoEncoder", "K-Means"],
            index=0
        )
        
        # Isolation Forest settings
        st.markdown("#### Isolation Forest Settings")
        
        isolation_forest_contamination = st.slider(
            "Default Contamination",
            min_value=0.01,
            max_value=0.2,
            value=0.05,
            step=0.01
        )
        
        isolation_forest_estimators = st.slider(
            "Default Number of Estimators",
            min_value=50,
            max_value=500,
            value=100,
            step=10
        )
        
        # AutoEncoder settings
        st.markdown("#### AutoEncoder Settings")
        
        autoencoder_threshold = st.slider(
            "Default Anomaly Threshold Percentile",
            min_value=90,
            max_value=99,
            value=95,
            step=1
        )
        
        autoencoder_epochs = st.slider(
            "Default Training Epochs",
            min_value=10,
            max_value=100,
            value=50,
            step=5
        )
        
        # K-Means settings
        st.markdown("#### K-Means Settings")
        
        kmeans_clusters = st.slider(
            "Default Number of Clusters",
            min_value=2,
            max_value=20,
            value=5,
            step=1
        )
        
        kmeans_threshold = st.slider(
            "Default Anomaly Threshold Percentile",
            min_value=90,
            max_value=99,
            value=95,
            step=1
        )
        
        # Save button
        if st.button("Save Algorithm Settings"):
            # In a real app, this would save to a configuration file or database
            algorithm_settings = {
                "default_algorithm": default_algorithm,
                "isolation_forest": {
                    "contamination": isolation_forest_contamination,
                    "n_estimators": isolation_forest_estimators
                },
                "autoencoder": {
                    "threshold_percent": autoencoder_threshold,
                    "epochs": autoencoder_epochs
                },
                "kmeans": {
                    "n_clusters": kmeans_clusters,
                    "threshold_percent": kmeans_threshold
                }
            }
            
            # Display the settings as JSON (in a real app, this would be saved)
            st.json(algorithm_settings)
            st.success("Algorithm settings saved successfully!")
    
    # Tab 4: System Information
    with tab4:
        st.markdown("### System Information")
        
        # System overview
        st.markdown("#### System Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("System Version", "1.0.0")
        
        with col2:
            st.metric("Last Updated", "2023-07-30")
        
        with col3:
            st.metric("Database Status", "Connected")
        
        # System health metrics (demo values)
        st.markdown("#### System Health")
        
        health_data = pd.DataFrame({
            'Metric': ['CPU Usage', 'Memory Usage', 'Disk Space', 'Database Connections', 'API Response Time'],
            'Value': ['15%', '32%', '47%', '3/20', '125ms'],
            'Status': ['Good', 'Good', 'Good', 'Good', 'Good']
        })
        
        st.dataframe(health_data, use_container_width=True)
        
        # System capabilities
        st.markdown("#### Installed Components")
        
        components = {
            'scikit-learn': '1.2.2',
            'TensorFlow': '2.12.0',
            'Plotly': '5.14.1',
            'Pandas': '2.0.1',
            'NumPy': '1.24.3',
            'Streamlit': '1.22.0'
        }
        
        st.json(components)
        
        # Logs (placeholder)
        st.markdown("#### System Logs")
        
        log_entries = [
            {'timestamp': '2023-07-30 10:15:23', 'level': 'INFO', 'message': 'System started successfully'},
            {'timestamp': '2023-07-30 10:17:45', 'level': 'INFO', 'message': 'User admin logged in'},
            {'timestamp': '2023-07-30 11:05:12', 'level': 'INFO', 'message': 'Anomaly detection completed (Isolation Forest)'},
            {'timestamp': '2023-07-30 11:32:08', 'level': 'WARNING', 'message': 'High memory usage detected (75%)'},
            {'timestamp': '2023-07-30 12:45:23', 'level': 'INFO', 'message': 'Database backup completed'}
        ]
        
        log_df = pd.DataFrame(log_entries)
        st.dataframe(log_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
