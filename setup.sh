#!/bin/bash
# Setup script for RSS1 Extemp Topic Generator

# Install Python dependencies
pip install -r requirements.txt

# Download the spaCy English model
echo "Downloading spaCy English model (en_core_web_sm)..."
python3 -m spacy download en_core_web_sm

echo "Setup complete."
