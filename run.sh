#!/bin/bash
# Dr.MortgageUSA deployment run script

# Use PORT from environment or default to 5000
PORT=${PORT:-5000}
export PORT

# Run the Python server
exec python main.py