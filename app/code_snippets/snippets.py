"""
Code Snippets for Energy Anomaly Detection System
"""

# Data Loading Snippets
data_loading_snippets = [
    {
        'title': 'Loading Energy Data from CSV',
        'description': 'Use this snippet to load your energy consumption data from a CSV file with proper timestamp parsing.',
        'code': """import pandas as pd

# Load energy consumption data from CSV
def load_energy_data(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path, parse_dates=['timestamp'])
    
    # Set the timestamp as index
    df.set_index('timestamp', inplace=True)
    
    # Sort by timestamp
    df.sort_index(inplace=True)
    
    # Check for missing values
    print(f"Missing values: {df.isna().sum().sum()}")
    
    return df

# Example usage
energy_data = load_energy_data('energy_consumption.csv')
print(energy_data.head())"""
    },
    {
        'title': 'Loading Energy Data from Database',
        'description': 'Use this snippet to load energy data from a SQL database using SQLAlchemy.',
        'code': """import pandas as pd
from sqlalchemy import create_engine

# Load energy data from a database
def load_energy_data_from_db(connection_string, query=None, table_name=None):
    # Create database connection
    engine = create_engine(connection_string)
    
    if query:
        # Use custom SQL query
        df = pd.read_sql(query, engine)
    elif table_name:
        # Read the entire table
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
    else:
        raise ValueError("Either query or table_name must be provided")
    
    # Convert timestamp column to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
    
    return df

# Example usage: SQLite
sqlite_conn = "sqlite:///energy_data.db"
energy_df = load_energy_data_from_db(
    sqlite_conn, 
    table_name="energy_consumption"
)

# Example with custom query
custom_df = load_energy_data_from_db(
    sqlite_conn,
    query="SELECT * FROM energy_consumption WHERE value > 100"
)"""
    }
]

# Preprocessing Snippets
preprocessing_snippets = [
    {
        'title': 'Resampling Time Series Data',
        'description': 'This function helps you resample your energy time series data to different frequencies (hourly, daily, etc.).',
        'code': """import pandas as pd
import numpy as np

# Resample energy data to a different frequency
def resample_energy_data(df, frequency='1H', aggregation='mean'):
    # Resample time series energy data to a different frequency.
    #
    # Parameters:
    #    df: DataFrame with DatetimeIndex
    #    frequency: Target frequency ('1H', '1D', '1W', etc.)
    #    aggregation: Aggregation method ('mean', 'sum', 'max', etc.)
    #
    # Returns:
    #    Resampled DataFrame
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex")
    
    # Dictionary of aggregation methods for each column
    agg_dict = {col: aggregation for col in df.columns}
    
    # Perform the resampling
    resampled_df = df.resample(frequency).agg(agg_dict)
    
    # Handle missing values after resampling
    resampled_df.interpolate(method='time', inplace=True)
    
    return resampled_df

# Example usage
hourly_data = resample_energy_data(energy_data, frequency='1H')
daily_data = resample_energy_data(energy_data, frequency='1D', aggregation='sum')"""
    },
    {
        'title': 'Feature Engineering for Time Series',
        'description': 'Extract useful time-based features from your energy consumption data for better anomaly detection.',
        'code': """import pandas as pd
import numpy as np
from datetime import datetime

# Create time-based features for energy data
def create_time_features(df):
    # Create time-based features from datetime index
    # Make a copy of the dataframe
    result = df.copy()
    
    # Extract datetime components
    result['hour'] = result.index.hour
    result['day_of_week'] = result.index.dayofweek
    result['day_of_month'] = result.index.day
    result['month'] = result.index.month
    result['year'] = result.index.year
    
    # Create cyclical features for hour
    result['hour_sin'] = np.sin(2 * np.pi * result.index.hour / 24)
    result['hour_cos'] = np.cos(2 * np.pi * result.index.hour / 24)
    
    # Create day of week features (0 = Monday, 6 = Sunday)
    result['is_weekend'] = (result['day_of_week'] >= 5).astype(int)
    
    # Create week of year
    result['week_of_year'] = result.index.isocalendar().week
    
    # Create business hours feature (9 AM to 5 PM, weekdays)
    result['is_business_hours'] = (
        (result['hour'] >= 9) & 
        (result['hour'] < 17) & 
        (result['is_weekend'] == 0)
    ).astype(int)
    
    # Create seasonal features
    # Winter: Dec, Jan, Feb; Spring: Mar, Apr, May; Summer: Jun, Jul, Aug; Fall: Sep, Oct, Nov
    conditions = [
        (result['month'].isin([12, 1, 2])),
        (result['month'].isin([3, 4, 5])),
        (result['month'].isin([6, 7, 8])),
        (result['month'].isin([9, 10, 11]))
    ]
    choices = ['winter', 'spring', 'summer', 'fall']
    result['season'] = np.select(conditions, choices, default='unknown')
    
    return result

# Example usage
energy_features_df = create_time_features(energy_data)"""
    }
]

