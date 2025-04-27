"""
Upload routes for the Energy Anomaly Detection System.
"""
import os
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Dataset
from app.upload.forms import UploadForm
from datetime import datetime
import uuid

# Create blueprint
upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

def validate_dataset(df):
    """
    Validate that the uploaded dataset contains required columns.
    
    Args:
        df (pandas.DataFrame): The dataset to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    # Check if required columns exist
    required_columns = ['timestamp', 'consumption']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check if timestamp column can be parsed
    try:
        pd.to_datetime(df['timestamp'])
    except Exception:
        return False, "Timestamp column could not be parsed. Please ensure it's in a standard date-time format."
    
    # Check if consumption column is numeric
    if not pd.api.types.is_numeric_dtype(df['consumption']):
        return False, "Consumption column must contain numeric values."
    
    # Check if there's enough data
    if len(df) < 10:
        return False, "Dataset contains too few rows (minimum 10 required)."
    
    return True, "Dataset is valid."

@upload_bp.route('/upload')
@login_required
def index():
    """Render the upload page."""
    # Initialize upload form
    form = UploadForm()
    
    # Get user's datasets
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    
    # Render upload page with form and datasets
    return render_template(
        'upload/index.html',
        active_page='upload',
        form=form,
        datasets=datasets
    )

@upload_bp.route('/upload/file', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload."""
    form = UploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        
        # Check if file was selected
        if not file:
            flash('No file selected', 'danger')
            return redirect(url_for('upload.index'))
        
        # Check if the file is allowed
        if not allowed_file(file.filename):
            flash('Only CSV files are allowed', 'danger')
            return redirect(url_for('upload.index'))
        
        try:
            # Read the file into a pandas DataFrame
            df = pd.read_csv(file, header=0 if form.has_header.data else None)
            
            # If file doesn't have headers, assign default ones
            if not form.has_header.data:
                df.columns = [f'col_{i}' for i in range(len(df.columns))]
                # Try to rename the first two columns to defaults if they exist
                if len(df.columns) >= 2:
                    df = df.rename(columns={'col_0': 'timestamp', 'col_1': 'consumption'})
            
            # Validate the dataset
            is_valid, message = validate_dataset(df)
            if not is_valid:
                flash(message, 'danger')
                return redirect(url_for('upload.index'))
            
            # Create a unique filename to avoid conflicts
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            # Create the upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file to disk
            file_path = os.path.join(upload_dir, filename)
            df.to_csv(file_path, index=False)
            
            # Get time period of the dataset
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                start_date = df['timestamp'].min()
                end_date = df['timestamp'].max()
                time_period = f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"
            except:
                time_period = "Unknown"
            
            # Create database record
            dataset = Dataset(
                name=form.name.data,
                description=form.description.data,
                filename=original_filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type='csv',
                row_count=len(df),
                column_count=len(df.columns),
                has_timestamps=True,
                user_id=current_user.id,
                dataset_metadata={
                    'columns': df.columns.tolist(),
                    'time_period': time_period
                }
            )
            
            db.session.add(dataset)
            db.session.commit()
            
            flash(f'Dataset "{form.name.data}" uploaded successfully with {len(df)} rows and {len(df.columns)} columns.', 'success')
            return redirect(url_for('upload.index'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(url_for('upload.index'))
    
    # If form validation failed
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('upload.index'))

@upload_bp.route('/upload/preview/<int:id>')
@login_required
def preview_dataset(id):
    """Preview a dataset."""
    dataset = Dataset.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        # Read the dataset file
        df = pd.read_csv(dataset.file_path)
        
        # Get basic stats
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'has_nulls': df.isnull().any().any(),
            'null_count': df.isnull().sum().sum()
        }
        
        # Get preview data (first 10 rows)
        preview_data = df.head(10).to_dict('records')
        
        return render_template(
            'upload/preview.html',
            active_page='upload',
            dataset=dataset,
            stats=stats,
            preview_data=preview_data,
            columns=df.columns.tolist()
        )
    except Exception as e:
        flash(f'Error previewing dataset: {str(e)}', 'danger')
        return redirect(url_for('upload.index'))

@upload_bp.route('/upload/delete/<int:id>')
@login_required
def delete_dataset(id):
    """Delete a dataset."""
    dataset = Dataset.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete the file from disk
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        
        # Delete database record
        db.session.delete(dataset)
        db.session.commit()
        
        flash(f'Dataset "{dataset.name}" deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting dataset: {str(e)}', 'danger')
    
    return redirect(url_for('upload.index'))

@upload_bp.route('/upload/download_sample')
@login_required
def download_sample():
    """Download a sample CSV file."""
    # Create a sample DataFrame
    dates = pd.date_range(start='2023-01-01', periods=24*7, freq='H')
    
    # Create consumption data with day/night pattern and weekday/weekend differences
    consumption = []
    for date in dates:
        hour = date.hour
        is_weekend = date.dayofweek >= 5  # 5 = Saturday, 6 = Sunday
        
        # Base consumption
        if 7 <= hour <= 22:  # Daytime
            base = 85 if is_weekend else 110
        else:  # Nighttime
            base = 45 if is_weekend else 50
        
        # Add some randomness
        noise = pd.np.random.normal(0, 5)
        consumption.append(base + noise)
    
    # Temperature with day/night pattern
    temperature = []
    for date in dates:
        hour = date.hour
        # Base temperature
        if 10 <= hour <= 16:  # Midday
            base = 25
        elif 6 <= hour <= 9 or 17 <= hour <= 21:  # Morning/Evening
            base = 22
        else:  # Night
            base = 19
        
        # Add some randomness
        noise = pd.np.random.normal(0, 1.5)
        temperature.append(base + noise)
    
    # Humidity
    humidity = []
    for i in range(len(dates)):
        base = 50
        # Higher humidity at night and early morning
        if dates[i].hour < 8 or dates[i].hour > 20:
            base = 65
        # Add some randomness
        noise = pd.np.random.normal(0, 5)
        humidity.append(max(min(base + noise, 100), 0))  # Clamp between 0 and 100
    
    # Create the DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'consumption': consumption,
        'temperature': temperature,
        'humidity': humidity
    })
    
    # Format timestamp as string
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Create a temporary file
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'sample_energy_data.csv')
    df.to_csv(temp_path, index=False)
    
    # Send the file
    return send_file(
        temp_path,
        as_attachment=True,
        download_name='sample_energy_data.csv',
        mimetype='text/csv'
    )