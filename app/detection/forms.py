"""
Forms for anomaly detection configuration.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class IsolationForestForm(FlaskForm):
    """Form for configuring Isolation Forest algorithm."""
    name = StringField('Analysis Name', validators=[DataRequired()])
    
    description = StringField('Description', validators=[Optional()])
    
    target_column = SelectField('Target Column', validators=[DataRequired()])
    
    n_estimators = IntegerField('Number of Estimators', 
                               validators=[NumberRange(min=10, max=1000)],
                               default=100)
    
    contamination = FloatField('Contamination Factor', 
                             validators=[NumberRange(min=0.01, max=0.5)],
                             default=0.1)
    
    max_samples = IntegerField('Max Samples', 
                              validators=[Optional()],
                              default=256)
    
    random_state = IntegerField('Random State', 
                               validators=[Optional()],
                               default=42)
    
    submit = SubmitField('Run Detection')


class AutoEncoderForm(FlaskForm):
    """Form for configuring Autoencoder algorithm."""
    name = StringField('Analysis Name', validators=[DataRequired()])
    
    description = StringField('Description', validators=[Optional()])
    
    target_column = SelectField('Target Column', validators=[DataRequired()])
    
    encoding_dim = IntegerField('Encoding Dimension', 
                               validators=[NumberRange(min=1, max=100)],
                               default=8)
    
    epochs = IntegerField('Epochs', 
                         validators=[NumberRange(min=10, max=1000)],
                         default=50)
    
    batch_size = IntegerField('Batch Size', 
                             validators=[NumberRange(min=8, max=1024)],
                             default=32)
    
    threshold_percentile = FloatField('Threshold Percentile', 
                                    validators=[NumberRange(min=90, max=99.9)],
                                    default=95)
    
    submit = SubmitField('Run Detection')


class KMeansForm(FlaskForm):
    """Form for configuring K-Means algorithm."""
    name = StringField('Analysis Name', validators=[DataRequired()])
    
    description = StringField('Description', validators=[Optional()])
    
    target_column = SelectField('Target Column', validators=[DataRequired()])
    
    n_clusters = IntegerField('Number of Clusters', 
                             validators=[NumberRange(min=2, max=50)],
                             default=8)
    
    distance_threshold = FloatField('Distance Threshold', 
                                  validators=[NumberRange(min=0.5, max=10)],
                                  default=2.0)
    
    random_state = IntegerField('Random State', 
                               validators=[Optional()],
                               default=42)
    
    submit = SubmitField('Run Detection')


class DBSCANForm(FlaskForm):
    """Form for configuring DBSCAN algorithm."""
    name = StringField('Analysis Name', validators=[DataRequired()])
    
    description = StringField('Description', validators=[Optional()])
    
    target_column = SelectField('Target Column', validators=[DataRequired()])
    
    eps = FloatField('Epsilon (Distance)', 
                    validators=[NumberRange(min=0.01, max=10)],
                    default=0.5)
    
    min_samples = IntegerField('Min Samples', 
                              validators=[NumberRange(min=2, max=100)],
                              default=5)
    
    submit = SubmitField('Run Detection')


class SelectAlgorithmForm(FlaskForm):
    """Form for selecting anomaly detection algorithm."""
    algorithm = SelectField('Select Algorithm', validators=[DataRequired()],
                          choices=[
                              ('isolation_forest', 'Isolation Forest'),
                              ('autoencoder', 'Autoencoder Neural Network'),
                              ('kmeans', 'K-Means Clustering'),
                              ('dbscan', 'DBSCAN Clustering')
                          ])
    
    submit = SubmitField('Next')