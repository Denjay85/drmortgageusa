#!/bin/bash
# Dr.MortgageUSA server startup script
# This script ensures the server starts correctly for deployment

echo "🚀 Starting Dr.MortgageUSA server..."

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo "❌ index.html not found in current directory"
    exit 1
fi

# Get port from environment variable or use default
PORT=${PORT:-5000}
echo "📡 Using port: $PORT"

# Try main.py (optimized server) first
if command -v python3 &> /dev/null; then
    echo "🐍 Attempting optimized Python server (main.py)..."
    python3 main.py && exit 0
fi

# Try run.py as fallback
if command -v python3 &> /dev/null; then
    echo "🐍 Attempting fallback Python server (run.py)..."
    python3 run.py && exit 0
fi

# Try custom Node.js server
if command -v node &> /dev/null; then
    echo "🟢 Attempting custom Node.js server..."
    node start-server.js && exit 0
fi

# Try npx serve as last resort
if command -v npx &> /dev/null; then
    echo "📦 Attempting npx serve..."
    npx serve -s . -l $PORT && exit 0
fi

echo "❌ All server options failed"
echo "💡 Available files:"
ls -la
echo "💡 Directory: $(pwd)"
exit 1