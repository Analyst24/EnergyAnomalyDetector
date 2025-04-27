"""
Code snippets module containing predefined code examples.
This module allows for easy management of code snippets used throughout the application.
Each snippet has a title, description, language, and the code itself.
"""

class CodeSnippet:
    """Class representing a code snippet with metadata."""
    
    def __init__(self, id, title, description, language, code):
        """Initialize a code snippet."""
        self.id = id
        self.title = title
        self.description = description
        self.language = language  # python, sql, r, etc.
        self.code = code


# Collection of all available code snippets
SNIPPETS = {
    # Data Loading Snippets
    'load_csv': CodeSnippet(
        id='load_csv',
        title='Load CSV Data with Pandas',
        description='Load data from a CSV file using pandas library.',
        language='python',
        code='''import pandas as pd

# Load the dataset from a CSV file
data = pd.read_csv('energy_consumption.csv')

# Print the first 5 rows to inspect the data
print(data.head())

# Check basic information about the dataset
print(data.info())
'''
    ),
    
    'load_excel': CodeSnippet(
        id='load_excel',
        title='Load Excel Data',
        description='Load data from an Excel file using pandas library.',
        language='python',
        code='''import pandas as pd

# Load the dataset from an Excel file
data = pd.read_excel('energy_consumption.xlsx', sheet_name='Consumption')

# Print the first 5 rows to inspect the data
print(data.head())

# Check basic information about the dataset
print(data.info())
'''
    ),
    
    # Data Preprocessing Snippets
    'clean_missing_values': CodeSnippet(
        id='clean_missing_values',
        title='Clean Missing Values',
        description='Handle missing values in your energy consumption data.',
        language='python',
        code='''import pandas as pd
import numpy as np

# Identify missing values
print("Missing values per column:")
print(data.isnull().sum())

# Option 1: Fill missing values with the mean of the column
data_filled = data.fillna(data.mean())

# Option 2: Fill missing values using forward fill method
data_ffill = data.fillna(method='ffill')

# Option 3: Interpolate missing values
data_interp = data.interpolate(method='linear')

# Option 4: Drop rows with missing values (use with caution!)
data_dropped = data.dropna()

# Verify no missing values remain
print("Missing values after cleaning:")
print(data_filled.isnull().sum())
'''
    ),
    
    'resample_timeseries': CodeSnippet(
        id='resample_timeseries',
        title='Resample Time Series Data',
        description='Resample time series data to different frequencies (hourly, daily, etc.).',
        language='python',
        code='''import pandas as pd

# Ensure the timestamp column is in datetime format
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Set the timestamp as the index
data.set_index('timestamp', inplace=True)

# Resample to hourly average
hourly_data = data.resample('H').mean()

# Resample to daily average
daily_data = data.resample('D').mean()

# Resample to weekly average
weekly_data = data.resample('W').mean()

# Resample to monthly average
monthly_data = data.resample('M').mean()

# Print the first few rows of the resampled data
print("Hourly data:")
print(hourly_data.head())

print("Daily data:")
print(daily_data.head())
'''
    ),
    
    # Anomaly Detection Snippets
    'isolation_forest': CodeSnippet(
        id='isolation_forest',
        title='Isolation Forest Anomaly Detection',
        description='Detect anomalies using the Isolation Forest algorithm.',
        language='python',
        code='''import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

# Prepare data for anomaly detection
# Select numerical columns only
X = data.select_dtypes(include=['number'])

# Fill any missing values
X = X.fillna(X.mean())

# Apply Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.05,  # Expected percentage of anomalies
    random_state=42
)

# Fit and predict anomalies
anomalies = model.fit_predict(X)

# Convert to binary labels (1: normal, -1: anomaly)
# Convert to more intuitive format (0: normal, 1: anomaly)
data['anomaly'] = np.where(anomalies == -1, 1, 0)

# Count anomalies
anomaly_count = data['anomaly'].sum()
print(f"Detected {anomaly_count} anomalies out of {len(data)} data points")

# Plot results if time-series data
if 'timestamp' in data.columns:
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['energy_consumption'], color='blue', label='Energy Consumption')
    plt.scatter(data[data['anomaly'] == 1].index, 
                data[data['anomaly'] == 1]['energy_consumption'],
                color='red', label='Anomaly')
    plt.title('Isolation Forest Anomaly Detection')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy Consumption')
    plt.legend()
    plt.show()
'''
    ),
    
    'autoencoder': CodeSnippet(
        id='autoencoder',
        title='Autoencoder Anomaly Detection',
        description='Detect anomalies using an autoencoder neural network.',
        language='python',
        code='''import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Prepare data for anomaly detection
# Select numerical columns only
X = data.select_dtypes(include=['number'])

# Fill any missing values
X = X.fillna(X.mean())

# Normalize the data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Create and compile the autoencoder model
model = Sequential([
    # Encoder
    Dense(X.shape[1], activation='relu', input_shape=(X.shape[1],)),
    Dense(int(X.shape[1]/2), activation='relu'),
    Dense(int(X.shape[1]/4), activation='relu'),
    
    # Decoder
    Dense(int(X.shape[1]/2), activation='relu'),
    Dense(X.shape[1], activation='sigmoid')
])

model.compile(optimizer='adam', loss='mse')

# Train the model
history = model.fit(
    X_scaled, X_scaled,
    epochs=50,
    batch_size=32,
    validation_split=0.1,
    verbose=1
)

# Predict and calculate reconstruction error
reconstructions = model.predict(X_scaled)
reconstruction_errors = np.mean(np.square(X_scaled - reconstructions), axis=1)

# Set a threshold for anomaly detection
threshold = np.percentile(reconstruction_errors, 95)  # Adjust as needed
data['anomaly'] = np.where(reconstruction_errors > threshold, 1, 0)

# Count anomalies
anomaly_count = data['anomaly'].sum()
print(f"Detected {anomaly_count} anomalies out of {len(data)} data points")

# Plot reconstruction errors
plt.figure(figsize=(10, 6))
plt.hist(reconstruction_errors, bins=50)
plt.axvline(threshold, color='r', linestyle='--')
plt.title('Reconstruction Error Distribution')
plt.xlabel('Reconstruction Error')
plt.ylabel('Count')
plt.show()

# Plot results if time-series data
if 'timestamp' in data.columns:
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['energy_consumption'], color='blue', label='Energy Consumption')
    plt.scatter(data[data['anomaly'] == 1].index, 
                data[data['anomaly'] == 1]['energy_consumption'],
                color='red', label='Anomaly')
    plt.title('Autoencoder Anomaly Detection')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy Consumption')
    plt.legend()
    plt.show()
'''
    ),
    
    'dbscan': CodeSnippet(
        id='dbscan',
        title='DBSCAN Clustering for Anomaly Detection',
        description='Detect anomalies using DBSCAN clustering algorithm.',
        language='python',
        code='''import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Prepare data for anomaly detection
# Select numerical columns only
X = data.select_dtypes(include=['number'])

# Fill any missing values
X = X.fillna(X.mean())

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply DBSCAN clustering
dbscan = DBSCAN(
    eps=0.5,             # Maximum distance between two samples for one to be in the neighborhood of the other
    min_samples=5,       # Number of samples in a neighborhood for a point to be a core point
    n_jobs=-1            # Use all available CPU cores
)

# Fit DBSCAN and get cluster labels
clusters = dbscan.fit_predict(X_scaled)

# Points with cluster label -1 are anomalies
data['anomaly'] = np.where(clusters == -1, 1, 0)

# Count anomalies
anomaly_count = data['anomaly'].sum()
print(f"Detected {anomaly_count} anomalies out of {len(data)} data points")

# Plot results if time-series data
if 'timestamp' in data.columns:
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['energy_consumption'], color='blue', label='Energy Consumption')
    plt.scatter(data[data['anomaly'] == 1].index, 
                data[data['anomaly'] == 1]['energy_consumption'],
                color='red', label='Anomaly')
    plt.title('DBSCAN Anomaly Detection')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy Consumption')
    plt.legend()
    plt.show()
'''
    ),
    
    # Data Visualization Snippets
    'time_series_plot': CodeSnippet(
        id='time_series_plot',
        title='Time Series Visualization',
        description='Visualize time series energy consumption data with anomalies.',
        language='python',
        code='''import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the visualization style
sns.set(style="whitegrid")
plt.figure(figsize=(14, 8))

# Basic time series plot
plt.plot(data.index, data['energy_consumption'], label='Energy Consumption')

# Highlight anomalies if available
if 'anomaly' in data.columns:
    anomalies = data[data['anomaly'] == 1]
    plt.scatter(anomalies.index, anomalies['energy_consumption'], 
                color='red', s=50, label='Anomalies')

# Add title and labels
plt.title('Energy Consumption Over Time', fontsize=16)
plt.xlabel('Timestamp', fontsize=12)
plt.ylabel('Energy Consumption (kWh)', fontsize=12)
plt.legend(fontsize=10)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout and display
plt.tight_layout()
plt.show()

# Create a histogram of energy consumption
plt.figure(figsize=(10, 6))
sns.histplot(data['energy_consumption'], kde=True)
plt.title('Distribution of Energy Consumption', fontsize=16)
plt.xlabel('Energy Consumption (kWh)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.show()
'''
    ),
    
    'interactive_plot': CodeSnippet(
        id='interactive_plot',
        title='Interactive Visualization with Plotly',
        description='Create interactive charts for energy consumption data analysis.',
        language='python',
        code='''import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Create an interactive time series plot
fig = px.line(data, x=data.index, y='energy_consumption',
              title='Interactive Energy Consumption Time Series')

# Add anomalies to the plot if available
if 'anomaly' in data.columns:
    anomalies = data[data['anomaly'] == 1]
    fig.add_trace(go.Scatter(
        x=anomalies.index,
        y=anomalies['energy_consumption'],
        mode='markers',
        name='Anomalies',
        marker=dict(color='red', size=8)
    ))

# Customize the layout
fig.update_layout(
    xaxis_title='Timestamp',
    yaxis_title='Energy Consumption (kWh)',
    hovermode='closest',
    template='plotly_white'
)

# Add range slider and buttons for time period selection
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

# Display the interactive plot
fig.show()

# Create a heatmap for hourly consumption patterns
if 'timestamp' in data.columns:
    # Extract hour and weekday
    data['hour'] = data.index.hour
    data['weekday'] = data.index.day_name()
    
    # Create pivot table
    hourly_consumption = data.pivot_table(
        values='energy_consumption', 
        index='weekday', 
        columns='hour', 
        aggfunc='mean'
    )
    
    # Create heatmap
    fig = px.imshow(hourly_consumption,
                   labels=dict(x="Hour of Day", y="Day of Week", color="Energy Consumption"),
                   title="Energy Consumption Patterns by Hour and Day")
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        coloraxis_colorbar=dict(title="kWh")
    )
    
    fig.show()
'''
    ),
    
    # Reporting and Export Snippets
    'generate_report': CodeSnippet(
        id='generate_report',
        title='Generate Anomaly Report',
        description='Create a comprehensive report of detected anomalies.',
        language='python',
        code='''import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Function to generate anomaly report
def generate_anomaly_report(data, algorithm_name):
    """Generate a report of detected anomalies."""
    # Ensure we have anomaly column
    if 'anomaly' not in data.columns:
        print("No anomaly column found in data.")
        return
    
    # Get anomalies
    anomalies = data[data['anomaly'] == 1].copy()
    
    # Basic statistics
    total_records = len(data)
    anomaly_count = len(anomalies)
    anomaly_percentage = (anomaly_count / total_records) * 100
    
    print(f"=== Anomaly Detection Report ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Algorithm: {algorithm_name}")
    print(f"Dataset Size: {total_records} records")
    print(f"Anomalies Detected: {anomaly_count} ({anomaly_percentage:.2f}%)")
    
    # Time distribution of anomalies
    if 'timestamp' in data.columns or data.index.dtype.kind == 'M':
        if 'timestamp' in data.columns:
            anomalies['hour'] = anomalies['timestamp'].dt.hour
            anomalies['day'] = anomalies['timestamp'].dt.day_name()
        else:
            anomalies['hour'] = anomalies.index.hour
            anomalies['day'] = anomalies.index.day_name()
            
        print("\nTemporal Distribution of Anomalies:")
        
        print("\nHourly Distribution:")
        hour_counts = anomalies['hour'].value_counts().sort_index()
        for hour, count in hour_counts.items():
            print(f"  Hour {hour}: {count} anomalies")
        
        print("\nDaily Distribution:")
        day_counts = anomalies['day'].value_counts()
        for day, count in day_counts.items():
            print(f"  {day}: {count} anomalies")
    
    # Feature statistics for anomalies vs normal
    normal = data[data['anomaly'] == 0]
    
    print("\nFeature Statistics (Anomalies vs Normal):")
    for column in data.select_dtypes(include=['number']).columns:
        if column != 'anomaly':
            anom_mean = anomalies[column].mean()
            norm_mean = normal[column].mean()
            anom_std = anomalies[column].std()
            norm_std = normal[column].std()
            
            print(f"\n  {column}:")
            print(f"    Anomalies: Mean = {anom_mean:.2f}, Std = {anom_std:.2f}")
            print(f"    Normal:    Mean = {norm_mean:.2f}, Std = {norm_std:.2f}")
            print(f"    Difference: {((anom_mean - norm_mean) / norm_mean * 100):.2f}%")
    
    # Save anomalies to CSV
    export_filename = f"anomalies_{algorithm_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    anomalies.to_csv(export_filename)
    print(f"\nDetailed anomaly data exported to {export_filename}")
    
    # Visualize anomalies
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['energy_consumption'], color='blue', alpha=0.5, label='All Data')
    plt.scatter(anomalies.index, anomalies['energy_consumption'], color='red', label='Anomalies')
    plt.title(f'Anomalies Detected by {algorithm_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy Consumption')
    plt.legend()
    
    # Save plot
    plot_filename = f"anomalies_plot_{algorithm_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(plot_filename)
    print(f"Visualization saved to {plot_filename}")
    
    return anomalies

# Generate report
anomalies = generate_anomaly_report(data, "Isolation Forest")
'''
    ),
    
    # SQL Database Query Snippets
    'sql_query_data': CodeSnippet(
        id='sql_query_data',
        title='Query Energy Data from SQL Database',
        description='Retrieve energy consumption data from SQL database.',
        language='sql',
        code='''-- Query all energy consumption data
SELECT timestamp, energy_consumption, temperature, humidity
FROM energy_data
ORDER BY timestamp DESC
LIMIT 1000;

-- Query daily average consumption
SELECT 
    DATE(timestamp) as date,
    AVG(energy_consumption) as avg_consumption,
    MIN(energy_consumption) as min_consumption,
    MAX(energy_consumption) as max_consumption
FROM energy_data
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 90;

-- Query for specific time period
SELECT timestamp, energy_consumption
FROM energy_data
WHERE timestamp BETWEEN '2023-01-01' AND '2023-01-31'
ORDER BY timestamp;

-- Query anomalies
SELECT timestamp, energy_consumption, anomaly_score
FROM energy_anomalies
WHERE is_anomaly = 1
ORDER BY timestamp DESC;

-- Join data with detected anomalies
SELECT 
    d.timestamp, 
    d.energy_consumption,
    d.temperature,
    d.humidity,
    CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END as is_anomaly,
    COALESCE(a.anomaly_score, 0) as anomaly_score
FROM 
    energy_data d
LEFT JOIN 
    energy_anomalies a ON d.timestamp = a.timestamp
WHERE 
    d.timestamp >= '2023-01-01'
ORDER BY 
    d.timestamp;
'''
    ),
}


def get_snippet(snippet_id):
    """Get a code snippet by ID."""
    return SNIPPETS.get(snippet_id)


def get_all_snippets():
    """Get all available code snippets."""
    return SNIPPETS


def get_snippets_by_category():
    """Group snippets by category based on their IDs."""
    categories = {
        'data_loading': ['load_csv', 'load_excel'],
        'data_preprocessing': ['clean_missing_values', 'resample_timeseries'],
        'anomaly_detection': ['isolation_forest', 'autoencoder', 'dbscan'],
        'visualization': ['time_series_plot', 'interactive_plot'],
        'reporting': ['generate_report'],
        'database': ['sql_query_data']
    }
    
    categorized_snippets = {}
    for category, snippet_ids in categories.items():
        categorized_snippets[category] = [SNIPPETS[s_id] for s_id in snippet_ids if s_id in SNIPPETS]
    
    return categorized_snippets