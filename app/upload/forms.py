"""
Upload forms for the Energy Anomaly Detection System.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class UploadForm(FlaskForm):
    """Form for uploading datasets."""
    name = StringField('Dataset Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    
    description = TextAreaField('Description (optional)', validators=[
        Optional(),
        Length(max=500)
    ])
    
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only')
    ])
    
    has_header = BooleanField('File has header row', default=True)
    
    submit = SubmitField('Upload')