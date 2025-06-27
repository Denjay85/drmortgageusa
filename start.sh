#!/bin/bash
# Dr.MortgageUSA server startup script
# This script ensures the server starts correctly for deployment

echo "🚀 Starting Dr.MortgageUSA server..."

# Get port from environment variable or use default
PORT=${PORT:-5000}

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "✅ Using Python 3"
    python3 run.py
elif command -v python &> /dev/null; then
    echo "✅ Using Python"
    python run.py
else
    echo "❌ Python not found. Trying Node.js alternative..."
    if command -v npx &> /dev/null; then
        echo "✅ Using npx serve"
        npx serve -s . -l $PORT
    else
        echo "❌ No suitable server found"
        exit 1
    fi
fi