#!/usr/bin/env python3
"""
Simple HTTP server to serve static files for Dr.MortgageUSA
Optimized for Replit deployment
"""
import http.server
import socketserver
import os
import signal
import sys

# Get port from environment variable or default to 5000
PORT = int(os.environ.get('PORT', 5000))

# Change to the directory containing the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for root requests
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

def signal_handler(signum, frame):
    print("\nShutting down server...")
    sys.exit(0)

# Handle graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

try:
    # Start server with SO_REUSEADDR option
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.socket.setsockopt(socketserver.socket.SOL_SOCKET, socketserver.socket.SO_REUSEADDR, 1)
        print(f"✅ Dr.MortgageUSA server running on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
except OSError as e:
    if e.errno == 98:  # Address already in use
        print(f"❌ Port {PORT} is already in use. Trying to find available port...")
        for port in range(5001, 5010):
            try:
                with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
                    httpd.socket.setsockopt(socketserver.socket.SOL_SOCKET, socketserver.socket.SO_REUSEADDR, 1)
                    print(f"✅ Dr.MortgageUSA server running on http://0.0.0.0:{port}")
                    httpd.serve_forever()
                    break
            except OSError:
                continue
    else:
        raise