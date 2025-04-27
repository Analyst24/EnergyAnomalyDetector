#!/bin/bash

echo "===== Energy Anomaly Detection System ====="
echo "Starting the application..."
echo
echo "Please wait while the application launches..."
echo

python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501 --browser.serverAddress=127.0.0.1

if [ $? -ne 0 ]; then
    echo
    echo "Error starting the application. Please try the following:"
    echo "1. Make sure Python and all dependencies are installed"
    echo "2. Try running 'python run.py' in a terminal"
    echo "3. Check INSTALL.txt for troubleshooting help"
    echo
    read -p "Press Enter to continue..."
fi