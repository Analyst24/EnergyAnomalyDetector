"""
Custom styling for the Energy Anomaly Detection System.
"""
import streamlit as st

def apply_custom_styles():
    """
    Apply custom CSS styling to the Streamlit application.
    """
    # Custom CSS for the application
    st.markdown("""
    <style>
    /* Dark theme customization */
    .stApp {
        background-color: #1e272e;
        color: #ffffff;
    }
    
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #2d3436 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4b7bec;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #3867d6;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Card styling */
    div.stBlock {
        background-color: #2d3436;
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #4b7bec !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }
    
    /* Form styling */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div, 
    .stNumberInput > div > div > input {
        background-color: #2d3436 !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #2d3436 !important;
    }
    
    /* Footer styling */
    footer {
        border-top: 1px solid #3867d6;
        padding-top: 1rem;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #a0a0a0;
    }
    
    /* Animation for transitions */
    .stAnimatedDiv {
        transition: all 0.3s ease;
    }
    
    /* Custom styling for headers */
    .header-container {
        background-color: rgba(30, 39, 46, 0.8);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #4b7bec;
    }
    
    /* Success/info message styling */
    div.stSuccess, div.stInfo {
        border-radius: 8px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2d3436;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4b7bec;
    }
    
    /* Login form styling */
    .login-container {
        background-color: #2d3436;
        padding: 20px;
        border-radius: 10px;
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Impact labels styling */
    .high-impact {
        color: #ff4b4b;
        font-weight: bold;
    }
    
    .medium-impact {
        color: #ffbb33;
        font-weight: bold;
    }
    
    .low-impact {
        color: #2ecc71;
        font-weight: bold;
    }
    
    /* Copyright footer */
    .copyright-footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #3867d6;
        color: #a0a0a0;
        font-size: 0.8rem;
    }
    
    /* Chart container styling */
    .chart-container {
        background-color: #2d3436;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    /* Upload area styling */
    [data-testid="stFileUploader"] {
        background-color: #2d3436;
        padding: 10px;
        border-radius: 8px;
        border: 1px dashed #4b7bec;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d3436;
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background-color: #1e272e;
        border-radius: 0 0 8px 8px;
    }
    </style>
    """, unsafe_allow_html=True)
