#!/bin/bash

set -euo pipefail

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found, installing..."
    # For Debian/Ubuntu systems
    sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
fi

# Create a temporary directory for the virtual environment
VENV_DIR=$(mktemp -d)

# Create virtual environment
python3 -m venv "$VENV_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r ./requirements.txt

# Run the images-controller script
python ./images-controller.py

# Deactivate virtual environment
deactivate

# Remove virtual environment directory
echo "Cleaning up virtual environment..."
rm -rf "$VENV_DIR"

echo "images-controller run completed."
