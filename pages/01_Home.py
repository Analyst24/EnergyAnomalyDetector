import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header

from utils.auth import is_authenticated
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Home | Energy Anomaly Detection",
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

# Page content
def main():
    st.title("⚡ Energy Anomaly Detection System")
    
    colored_header(
        label="System Overview",
        description="Detect and analyze energy consumption anomalies",
        color_name="blue-70"
    )
    
    # System description
    st.markdown("""
    ## Welcome to the Energy Anomaly Detection System
    
    This advanced system helps you identify and analyze abnormal energy consumption patterns using 
    state-of-the-art machine learning algorithms. By detecting anomalies early, you can:
    
    - **Reduce energy costs** by identifying wasteful consumption
    - **Prevent equipment failures** by detecting unusual operation patterns
    - **Optimize energy usage** with data-driven insights
    - **Meet sustainability goals** by improving energy efficiency
    """)
    
    # Key features with metrics
    st.markdown("## System Capabilities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Anomaly Detection Accuracy", value="96.5%", delta="2.3%")
        st.markdown("Using advanced machine learning algorithms to identify unusual patterns.")
    
    with col2:
        st.metric(label="Processing Speed", value="500K+ points/sec", delta="50K")
        st.markdown("Efficiently process large volumes of energy consumption data.")
    
    with col3:
        st.metric(label="Potential Energy Savings", value="12-18%", delta="3%")
        st.markdown("Typical savings achieved by addressing identified anomalies.")
    
    # Workflow visualization
    st.markdown("## How It Works")
    
    # Sample data for workflow visualization
    stages = ["Data Upload", "Pre-processing", "Anomaly Detection", "Visualization", "Recommendations"]
    progress = [100, 100, 100, 100, 100]
    
    fig = go.Figure(data=[
        go.Bar(
            name='Workflow',
            x=stages,
            y=progress,
            text=progress,
            textposition='auto',
            marker_color=['#4b7bec', '#3867d6', '#3742fa', '#1e90ff', '#70a1ff']
        )
    ])
    
    fig.update_layout(
        title_text='System Workflow',
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("## Recent System Activity")
    
    # Sample activity data
    activity_data = pd.DataFrame({
        'Timestamp': pd.date_range(start='2023-07-01', periods=5, freq='D'),
        'User': ['admin', 'demo', 'admin', 'demo', 'admin'],
        'Action': [
            'Run anomaly detection (Isolation Forest)',
            'Upload new dataset (building_B.csv)',
            'View model insights',
            'Generate recommendations',
            'Update system settings'
        ]
    })
    
    st.dataframe(activity_data, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
