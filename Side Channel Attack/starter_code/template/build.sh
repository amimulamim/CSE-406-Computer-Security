#!/bin/bash
# Build script for Render deployment

# Upgrade pip and install build tools first
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

echo "Build completed successfully!"