# Anomaly Detection Snippets
anomaly_detection_snippets = [
    {
        'title': 'Isolation Forest for Anomaly Detection',
        'description': 'Use the Isolation Forest algorithm to detect anomalies in your energy consumption data.',
        'code': """import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

def detect_anomalies_isolation_forest(df, feature_columns, n_estimators=100, contamination=0.05):
    # Detect anomalies in energy data using Isolation Forest algorithm
    #
    # Parameters:
    #    df: DataFrame with energy data
    #    feature_columns: List of columns to use for anomaly detection
    #    n_estimators: Number of trees in the forest
    #    contamination: Expected proportion of anomalies in the dataset
    #
    # Returns:
    #    DataFrame with added anomaly scores and labels
    # Create a copy of the input dataframe
    result_df = df.copy()
    
    # Extract features for anomaly detection
    X = result_df[feature_columns].values
    
    # Initialize and fit the model
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=42,
        n_jobs=-1  # Use all available processors
    )
    
    # Fit the model and predict anomalies
    result_df['anomaly_score'] = model.fit_predict(X)
    
    # Convert prediction to binary (1: normal, -1: anomaly)
    result_df['is_anomaly'] = (result_df['anomaly_score'] == -1).astype(int)
    
    # Calculate anomaly decision score (negative for anomalies)
    result_df['decision_score'] = model.decision_function(X)
    
    return result_df, model

# Example usage
features = ['consumption', 'temperature', 'humidity']
anomaly_df, isolation_forest_model = detect_anomalies_isolation_forest(
    energy_features_df, 
    feature_columns=features
)

# Display summary of anomalies
anomaly_count = anomaly_df['is_anomaly'].sum()
print(f"Detected {anomaly_count} anomalies out of {len(anomaly_df)} data points")"""
    },
    {
        'title': 'DBSCAN Clustering for Anomaly Detection',
        'description': 'Use DBSCAN clustering to identify outliers as anomalies in your energy consumption data.',
        'code': """import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def detect_anomalies_dbscan(df, feature_columns, eps=0.5, min_samples=5):
    # Detect anomalies in energy data using DBSCAN clustering
    #
    # Parameters:
    #    df: DataFrame with energy data
    #    feature_columns: List of columns to use for anomaly detection
    #    eps: Maximum distance between samples for them to be considered as in the same neighborhood
    #    min_samples: Minimum number of samples in a neighborhood for a point to be a core point
    #
    # Returns:
    #    DataFrame with added cluster labels (-1 for outliers/anomalies)
    # Create a copy of the input dataframe
    result_df = df.copy()
    
    # Extract features for anomaly detection
    X = result_df[feature_columns].values
    
    # Standardize the features
    X_scaled = StandardScaler().fit_transform(X)
    
    # Initialize and fit DBSCAN
    model = DBSCAN(eps=eps, min_samples=min_samples)
    
    # Fit the model and get cluster labels
    # Cluster label -1 indicates outliers/anomalies
    result_df['cluster'] = model.fit_predict(X_scaled)
    
    # Create a binary anomaly indicator (1 for anomalies)
    result_df['is_anomaly'] = (result_df['cluster'] == -1).astype(int)
    
    return result_df, model

# Example usage
features = ['consumption', 'temperature', 'humidity']
anomaly_df, dbscan_model = detect_anomalies_dbscan(
    energy_features_df, 
    feature_columns=features,
    eps=0.3,
    min_samples=10
)

# Display summary of anomalies
anomaly_count = anomaly_df['is_anomaly'].sum()
print(f"Detected {anomaly_count} anomalies out of {len(anomaly_df)} data points")"""
    }
]

