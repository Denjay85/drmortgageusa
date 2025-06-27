#!/usr/bin/env python3
import http.server
import socketserver
import os
from pathlib import Path

# Get port from environment variable or default to 5000
PORT = int(os.environ.get('PORT', 5000))

# Set the current directory as the web root
web_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(web_dir)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # If requesting root path, serve index.html
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

# Start the server
with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Server started at http://0.0.0.0:{PORT}")
    print(f"Serving files from: {web_dir}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown()