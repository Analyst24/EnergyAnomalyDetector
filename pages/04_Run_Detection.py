import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header

from utils.auth import is_authenticated
from models.isolation_forest import run_isolation_forest
from models.autoencoder import run_autoencoder
from models.kmeans import run_kmeans
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Run Detection | Energy Anomaly Detection",
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
    st.title("⚡ Run Anomaly Detection")
    
    colored_header(
        label="Anomaly Detection",
        description="Detect energy consumption anomalies using machine learning algorithms",
        color_name="blue-70"
    )
    
    # Check if data is available
    if st.session_state.current_data is None:
        st.warning("No data available. Please upload or generate data first.")
        st.stop()
    
    # Get the data
    data = st.session_state.current_data
    
    # Algorithm selection
    st.markdown("### Select Anomaly Detection Algorithm")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        algorithm = st.radio(
            "Algorithm",
            ["Isolation Forest", "AutoEncoder", "K-Means"],
            index=0
        )
        
        st.session_state.selected_algorithm = algorithm
    
    with col2:
        if algorithm == "Isolation Forest":
            st.markdown("""
            **Isolation Forest** is an algorithm that explicitly identifies anomalies by isolating observations.
            It works on the principle that anomalies are 'few and different', making them easier to isolate
            in feature space compared to normal points.
            
            Best for: General-purpose anomaly detection with good performance on high-dimensional data.
            """)
            
            # Algorithm parameters
            contamination = st.slider(
                "Contamination (expected percentage of anomalies)",
                min_value=0.01,
                max_value=0.2,
                value=0.05,
                step=0.01
            )
            
            n_estimators = st.slider(
                "Number of estimators",
                min_value=50,
                max_value=500,
                value=100,
                step=10
            )
            
            params = {
                "contamination": contamination,
                "n_estimators": n_estimators
            }
            
        elif algorithm == "AutoEncoder":
            st.markdown("""
            **AutoEncoder** is a neural network-based approach that learns to reconstruct normal patterns.
            Points with high reconstruction error are flagged as anomalies.
            
            Best for: Complex non-linear patterns and capturing temporal dependencies in energy consumption.
            """)
            
            # Algorithm parameters
            threshold_percent = st.slider(
                "Anomaly threshold percentile",
                min_value=90,
                max_value=99,
                value=95,
                step=1
            )
            
            epochs = st.slider(
                "Training epochs",
                min_value=10,
                max_value=100,
                value=50,
                step=5
            )
            
            params = {
                "threshold_percent": threshold_percent,
                "epochs": epochs
            }
            
        elif algorithm == "K-Means":
            st.markdown("""
            **K-Means** clustering identifies anomalies by measuring the distance to the nearest cluster center.
            Points far from any cluster center are considered anomalies.
            
            Best for: Identifying distinct groups of consumption patterns and detecting outliers.
            """)
            
            # Algorithm parameters
            n_clusters = st.slider(
                "Number of clusters",
                min_value=2,
                max_value=20,
                value=5,
                step=1
            )
            
            threshold_percent = st.slider(
                "Anomaly threshold percentile",
                min_value=90,
                max_value=99,
                value=95,
                step=1
            )
            
            params = {
                "n_clusters": n_clusters,
                "threshold_percent": threshold_percent
            }
    
    # Feature selection
    st.markdown("### Select Features for Anomaly Detection")
    
    all_features = list(data.columns)
    non_selectable = ['timestamp', 'is_anomaly']
    selectable_features = [f for f in all_features if f not in non_selectable]
    
    selected_features = st.multiselect(
        "Features to use for detection",
        selectable_features,
        default=['consumption']
    )
    
    if not selected_features:
        st.error("Please select at least one feature for anomaly detection.")
        st.stop()
    
    # Run detection button
    if st.button("Run Anomaly Detection", type="primary"):
        with st.spinner(f"Running {algorithm} algorithm..."):
            # Track start time
            start_time = time.time()
            
            # Run the selected algorithm
            if algorithm == "Isolation Forest":
                result_data, model_info = run_isolation_forest(data, selected_features, params)
            elif algorithm == "AutoEncoder":
                result_data, model_info = run_autoencoder(data, selected_features, params)
            elif algorithm == "K-Means":
                result_data, model_info = run_kmeans(data, selected_features, params)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Store results in session state
            st.session_state.detection_results = result_data
            st.session_state.model_metrics = model_info
        
        # Display results summary
        st.success(f"Anomaly detection completed in {execution_time:.2f} seconds.")
        
        # Count anomalies
        anomaly_count = result_data['is_anomaly'].sum()
        total_count = len(result_data)
        anomaly_percent = (anomaly_count / total_count) * 100
        
        # Results metrics
        st.markdown("### Detection Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", total_count)
        
        with col2:
            st.metric("Anomalies Detected", anomaly_count)
        
        with col3:
            st.metric("Anomaly Percentage", f"{anomaly_percent:.2f}%")
        
        # Display model-specific metrics
        st.markdown("### Model Metrics")
        
        for metric_name, metric_value in model_info.items():
            if isinstance(metric_value, (int, float)):
                st.metric(metric_name, f"{metric_value:.4f}" if isinstance(metric_value, float) else metric_value)
        
        # Visualization of results
        st.markdown("### Anomaly Visualization")
        
        # Time series plot with anomalies
        fig = px.line(
            result_data, 
            x='timestamp', 
            y='consumption',
            title=f"Energy Consumption with Detected Anomalies ({algorithm})",
            labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
        )
        
        # Add anomaly points to the chart
        anomalies = result_data[result_data['is_anomaly'] == 1]
        
        fig.add_trace(
            go.Scatter(
                x=anomalies['timestamp'],
                y=anomalies['consumption'],
                mode='markers',
                marker=dict(size=10, color='red', symbol='circle'),
                name='Detected Anomalies'
            )
        )
        
        # Update layout for dark theme
        fig.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature distribution with anomalies
        if 'anomaly_score' in result_data.columns:
            # Create histogram of anomaly scores
            fig_hist = px.histogram(
                result_data,
                x='anomaly_score',
                color='is_anomaly',
                marginal='box',
                title="Distribution of Anomaly Scores",
                labels={"anomaly_score": "Anomaly Score", "is_anomaly": "Is Anomaly"},
                color_discrete_map={0: "blue", 1: "red"}
            )
            
            fig_hist.update_layout(
                plot_bgcolor='rgba(30, 39, 46, 0.8)',
                paper_bgcolor='rgba(30, 39, 46, 0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                height=400
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Download results button
        csv = result_data.to_csv(index=False)
        st.download_button(
            label="Download Detection Results",
            data=csv,
            file_name=f"anomaly_detection_results_{algorithm.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        # Guidance for next steps
        st.info("You can now go to the Results page for more detailed analysis of the detected anomalies.")
    
    # Algorithm comparison info
    st.markdown("---")
    st.markdown("### Algorithm Comparison")
    
    comparison_data = {
        'Algorithm': ['Isolation Forest', 'AutoEncoder', 'K-Means'],
        'Best For': [
            'General anomaly detection, works well with high-dimensional data',
            'Complex patterns, capturing temporal dependencies',
            'Identifying distinct consumption patterns'
        ],
        'Speed': ['Fast', 'Slow (training required)', 'Medium'],
        'Explainability': ['Medium', 'Low', 'High'],
        'Handles Noise': ['Excellent', 'Good', 'Fair']
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
