#!/usr/bin/env python3
"""
WSGI entry point for Dr.MortgageUSA
This file provides a WSGI-compatible entry point for deployment platforms
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import our main application
from main import main

if __name__ == "__main__":
    main()