import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import plotly.express as px
from streamlit_extras.colored_header import colored_header

from utils.auth import is_authenticated
from utils.data_processing import (
    validate_dataset, preprocess_data, 
    detect_csv_format, read_energy_csv, 
    list_energy_csv_files, save_processed_data
)
from styles.custom import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="Upload Data | Energy Anomaly Detection",
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
    st.title("⚡ Upload Energy Data")
    
    colored_header(
        label="Data Upload and Validation",
        description="Upload energy consumption datasets for anomaly detection",
        color_name="blue-70"
    )
    
    # Data upload section
    st.markdown("""
    ## Upload Your Energy Consumption Data
    
    Upload a CSV file containing your energy consumption data. The system expects the following columns:
    
    - **timestamp**: Date and time of the measurement (required)
    - **consumption**: Energy consumption value (required)
    - **temperature**: Temperature value (optional)
    - **humidity**: Humidity value (optional)
    - **occupancy**: Building occupancy (optional)
    
    Additional columns will be preserved but might not be used for analysis.
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Load the data
            data = pd.read_csv(uploaded_file)
            
            # Display raw data sample
            st.markdown("### Raw Data Preview")
            st.dataframe(data.head(10), use_container_width=True)
            
            # Validate the dataset
            validation_result, validation_message = validate_dataset(data)
            
            if validation_result:
                st.success(validation_message)
                
                # Process data
                with st.spinner("Processing data..."):
                    processed_data = preprocess_data(data)
                
                st.session_state.current_data = processed_data
                
                # Display processed data sample
                st.markdown("### Processed Data Preview")
                st.dataframe(processed_data.head(10), use_container_width=True)
                
                # Data statistics
                st.markdown("### Data Statistics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Records", len(processed_data))
                
                with col2:
                    start_date = processed_data['timestamp'].min()
                    end_date = processed_data['timestamp'].max()
                    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                    st.metric("Date Range", date_range)
                
                with col3:
                    avg_consumption = processed_data['consumption'].mean()
                    st.metric("Average Consumption", f"{avg_consumption:.2f} kWh")
                
                # Data visualization
                st.markdown("### Data Visualization")
                
                # Time series plot
                fig = px.line(
                    processed_data, 
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
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Distribution plot
                fig_hist = px.histogram(
                    processed_data,
                    x='consumption',
                    nbins=50,
                    title="Energy Consumption Distribution",
                    labels={"consumption": "Energy (kWh)"}
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
                
                # Data download option
                st.markdown("### Download Processed Data")
                
                csv = processed_data.to_csv(index=False)
                st.download_button(
                    label="Download Processed CSV",
                    data=csv,
                    file_name="processed_energy_data.csv",
                    mime="text/csv"
                )
                
            else:
                st.error(validation_message)
        
        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")
    
    # Browse existing CSV files
    st.markdown("---")
    st.markdown("### Browse Existing Energy CSV Files")
    st.markdown("""
    Browse and load existing CSV files that contain energy consumption data.
    The system will automatically detect timestamp and energy consumption columns.
    """)
    
    # Specify the data directory
    data_dir = "assets"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Scan for CSV files
    csv_files = list_energy_csv_files(data_dir)
    
    if csv_files:
        if 'error' in csv_files[0]:
            st.error(f"Error scanning for CSV files: {csv_files[0]['error']}")
        else:
            # Create a dataframe for display
            file_info = []
            for file_data in csv_files:
                if 'is_energy_data' in file_data:
                    is_energy = "✅ Yes" if file_data['is_energy_data'] else "❌ No"
                    size_kb = f"{float(file_data['size']) / 1024:.1f} KB"
                    file_info.append({
                        "Filename": file_data['filename'],
                        "Size": size_kb,
                        "Last Modified": file_data['last_modified'],
                        "Energy Data": is_energy
                    })
            
            if file_info:
                file_df = pd.DataFrame(file_info)
                st.dataframe(file_df, use_container_width=True)
                
                # File selection
                energy_files = [f['filename'] for f in csv_files if f.get('is_energy_data', False)]
                if energy_files:
                    selected_file = st.selectbox("Select an energy data file to load:", 
                                                options=energy_files)
                    
                    if st.button("Load Selected File"):
                        selected_path = os.path.join(data_dir, selected_file)
                        with st.spinner("Loading and processing file..."):
                            # Get the format info
                            format_info = detect_csv_format(selected_path)
                            
                            # Read the file with the detected format
                            data, info = read_energy_csv(selected_path, format_info)
                            
                            if 'error' in info:
                                st.error(f"Error loading file: {info['error']}")
                            else:
                                # Display format detection info
                                st.success(f"File loaded successfully")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("Detected format:")
                                    format_msg = f"""
                                    - Timestamp column: {info['timestamp_column']}
                                    - Consumption column: {info['consumption_column']}
                                    """
                                    if info['temperature_column']:
                                        format_msg += f"- Temperature column: {info['temperature_column']}\n"
                                    if info['humidity_column']:
                                        format_msg += f"- Humidity column: {info['humidity_column']}\n"
                                    if info['occupancy_column']:
                                        format_msg += f"- Occupancy column: {info['occupancy_column']}\n"
                                    
                                    st.markdown(format_msg)
                                
                                # Display raw data sample
                                st.markdown("### Raw Data Preview")
                                st.dataframe(data.head(10), use_container_width=True)
                                
                                # Process the data
                                processed_data = preprocess_data(data)
                                
                                # Store in session state
                                st.session_state.current_data = processed_data
                                
                                # Display processed data sample
                                st.markdown("### Processed Data Preview")
                                st.dataframe(processed_data.head(10), use_container_width=True)
                                
                                # Data visualization
                                st.markdown("### Data Visualization")
                                
                                # Time series plot
                                fig = px.line(
                                    processed_data, 
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
                                
                                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No energy-related CSV files were found. You can upload new files above.")
            else:
                st.info("No CSV files found in the assets directory.")
    else:
        st.info("No CSV files found in the assets directory.")
    
    # Sample data generation option
    st.markdown("---")
    st.markdown("### Generate Sample Data")
    st.markdown("""
    If you don't have your own data but want to test the system, you can generate sample energy consumption data.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_days = st.slider("Number of days", min_value=1, max_value=90, value=30)
    
    with col2:
        anomaly_percentage = st.slider("Anomaly percentage", min_value=0.0, max_value=10.0, value=2.0)
    
    if st.button("Generate Sample Data"):
        with st.spinner("Generating sample data..."):
            # Generate dates
            end_date = pd.Timestamp.now().floor('H')
            start_date = end_date - pd.Timedelta(days=num_days)
            dates = pd.date_range(start=start_date, end=end_date, freq='H')
            
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
            
            # Add anomalies
            anomalies = np.zeros(len(dates))
            num_anomalies = int(len(dates) * (anomaly_percentage / 100))
            anomaly_indices = np.random.choice(len(dates), size=num_anomalies, replace=False)
            anomalies[anomaly_indices] = np.random.normal(0, 30, size=num_anomalies)
            
            # Create the dataset
            sample_data = pd.DataFrame({
                'timestamp': dates,
                'consumption': base + noise + anomalies,
                'temperature': 20 + 10 * np.sin(np.pi * hours / 24) + np.random.normal(0, 2, size=len(dates)),
                'humidity': 50 + 10 * np.sin(np.pi * hours / 12) + np.random.normal(0, 5, size=len(dates)),
                'occupancy': np.where((hours >= 8) & (hours <= 18) & (weekdays < 5), 
                                     np.random.randint(10, 50, size=len(dates)), 
                                     np.random.randint(0, 10, size=len(dates)))
            })
            
            # Flag the anomalies
            sample_data['is_anomaly'] = 0
            sample_data.loc[anomaly_indices, 'is_anomaly'] = 1
            
            # Store in session state
            st.session_state.current_data = sample_data
        
        st.success(f"Generated sample data with {len(sample_data)} records and {num_anomalies} anomalies.")
        
        # Display sample data
        st.dataframe(sample_data.head(10), use_container_width=True)
        
        # Create a download button for the sample data
        csv = sample_data.to_csv(index=False)
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Download Sample Data CSV",
                data=csv,
                file_name="sample_energy_data.csv",
                mime="text/csv"
            )
        
        with col2:
            save_filename = st.text_input("Save as filename (in assets folder):", 
                                         value="sample_energy_data.csv")
            
            if st.button("Save to Assets Folder"):
                # Make sure assets directory exists
                if not os.path.exists("assets"):
                    os.makedirs("assets", exist_ok=True)
                
                # Save the file
                save_path = os.path.join("assets", save_filename)
                
                if save_processed_data(sample_data, save_path):
                    st.success(f"Data saved successfully to {save_path}")
                else:
                    st.error("Failed to save data to file")
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Opulent Chikwiramakomo. All rights reserved.")

if __name__ == "__main__":
    main()
