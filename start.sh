#!/bin/bash

echo "Starting AI Chat Assistant..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

# Check if setup was run
if [ ! -d "venv" ]; then
    echo "First time setup required..."
    echo "Running setup.py to install dependencies..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "Setup failed! Please check the error messages above."
        exit 1
    fi
fi

# Run the application
echo "Launching AI Chat Assistant..."
./venv/bin/python -m gui.app
