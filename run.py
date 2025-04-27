#!/usr/bin/env python
"""
Launcher script for the Energy Anomaly Detection System
This script ensures all path settings are correct and launches the app
"""
import os
import sys
import subprocess
import platform

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """
    Main function to launch the application
    """
    print("=== Energy Anomaly Detection System ===")
    print("Starting the application...")
    
    # Launch with explicit localhost address and port
    command = ["streamlit", "run", "app.py", "--server.address=127.0.0.1", "--server.port=8501", "--browser.serverAddress=127.0.0.1"]
    
    # Check if on Windows for correct command formatting
    if platform.system() == "Windows":
        subprocess.run(command, shell=True, check=True)
    else:
        subprocess.run(command, check=True)
    
if __name__ == "__main__":
    main()