# Visualization Snippets
visualization_snippets = [
    {
        'title': 'Visualizing Energy Consumption with Anomalies',
        'description': 'Create an interactive visualization of your energy consumption data with highlighted anomalies using Plotly.',
        'code': """import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_energy_consumption_with_anomalies(df, value_column='consumption', anomaly_column='is_anomaly'):
    # Plot energy consumption with highlighted anomalies using Plotly
    #
    # Parameters:
    #    df: DataFrame with energy data, anomaly indicators, and DatetimeIndex
    #    value_column: Name of the column containing consumption values
    #    anomaly_column: Name of the column containing anomaly indicators (1 for anomalies)
    #
    # Returns:
    #    Plotly figure object
    # Create a new figure
    fig = go.Figure()
    
    # Add the main consumption line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[value_column],
            mode='lines',
            name='Energy Consumption',
            line=dict(color='rgba(0, 176, 255, 0.8)', width=2)
        )
    )
    
    # Extract anomalies
    anomalies = df[df[anomaly_column] == 1]
    
    # Add anomaly points
    if len(anomalies) > 0:
        fig.add_trace(
            go.Scatter(
                x=anomalies.index,
                y=anomalies[value_column],
                mode='markers',
                name='Anomalies',
                marker=dict(
                    color='red',
                    size=10,
                    line=dict(color='black', width=1)
                )
            )
        )
    
    # Update layout for a professional look
    fig.update_layout(
        title='Energy Consumption with Detected Anomalies',
        xaxis_title='Time',
        yaxis_title='Energy Consumption',
        template='plotly_dark',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white')
    )
    
    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

# Example usage
fig = plot_energy_consumption_with_anomalies(anomaly_df)
fig.show()  # In Flask: return fig.to_html()"""
    },
    {
        'title': 'Creating an Anomaly Analysis Dashboard',
        'description': 'Build a comprehensive dashboard with multiple visualizations to analyze energy consumption anomalies.',
        'code': """import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_anomaly_analysis_dashboard(df, value_column='consumption', anomaly_column='is_anomaly'):
    # Create a comprehensive anomaly analysis dashboard with multiple visualizations
    #
    # Parameters:
    #    df: DataFrame with energy data, anomaly indicators, and DatetimeIndex
    #    value_column: Name of the column containing consumption values
    #    anomaly_column: Name of the column containing anomaly indicators (1 for anomalies)
    #
    # Returns:
    #    Plotly figure object with multiple subplots
    # Create a figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Energy Consumption Time Series',
            'Distribution of Normal vs Anomalous Values',
            'Hourly Pattern of Anomalies',
            'Monthly Anomaly Frequency'
        ),
        specs=[
            [{"colspan": 2}, None],
            [{"type": "xy"}, {"type": "xy"}]
        ],
        vertical_spacing=0.1
    )
    
    # Extract normal and anomalous points
    normal_df = df[df[anomaly_column] == 0]
    anomaly_df = df[df[anomaly_column] == 1]
    
    # 1. Time Series Plot (top row, spans both columns)
    fig.add_trace(
        go.Scatter(
            x=normal_df.index,
            y=normal_df[value_column],
            mode='lines',
            name='Normal',
            line=dict(color='rgba(0, 176, 255, 0.7)', width=1.5)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=anomaly_df.index,
            y=anomaly_df[value_column],
            mode='markers',
            name='Anomalies',
            marker=dict(color='red', size=8, symbol='circle')
        ),
        row=1, col=1
    )
    
    # 2. Distribution Plot (bottom left)
    fig.add_trace(
        go.Histogram(
            x=normal_df[value_column],
            name='Normal Values',
            opacity=0.7,
            marker_color='rgba(0, 176, 255, 0.7)',
            nbinsx=30
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Histogram(
            x=anomaly_df[value_column],
            name='Anomalous Values',
            opacity=0.7,
            marker_color='rgba(255, 0, 0, 0.7)',
            nbinsx=30
        ),
        row=2, col=1
    )
    
    # 3. Hourly Pattern (bottom right)
    # Group anomalies by hour
    if 'hour' not in df.columns and isinstance(df.index, pd.DatetimeIndex):
        df_with_hour = df.copy()
        df_with_hour['hour'] = df_with_hour.index.hour
    else:
        df_with_hour = df
    
    hourly_anomalies = df_with_hour[df_with_hour[anomaly_column] == 1]
    hour_counts = hourly_anomalies.groupby('hour').size().reset_index(name='count')
    
    fig.add_trace(
        go.Bar(
            x=hour_counts['hour'],
            y=hour_counts['count'],
            name='Hourly Anomalies',
            marker_color='rgba(255, 165, 0, 0.7)'
        ),
        row=2, col=2
    )
    
    # Update layout and axis labels
    fig.update_layout(
        height=800,
        title='Energy Consumption Anomaly Analysis Dashboard',
        template='plotly_dark',
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        plot_bgcolor='rgba(30, 39, 46, 0.8)',
        paper_bgcolor='rgba(30, 39, 46, 0)',
        font=dict(color='white')
    )
    
    fig.update_xaxes(title_text='Time', row=1, col=1)
    fig.update_yaxes(title_text='Energy Consumption', row=1, col=1)
    
    fig.update_xaxes(title_text='Energy Consumption', row=2, col=1)
    fig.update_yaxes(title_text='Frequency', row=2, col=1)
    
    fig.update_xaxes(title_text='Hour of Day', row=2, col=2)
    fig.update_yaxes(title_text='Number of Anomalies', row=2, col=2)
    
    return fig

# Example usage
dashboard_fig = create_anomaly_analysis_dashboard(anomaly_df)
dashboard_fig.show()  # In Flask: return dashboard_fig.to_html()"""
    }
]