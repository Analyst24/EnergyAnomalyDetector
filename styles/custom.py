"""
Custom styles for the Energy Anomaly Detection System
"""
import streamlit as st

def apply_custom_styles():
    """Apply custom styling to the Streamlit app"""
    # Custom CSS for dark theme and better UI
    custom_css = """
    <style>
    .stApp {
        background-color: #1E272E;
        color: #FFFFFF;
    }
    .css-1kyxreq, .css-1kyxreq:hover {
        color: #FFFFFF;
    }
    .css-10trblm {
        color: #00B0FF;
    }
    .stButton button {
        background-color: #00B0FF;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #0091EA;
        color: white;
    }
    .stTextInput input, .stSelectbox select {
        background-color: #2C3E50;
        color: white;
        border-radius: 5px;
    }
    .stProgress .st-bo {
        background-color: #00B0FF;
    }
    .stAlert {
        background-color: #2C3E50;
        color: white;
        border-radius: 5px;
    }
    .stDataFrame {
        background-color: #2C3E50;
    }
    .stDataFrame table {
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E272E;
    }
    .stTabs [data-baseweb="tab"] {
        color: white;
    }
    .css-12oz5g7 {
        padding-top: 2rem;
    }
    </style>
    """
    
    # Inject custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Set streamlit theme if not already set
    if not st.session_state.get('theme_set', False):
        st.session_state['theme_set'] = True