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
    page_title="Results | Energy Anomaly Detection",
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
    st.title("⚡ Anomaly Detection Results")
    
    colored_header(
        label="Results Analysis",
        description="Detailed analysis of detected energy consumption anomalies",
        color_name="blue-70"
    )
    
    # Check if results are available
    if st.session_state.detection_results is None:
        st.warning("No detection results available. Please run anomaly detection first.")
        st.stop()
    
    # Get the results
    results = st.session_state.detection_results
    anomalies = results[results['is_anomaly'] == 1]
    
    # Summary statistics
    st.markdown("### Summary of Detected Anomalies")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(results)
        st.metric("Total Records", total_records)
    
    with col2:
        anomaly_count = len(anomalies)
        st.metric("Anomalies Detected", anomaly_count)
    
    with col3:
        anomaly_percent = (anomaly_count / total_records) * 100
        st.metric("Anomaly Percentage", f"{anomaly_percent:.2f}%")
    
    with col4:
        algorithm = st.session_state.selected_algorithm
        st.metric("Detection Algorithm", algorithm)
    
    # Time series visualization with anomalies
    st.markdown("### Energy Consumption with Detected Anomalies")
    
    # Create figure
    fig = px.line(
        results, 
        x='timestamp', 
        y='consumption',
        title=f"Energy Consumption Time Series with Anomalies ({algorithm})",
        labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
    )
    
    # Add anomaly points
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
    
    # Anomalies analysis
    st.markdown("### Anomaly Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of anomaly scores
        if 'anomaly_score' in results.columns:
            fig_hist = px.histogram(
                results,
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
    
    with col2:
        # Anomaly by hour of day
        anomalies_hour = anomalies.copy()
        anomalies_hour['hour'] = anomalies_hour['timestamp'].dt.hour
        hour_counts = anomalies_hour.groupby('hour').size().reset_index(name='count')
        
        fig_hour = px.bar(
            hour_counts,
            x='hour',
            y='count',
            title="Anomalies by Hour of Day",
            labels={"count": "Number of Anomalies", "hour": "Hour of Day (24h)"}
        )
        
        fig_hour.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_hour, use_container_width=True)
    
    # Anomalies by day of week
    st.markdown("### Temporal Distribution of Anomalies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Anomalies by day of week
        anomalies_dow = anomalies.copy()
        anomalies_dow['weekday'] = anomalies_dow['timestamp'].dt.day_name()
        
        # Ensure proper ordering of days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = anomalies_dow.groupby('weekday').size().reindex(day_order).reset_index(name='count')
        
        fig_dow = px.bar(
            dow_counts,
            x='weekday',
            y='count',
            title="Anomalies by Day of Week",
            labels={"count": "Number of Anomalies", "weekday": "Day of Week"}
        )
        
        fig_dow.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_dow, use_container_width=True)
    
    with col2:
        # Anomalies over time (weekly aggregation)
        anomalies_time = anomalies.copy()
        anomalies_time['week'] = anomalies_time['timestamp'].dt.isocalendar().week
        anomalies_time['year'] = anomalies_time['timestamp'].dt.isocalendar().year
        anomalies_time['yearweek'] = anomalies_time['year'].astype(str) + '-W' + anomalies_time['week'].astype(str).str.zfill(2)
        
        week_counts = anomalies_time.groupby('yearweek').size().reset_index(name='count')
        
        fig_time = px.line(
            week_counts,
            x='yearweek',
            y='count',
            title="Anomalies Over Time (Weekly)",
            labels={"count": "Number of Anomalies", "yearweek": "Year-Week"}
        )
        
        fig_time.update_layout(
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
            height=400
        )
        
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Detailed list of anomalies
    st.markdown("### Detailed Anomalies List")
    
    # Display anomalies with additional context
    if len(anomalies) > 0:
        # Sort by anomaly score or timestamp
        if 'anomaly_score' in anomalies.columns:
            sorted_anomalies = anomalies.sort_values(by='anomaly_score', ascending=False)
        else:
            sorted_anomalies = anomalies.sort_values(by='timestamp')
        
        # Calculate percentage deviation from expected
        if 'expected_value' in sorted_anomalies.columns:
            sorted_anomalies['deviation_pct'] = ((sorted_anomalies['consumption'] - sorted_anomalies['expected_value']) / 
                                                sorted_anomalies['expected_value'] * 100)
        
        # Display the anomalies table
        st.dataframe(sorted_anomalies, use_container_width=True)
        
        # Download button for anomalies
        csv = sorted_anomalies.to_csv(index=False)
        st.download_button(
            label="Download Anomalies CSV",
            data=csv,
            file_name="energy_anomalies.csv",
            mime="text/csv"
        )
    else:
        st.info("No anomalies were detected in the dataset.")
    
    # Anomaly patterns
    if len(anomalies) > 0:
        st.markdown("### Anomaly Patterns")
        
        # Compare normal vs anomalous consumption
        consumption_comparison = pd.DataFrame({
            'Status': ['Normal', 'Anomaly'],
            'Average Consumption': [
                results[results['is_anomaly'] == 0]['consumption'].mean(),
                results[results['is_anomaly'] == 1]['consumption'].mean()
            ],
            'Minimum Consumption': [
                results[results['is_anomaly'] == 0]['consumption'].min(),
                results[results['is_anomaly'] == 1]['consumption'].min()
            ],
            'Maximum Consumption': [
                results[results['is_anomaly'] == 0]['consumption'].max(),
                results[results['is_anomaly'] == 1]['consumption'].max()
            ],
            'Standard Deviation': [
                results[results['is_anomaly'] == 0]['consumption'].std(),
                results[results['is_anomaly'] == 1]['consumption'].std()
            ]
        })
        
        st.dataframe(consumption_comparison, use_container_width=True)
        
        # Visualize the comparison
        fig_comparison = go.Figure()
        
        # Add normal data
        fig_comparison.add_trace(go.Box(
            y=results[results['is_anomaly'] == 0]['consumption'],
            name='Normal',
            marker_color='blue'
        ))
        
        # Add anomaly data
        fig_comparison.add_trace(go.Box(
            y=results[results['is_anomaly'] == 1]['consumption'],
            name='Anomaly',
            marker_color='red'
        ))
        
        fig_comparison.update_layout(
            title="Consumption Distribution: Normal vs Anomaly",
            yaxis_title="Energy Consumption (kWh)",
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            font=dict(color='white'),
            height=500
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
