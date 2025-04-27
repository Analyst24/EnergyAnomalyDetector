"""
Energy Anomaly Detection System - Start Page (Redirector)
This page hijacks the "init" entry by being alphabetically first
"""
import streamlit as st

# This is a "dummy" page that will appear as the first entry
# in the Streamlit sidebar, replacing the "init" entry

# We immediately redirect to the app.py (main file) when this page is accessed
st.markdown(
    """
    <meta http-equiv="refresh" content="0;url=/" />
    <style>
    /* Hide ALL sidebar navigation elements programmatically */
    div[data-testid="stSidebarNav"] {
        visibility: hidden !important;
    }
    
    /* Then manually recreate only the ones we want (skip "init" and this page) */
    div[data-testid="stSidebarNav"] > ul > li:nth-child(n+3) {
        visibility: visible !important;
    }
    
    /* Complete hide of init and this redirector */
    div[data-testid="stSidebarNav"] > ul > li:first-child, 
    div[data-testid="stSidebarNav"] > ul > li:nth-child(2) {
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        position: absolute !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Heading for this page (rarely seen, just in case)
st.title("⚡ Energy Anomaly Detection System")
st.info("Redirecting to main dashboard...")