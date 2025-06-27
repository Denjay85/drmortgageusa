#!/bin/bash
# Dr.MortgageUSA Docker/Container startup script
set -e

echo "🚀 Starting Dr.MortgageUSA server..."

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo "❌ index.html not found"
    exit 1
fi

# Get port from environment
export PORT=${PORT:-5000}
echo "📡 Using port: $PORT"

# Try Python server first (most reliable)
if command -v python3 &> /dev/null; then
    echo "🐍 Starting Python server..."
    exec python3 app.py
fi

# Fallback to Node.js
if command -v node &> /dev/null; then
    echo "🟢 Starting Node.js server..."
    exec node start-server.js
fi

# Last resort - npx serve
if command -v npx &> /dev/null; then
    echo "📦 Starting npx serve..."
    exec npx serve -s . -l $PORT
fi

echo "❌ No suitable server found"
exit 1