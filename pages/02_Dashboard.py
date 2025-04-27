import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from streamlit_extras.colored_header import colored_header

# Import handling for both direct and package imports
import sys
import os

# Determine if the script is being run directly
if __name__ == "__main__" or os.path.basename(sys.argv[0]) == "pages":
    # If running directly, add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from the project packages
from utils.auth import is_authenticated
from utils.visualization import plot_consumption_overview, plot_anomaly_distribution
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Dashboard | Energy Anomaly Detection",
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

# Generate sample data if needed (in a real app, this would come from a database)
def generate_sample_data():
    if st.session_state.current_data is None:
        # Create date range for the past 30 days
        dates = pd.date_range(end=datetime.now(), periods=720, freq='H')
        
        # Generate base consumption with daily and weekly patterns
        hours = np.array([d.hour for d in dates])
        weekdays = np.array([d.weekday() for d in dates])
        
        # Daily pattern: higher during work hours (8am-6pm)
        daily_pattern = 20 * np.sin(np.pi * hours / 24) + 20
        
        # Weekly pattern: lower on weekends
        weekly_factor = np.where(weekdays >= 5, 0.8, 1.0)
        
        # Base consumption with patterns
        base = 100 + daily_pattern * weekly_factor
        
        # Add random noise
        noise = np.random.normal(0, 5, size=len(dates))
        
        # Add some anomalies
        anomalies = np.zeros(len(dates))
        anomaly_indices = np.random.choice(len(dates), size=15, replace=False)
        anomalies[anomaly_indices] = np.random.normal(0, 30, size=15)
        
        # Prepare the dataset
        energy_data = pd.DataFrame({
            'timestamp': dates,
            'consumption': base + noise + anomalies,
            'temperature': 20 + 10 * np.sin(np.pi * hours / 24) + np.random.normal(0, 2, size=len(dates)),
            'humidity': 50 + 10 * np.sin(np.pi * hours / 12) + np.random.normal(0, 5, size=len(dates)),
            'occupancy': np.where((hours >= 8) & (hours <= 18) & (weekdays < 5), 
                                 np.random.randint(10, 50, size=len(dates)), 
                                 np.random.randint(0, 10, size=len(dates)))
        })
        
        # Mark anomalies (for demonstration)
        energy_data['is_anomaly'] = 0
        energy_data.loc[anomaly_indices, 'is_anomaly'] = 1
        
        # Store the data in session state
        st.session_state.current_data = energy_data
    
    return st.session_state.current_data

def main():
    # Title
    st.title("⚡ Energy Dashboard")
    
    colored_header(
        label="Real-time Energy Monitoring",
        description="Visual insights into energy consumption patterns and anomalies",
        color_name="blue-70"
    )
    
    # Get data
    data = generate_sample_data()
    
    # Filters row
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Time range filter
            time_options = ["Last 24 hours", "Last 7 days", "Last 30 days", "All data"]
            selected_time = st.selectbox("Time Range", time_options, index=2)
            
            # Filter data based on selection
            if selected_time == "Last 24 hours":
                filtered_data = data[data['timestamp'] >= (data['timestamp'].max() - pd.Timedelta(days=1))]
            elif selected_time == "Last 7 days":
                filtered_data = data[data['timestamp'] >= (data['timestamp'].max() - pd.Timedelta(days=7))]
            elif selected_time == "Last 30 days":
                filtered_data = data[data['timestamp'] >= (data['timestamp'].max() - pd.Timedelta(days=30))]
            else:
                filtered_data = data
        
        with col2:
            # View type filter
            view_options = ["All data", "Anomalies only"]
            selected_view = st.selectbox("View", view_options)
            
            if selected_view == "Anomalies only":
                filtered_data = filtered_data[filtered_data['is_anomaly'] == 1]
        
        with col3:
            # Refresh button
            if st.button("Refresh Dashboard"):
                st.session_state.current_data = None
                st.rerun()
    
    # Key metrics
    st.markdown("### Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_consumption = filtered_data['consumption'].sum()
        st.metric(label="Total Energy Consumption", value=f"{total_consumption:.2f} kWh")
    
    with col2:
        avg_consumption = filtered_data['consumption'].mean()
        st.metric(label="Average Consumption", value=f"{avg_consumption:.2f} kWh")
    
    with col3:
        anomaly_count = filtered_data['is_anomaly'].sum()
        st.metric(label="Anomalies Detected", value=f"{anomaly_count}")
    
    with col4:
        anomaly_percent = (anomaly_count / len(filtered_data)) * 100
        st.metric(label="Anomaly Percentage", value=f"{anomaly_percent:.2f}%")
    
    # Main charts
    st.markdown("### Energy Consumption Patterns")
    
    # Time series chart
    fig_timeseries = px.line(
        filtered_data, 
        x='timestamp', 
        y='consumption',
        title="Energy Consumption Over Time",
        labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
    )
    
    # Add anomaly points to the chart
    anomalies = filtered_data[filtered_data['is_anomaly'] == 1]
    
    fig_timeseries.add_trace(
        go.Scatter(
            x=anomalies['timestamp'],
            y=anomalies['consumption'],
            mode='markers',
            marker=dict(size=10, color='red', symbol='circle'),
            name='Anomalies'
        )
    )
    
    # Update layout for dark theme
    fig_timeseries.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    st.plotly_chart(fig_timeseries, use_container_width=True)
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly pattern analysis
        hourly_data = filtered_data.copy()
        hourly_data['hour'] = hourly_data['timestamp'].dt.hour
        hourly_avg = hourly_data.groupby('hour')['consumption'].mean().reset_index()
        
        fig_hourly = px.bar(
            hourly_avg,
            x='hour',
            y='consumption',
            title="Average Energy Consumption by Hour of Day",
            labels={"consumption": "Energy (kWh)", "hour": "Hour of Day (24h)"}
        )
        
        fig_hourly.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Weekly pattern
        weekly_data = filtered_data.copy()
        weekly_data['weekday'] = weekly_data['timestamp'].dt.day_name()
        
        # Ensure proper ordering of days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_avg = weekly_data.groupby('weekday')['consumption'].mean().reindex(day_order).reset_index()
        
        fig_weekly = px.bar(
            weekly_avg,
            x='weekday',
            y='consumption',
            title="Average Energy Consumption by Day of Week",
            labels={"consumption": "Energy (kWh)", "weekday": "Day of Week"}
        )
        
        fig_weekly.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Third row - Correlation heatmap
    st.markdown("### Correlation Analysis")
    
    # Prepare correlation data
    corr_data = filtered_data[['consumption', 'temperature', 'humidity', 'occupancy']].corr()
    
    # Create heatmap
    fig_corr = px.imshow(
        corr_data,
        text_auto=True,
        color_continuous_scale='Blues',
        title="Correlation between Energy Consumption and Environmental Factors"
    )
    
    fig_corr.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        height=400
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
