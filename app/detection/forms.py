"""
Detection forms for the Energy Anomaly Detection System.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class DetectionForm(FlaskForm):
    """Form for configuring anomaly detection."""
    name = StringField('Analysis Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    
    description = TextAreaField('Description (optional)', validators=[
        Optional(),
        Length(max=500)
    ])
    
    dataset_id = SelectField('Dataset', coerce=int, validators=[
        DataRequired()
    ])
    
    algorithm = SelectField('Algorithm', validators=[
        DataRequired()
    ], choices=[
        ('isolation_forest', 'Isolation Forest'),
        ('autoencoder', 'AutoEncoder'),
        ('kmeans', 'K-Means Clustering')
    ])
    
    # Isolation Forest parameters
    if_n_estimators = IntegerField('Number of Estimators', default=100, validators=[
        Optional(),
        NumberRange(min=50, max=500)
    ])
    
    if_contamination = FloatField('Contamination Factor', default=0.05, validators=[
        Optional(),
        NumberRange(min=0.01, max=0.2)
    ])
    
    # AutoEncoder parameters
    ae_threshold = IntegerField('Threshold Percentile', default=95, validators=[
        Optional(),
        NumberRange(min=90, max=99)
    ])
    
    ae_components = IntegerField('Number of Components', default=2, validators=[
        Optional(),
        NumberRange(min=1, max=10)
    ])
    
    # K-Means parameters
    km_clusters = IntegerField('Number of Clusters', default=5, validators=[
        Optional(),
        NumberRange(min=2, max=20)
    ])
    
    km_threshold = IntegerField('Threshold Percentile', default=95, validators=[
        Optional(),
        NumberRange(min=90, max=99)
    ])
    
    submit = SubmitField('Run Detection')