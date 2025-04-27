"""
Visualization utilities for the Energy Anomaly Detection System.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def plot_consumption_overview(data):
    """
    Create an interactive plot showing energy consumption over time.
    
    Parameters:
        data (DataFrame): The dataset with 'timestamp' and 'consumption' columns
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create figure
    fig = px.line(
        data, 
        x='timestamp', 
        y='consumption',
        title="Energy Consumption Over Time",
        labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    return fig

def plot_anomaly_distribution(data):
    """
    Create a plot showing the distribution of normal vs anomalous consumption.
    
    Parameters:
        data (DataFrame): The dataset with 'consumption' and 'is_anomaly' columns
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create figure
    fig = px.histogram(
        data,
        x='consumption',
        color='is_anomaly',
        marginal='box',
        nbins=50,
        title="Distribution of Normal vs Anomalous Consumption",
        labels={"consumption": "Energy (kWh)", "is_anomaly": "Is Anomaly"},
        color_discrete_map={0: "blue", 1: "red"}
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    return fig

def plot_hourly_pattern(data):
    """
    Create a plot showing average consumption by hour of day.
    
    Parameters:
        data (DataFrame): The dataset with 'timestamp' and 'consumption' columns
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create hour column
    hourly_data = data.copy()
    hourly_data['hour'] = hourly_data['timestamp'].dt.hour
    
    # Aggregate by hour
    hourly_avg = hourly_data.groupby('hour')['consumption'].mean().reset_index()
    
    # Create plot
    fig = px.bar(
        hourly_avg,
        x='hour',
        y='consumption',
        title="Average Energy Consumption by Hour of Day",
        labels={"consumption": "Energy (kWh)", "hour": "Hour of Day (24h)"}
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    return fig

def plot_weekly_pattern(data):
    """
    Create a plot showing average consumption by day of week.
    
    Parameters:
        data (DataFrame): The dataset with 'timestamp' and 'consumption' columns
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create weekday column
    weekly_data = data.copy()
    weekly_data['weekday'] = weekly_data['timestamp'].dt.day_name()
    
    # Ensure proper ordering of days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_avg = weekly_data.groupby('weekday')['consumption'].mean().reindex(day_order).reset_index()
    
    # Create plot
    fig = px.bar(
        weekly_avg,
        x='weekday',
        y='consumption',
        title="Average Energy Consumption by Day of Week",
        labels={"consumption": "Energy (kWh)", "weekday": "Day of Week"}
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    return fig

def plot_anomaly_heatmap(data):
    """
    Create a heatmap showing anomaly distribution by hour and day of week.
    
    Parameters:
        data (DataFrame): The dataset with anomaly indicators
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create hour and weekday columns
    heatmap_data = data.copy()
    heatmap_data = heatmap_data[heatmap_data['is_anomaly'] == 1]
    heatmap_data['hour'] = heatmap_data['timestamp'].dt.hour
    heatmap_data['weekday'] = heatmap_data['timestamp'].dt.day_name()
    
    # Count anomalies by hour and weekday
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    anomaly_counts = pd.crosstab(heatmap_data['weekday'], heatmap_data['hour'])
    
    # Reorder rows based on day_order
    anomaly_counts = anomaly_counts.reindex(day_order)
    
    # Create heatmap
    fig = px.imshow(
        anomaly_counts,
        title="Anomaly Distribution by Hour and Day",
        labels=dict(x="Hour of Day", y="Day of Week", color="Anomaly Count"),
        color_continuous_scale="Reds"
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

def plot_feature_correlation(data):
    """
    Create a correlation heatmap between different features.
    
    Parameters:
        data (DataFrame): The dataset with numeric features
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Select only numeric columns
    numeric_data = data.select_dtypes(include=[np.number])
    
    # Calculate correlation
    corr_matrix = numeric_data.corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        title="Feature Correlation Matrix",
        color_continuous_scale="Blues"
    )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def plot_anomaly_scores(data, score_column, threshold=None):
    """
    Create a plot of anomaly scores with threshold line.
    
    Parameters:
        data (DataFrame): The dataset with anomaly scores
        score_column (str): The name of the column containing anomaly scores
        threshold (float): The threshold value for anomaly detection
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create figure
    fig = px.histogram(
        data,
        x=score_column,
        color='is_anomaly',
        marginal='box',
        nbins=50,
        title=f"Distribution of {score_column.replace('_', ' ').title()}",
        labels={score_column: score_column.replace('_', ' ').title(), "is_anomaly": "Is Anomaly"},
        color_discrete_map={0: "blue", 1: "red"}
    )
    
    # Add threshold line if provided
    if threshold is not None:
        fig.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="green",
            annotation_text="Threshold",
            annotation_position="top right"
        )
    
    # Update layout for dark theme
    fig.update_layout(
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    return fig

def plot_time_series_with_anomalies(data, algorithm_name=None):
    """
    Create a time series plot with highlighted anomalies.
    
    Parameters:
        data (DataFrame): The dataset with 'timestamp', 'consumption' and 'is_anomaly' columns
        algorithm_name (str): The name of the algorithm used for detection
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure
    """
    # Create figure
    title = "Energy Consumption with Detected Anomalies"
    if algorithm_name:
        title += f" ({algorithm_name})"
    
    fig = px.line(
        data, 
        x='timestamp', 
        y='consumption',
        title=title,
        labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
    )
    
    # Add anomaly points
    anomalies = data[data['is_anomaly'] == 1]
    
    if len(anomalies) > 0:
        fig.add_trace(
            go.Scatter(
                x=anomalies['timestamp'],
                y=anomalies['consumption'],
                mode='markers',
                marker=dict(size=10, color='red', symbol='circle'),
                name='Anomalies'
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
    
    return fig

def create_metrics_card(title, metrics_dict):
    """
    Create a card with metrics display.
    
    Parameters:
        title (str): The title of the metrics card
        metrics_dict (dict): Dictionary of metric names and values
    """
    st.markdown(f"### {title}")
    
    # Determine number of columns based on metrics count
    num_metrics = len(metrics_dict)
    cols = st.columns(min(num_metrics, 4))  # Max 4 columns
    
    # Display metrics in columns
    for i, (metric_name, metric_value) in enumerate(metrics_dict.items()):
        col_idx = i % len(cols)
        
        with cols[col_idx]:
            if isinstance(metric_value, float):
                st.metric(metric_name, f"{metric_value:.2f}")
            else:
                st.metric(metric_name, metric_value)
