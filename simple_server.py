#!/usr/bin/env python3
"""
Dr.MortgageUSA Simple Static Server
Minimal HTTP server for reliable deployment
"""
import http.server
import socketserver
import os
import sys

PORT = int(os.environ.get('PORT', 5000))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

class Server(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check index.html exists
    if not os.path.exists('index.html'):
        print("❌ index.html not found")
        sys.exit(1)
    
    try:
        with Server(("0.0.0.0", PORT), Handler) as httpd:
            print(f"✅ Server running on http://0.0.0.0:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Server failed: {e}")
        sys.exit(1)