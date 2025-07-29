#!/usr/bin/env python3
"""
Dr.MortgageUSA Static Site Server
Ultra-simple static file server for production deployment
"""
import http.server
import socketserver
import os
import sys

# Set port from environment or default
PORT = int(os.environ.get('PORT', 5000))

class StaticHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Always serve index.html for root
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        # CORS headers for external API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Static site headers
        self.send_header('Cache-Control', 'public, max-age=86400')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

class StaticServer(socketserver.TCPServer):
    allow_reuse_address = True

def main():
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Verify static files exist
    if not os.path.exists('index.html'):
        print("ERROR: index.html not found")
        sys.exit(1)
    
    # Start static server
    with StaticServer(("0.0.0.0", PORT), StaticHandler) as server:
        print(f"Static site running at http://0.0.0.0:{PORT}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    main()