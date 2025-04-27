"""
Routes for file upload and data import.
"""
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user
from app import db
from app.upload import upload_bp
from app.upload.forms import UploadDatasetForm, DataPreviewForm
from app.models import Dataset


@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Upload dataset form page."""
    form = UploadDatasetForm()
    
    if form.validate_on_submit():
        # Get the uploaded file
        file = form.file.data
        filename = secure_filename(file.filename)
        
        # Create uploads directory if it doesn't exist
        uploads_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_id = current_user.id
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save the file
        file.save(file_path)
        
        # Try to parse the file for preview
        try:
            # Get file extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            # Parse based on file type
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            elif ext == '.txt':
                # Try to detect delimiter
                df = pd.read_csv(file_path, sep=None, engine='python')
            else:
                flash('Unsupported file format.', 'danger')
                return redirect(url_for('upload.index'))
            
            # Store temp info in session
            session['upload_file_path'] = file_path
            session['upload_file_name'] = filename
            session['upload_file_size'] = os.path.getsize(file_path)
            session['upload_dataset_name'] = form.name.data
            session['upload_dataset_description'] = form.description.data
            session['upload_has_header'] = form.has_header.data
            session['upload_has_timestamp'] = form.has_timestamp.data
            session['upload_parse_timestamps'] = form.parse_timestamps.data
            
            # Get preview of data and store column names
            preview_data = df.head(10).to_dict('records')
            session['upload_columns'] = df.columns.tolist()
            
            # Guess timestamp and target columns
            timestamp_col = None
            if form.has_timestamp.data:
                # Try to find timestamp column
                for col in df.columns:
                    if 'time' in col.lower() or 'date' in col.lower():
                        timestamp_col = col
                        break
            
            # Guess target column (energy consumption)
            target_col = None
            for col in df.columns:
                if any(term in col.lower() for term in ['energy', 'consumption', 'power', 'kwh', 'kw']):
                    target_col = col
                    break
            
            # If no target found, use first numeric column
            if target_col is None:
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        target_col = col
                        break
            
            return render_template('upload/preview.html',
                                  title='Data Preview',
                                  preview_data=preview_data,
                                  columns=df.columns.tolist(),
                                  timestamp_col=timestamp_col,
                                  target_col=target_col,
                                  dataset_name=form.name.data,
                                  file_name=filename)
        
        except Exception as e:
            flash(f'Error parsing file: {str(e)}', 'danger')
            # Clean up the file
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect(url_for('upload.index'))
    
    return render_template('upload/index.html', title='Upload Dataset', form=form)


@upload_bp.route('/preview', methods=['GET', 'POST'])
@login_required
def preview():
    """Preview and confirm dataset."""
    # Check if we have upload data in session
    if not all(key in session for key in [
        'upload_file_path', 
        'upload_file_name', 
        'upload_file_size', 
        'upload_dataset_name', 
        'upload_columns'
    ]):
        flash('No upload data found. Please upload a file first.', 'warning')
        return redirect(url_for('upload.index'))
    
    form = DataPreviewForm()
    
    if form.validate_on_submit():
        if form.back.data:
            return redirect(url_for('upload.index'))
        
        # Get form data
        timestamp_column = form.timestamp_column.data
        target_column = form.target_column.data
        
        # Get session data
        file_path = session['upload_file_path']
        filename = session['upload_file_name']
        file_size = session['upload_file_size']
        dataset_name = session['upload_dataset_name']
        description = session.get('upload_dataset_description', '')
        has_header = session.get('upload_has_header', True)
        has_timestamp = session.get('upload_has_timestamp', True)
        parse_timestamps = session.get('upload_parse_timestamps', True)
        
        try:
            # Load the data to get row and column count
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            elif ext == '.txt':
                df = pd.read_csv(file_path, sep=None, engine='python')
            
            # Create dataset record
            dataset = Dataset(
                name=dataset_name,
                description=description,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_type=ext[1:],  # Remove the dot
                row_count=len(df),
                column_count=len(df.columns),
                has_timestamps=has_timestamp,
                user_id=current_user.id
            )
            
            # Add and commit to database
            db.session.add(dataset)
            db.session.commit()
            
            # Clear session data
            for key in list(session.keys()):
                if key.startswith('upload_'):
                    session.pop(key, None)
            
            flash(f'Dataset "{dataset_name}" uploaded successfully!', 'success')
            return redirect(url_for('dashboard.view_dataset', dataset_id=dataset.id))
        
        except Exception as e:
            flash(f'Error saving dataset: {str(e)}', 'danger')
            return redirect(url_for('upload.preview'))
    
    # Pre-populate form if coming from upload
    if request.method == 'GET':
        timestamp_col = request.args.get('timestamp_col', '')
        target_col = request.args.get('target_col', '')
        form.timestamp_column.data = timestamp_col
        form.target_column.data = target_col
    
    # Get data for preview
    file_path = session['upload_file_path']
    try:
        # Get file extension
        _, ext = os.path.splitext(session['upload_file_name'])
        ext = ext.lower()
        
        # Parse based on file type
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif ext == '.json':
            df = pd.read_json(file_path)
        elif ext == '.txt':
            df = pd.read_csv(file_path, sep=None, engine='python')
        
        preview_data = df.head(10).to_dict('records')
        columns = df.columns.tolist()
        
        return render_template('upload/preview.html',
                              title='Data Preview',
                              form=form,
                              preview_data=preview_data,
                              columns=columns,
                              dataset_name=session['upload_dataset_name'],
                              file_name=session['upload_file_name'])
    
    except Exception as e:
        flash(f'Error parsing file: {str(e)}', 'danger')
        return redirect(url_for('upload.index'))


@upload_bp.route('/cancel')
@login_required
def cancel():
    """Cancel upload and clean up temporary files."""
    # Check if we have a file path in session
    if 'upload_file_path' in session:
        file_path = session['upload_file_path']
        
        # Remove the file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                flash(f'Error removing temporary file: {str(e)}', 'warning')
        
        # Clear session data
        for key in list(session.keys()):
            if key.startswith('upload_'):
                session.pop(key, None)
    
    flash('Upload cancelled.', 'info')
    return redirect(url_for('dashboard.datasets'))