"""
Visualization utilities for the Energy Anomaly Detection System
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_consumption_overview(data, time_period="Last 30 days"):
    """
    Create a consumption overview plot
    
    Args:
        data: Pandas DataFrame with timestamp and consumption columns
        time_period: String representing the time period to display
        
    Returns:
        fig: Plotly figure object
    """
    # Basic time series plot with dark theme
    fig = px.line(
        data, 
        x='timestamp', 
        y='consumption',
        title=f"Energy Consumption Overview ({time_period})",
        labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
    )
    
    # Add styling for dark theme
    fig.update_layout(
        template="plotly_dark",
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
    Create a plot showing anomaly distribution
    
    Args:
        data: Pandas DataFrame with anomaly data
        
    Returns:
        fig: Plotly figure object
    """
    # Check if data has anomalies
    if 'is_anomaly' not in data.columns or data['is_anomaly'].sum() == 0:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No anomalies detected in the current dataset",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="white")
        )
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(30, 39, 46, 0.8)',
            paper_bgcolor='rgba(30, 39, 46, 0)',
            height=400
        )
        return fig
        
    # Get only anomalies
    anomalies = data[data['is_anomaly'] == 1]
    
    # Create scatter plot of anomalies
    fig = px.scatter(
        anomalies,
        x='timestamp',
        y='consumption',
        title="Detected Anomalies",
        color_discrete_sequence=['red'],
        labels={"consumption": "Energy (kWh)", "timestamp": "Time"}
    )
    
    # Add all data points as background
    fig.add_trace(
        go.Scatter(
            x=data['timestamp'],
            y=data['consumption'],
            mode='lines',
            line=dict(color='rgba(100, 100, 100, 0.3)'),
            name='Normal Values'
        )
    )
    
    # Customize for dark theme
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=400
    )
    
    return fig