#!/bin/bash
# Setup script for RSS1 Extemp Topic Generator

# Ensure script is run from the project root
if [ ! -f requirements.txt ]; then
  echo "Error: Please run this script from the project root directory containing requirements.txt."
  exit 1
fi

# Make the script executable (if not already)
chmod +x "$0"

# Install Python dependencies
pip install --user -r requirements.txt

# Download the spaCy English model to user directory for compatibility
python3 -m spacy download en_core_web_sm --user

echo "Setup complete."
