"""
Energy Anomaly Detection System Pages
Initializing the pages package and applying special sidebar hiding
"""
import os
import shutil
import streamlit as st

# This script runs when the pages folder is imported
# Hide all .py files in this directory from Streamlit's page registry
# by adding a leading underscore

# Get the current directory (pages/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Hide "init" from sidebar by removing it from pages registry
try:
    # Hide the initialization file at runtime
    for filename in os.listdir(current_dir):
        if filename.startswith('__init__'):
            # Skip this file
            continue
            
    # Force hide via inject custom style
    st.markdown("""
    <style>
    /* Hide the first (init) item in sidebar - aggressive version */
    div[data-testid="stSidebarNav"] > ul:first-child > li:first-child,
    div[data-testid="stSidebarNav"] ul > li:has(a[href="/"]),
    div[data-testid="stSidebarNav"] ul > li:first-child,
    section[data-testid="stSidebar"] div > ul > li:has(a[href="/"]) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
except Exception as e:
    # Don't show any errors to avoid UI disruption
    pass