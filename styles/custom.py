"""
Custom styling utilities for the Energy Anomaly Detection System
"""
import streamlit as st

def apply_custom_styles():
    """Apply custom styles to the Streamlit app"""
    # Set dark theme
    dark_theme = """
    <style>
        /* Dark theme customization */
        .stApp {
            background-color: #1E2730;
            color: #ffffff;
        }
        
        .stTextInput, .stNumberInput, .stDateInput, .stSelectbox {
            background-color: #2C3E50;
            color: #ffffff;
            border-radius: 5px;
        }
        
        .stButton button {
            background-color: #3498DB;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 8px 16px;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background-color: #2980B9;
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.2);
        }
        
        h1, h2, h3 {
            color: #3498DB;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #2C3E50;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            color: white;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3498DB !important;
            color: white !important;
        }
        
        /* Table styling */
        .stDataFrame table {
            border-collapse: collapse;
            border: none;
        }
        
        .stDataFrame th {
            background-color: #3498DB;
            color: white;
            font-weight: bold;
            padding: 10px;
            text-align: center;
            border: 1px solid #2980B9;
        }
        
        .stDataFrame td {
            background-color: #2C3E50;
            color: white;
            padding: 8px;
            border: 1px solid #34495E;
        }
        
        /* Card styling */
        .card {
            background-color: #2C3E50;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #2C3E50;
            border-right: 1px solid #34495E;
            padding-top: 20px;
        }
        
        [data-testid="stSidebar"] hr {
            margin-top: 30px;
            margin-bottom: 30px;
            border-color: #34495E;
        }
    </style>
    """
    
    st.markdown(dark_theme, unsafe_allow_html=True)

def create_card(title, content, key=None):
    """
    Create a styled card with a title and content
    
    Args:
        title (str): Card title
        content (str): Card content (markdown)
        key (str, optional): Unique key for the card container
    """
    st.markdown(f"""
    <div class="card">
        <h3>{title}</h3>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_suffix=None, style="primary"):
    """
    Create a styled metric card
    
    Args:
        title (str): Metric title
        value (str/int/float): Main value to display
        delta (str/int/float, optional): Delta/change value 
        delta_suffix (str, optional): Suffix for delta (e.g., %)
        style (str): Style - primary, success, warning, danger
    """
    # Choose color based on style
    colors = {
        "primary": "#3498DB",
        "success": "#2ECC71",
        "warning": "#F39C12",
        "danger": "#E74C3C"
    }
    
    color = colors.get(style, colors["primary"])
    
    # Format delta if provided
    delta_html = ""
    if delta is not None:
        delta_prefix = "+" if float(delta) > 0 else ""
        delta_color = "#2ECC71" if float(delta) > 0 else "#E74C3C" if float(delta) < 0 else "#7F8C8D"
        
        delta_value = f"{delta_prefix}{delta}"
        if delta_suffix:
            delta_value += f" {delta_suffix}"
            
        delta_html = f"""
        <div style="font-size: 14px; color: {delta_color}; margin-top: 5px;">
            {delta_value}
        </div>
        """
    
    st.markdown(f"""
    <div style="background-color: #2C3E50; border-left: 4px solid {color}; 
                padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <div style="font-size: 16px; color: #BDC3C7;">{title}</div>
        <div style="font-size: 28px; font-weight: bold; color: white;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)