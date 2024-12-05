#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env file with a random secret key
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')" > .env

# Create necessary directories if they don't exist
mkdir -p static/css static/js templates

echo "Setup complete! To start the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python app.py"
echo "3. Open http://localhost:5000 in your browser"
