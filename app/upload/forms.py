"""
Forms for the upload blueprint.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class UploadDatasetForm(FlaskForm):
    """Form for uploading a new dataset."""
    name = StringField('Dataset Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters.')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description must be less than 500 characters.')
    ])
    
    file = FileField('Dataset File', validators=[
        FileRequired(),
        FileAllowed(['csv', 'xlsx', 'xls', 'json', 'txt'], 
                    'Only CSV, Excel, JSON, and TXT files are allowed.')
    ])
    
    has_header = BooleanField('File has header row', default=True)
    
    has_timestamp = BooleanField('File contains timestamp column', default=True)
    
    parse_timestamps = BooleanField('Automatically parse timestamps', default=True)
    
    submit = SubmitField('Upload Dataset')


class DataPreviewForm(FlaskForm):
    """Form for confirming dataset preview and column mappings."""
    timestamp_column = StringField('Timestamp Column', validators=[Optional()])
    
    target_column = StringField('Target Column (Energy Consumption)', validators=[DataRequired()])
    
    submit = SubmitField('Confirm and Save Dataset')
    
    back = SubmitField('Back to Upload')