#!/usr/bin/env python3
"""
Dr.MortgageUSA Production Server
Deployment-optimized HTTP server for serving the mortgage sales funnel
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def main():
    """Main function to start the production server"""
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Verify index.html exists
    if not os.path.exists('index.html'):
        print("ERROR: index.html not found in current directory")
        sys.exit(1)
    
    print(f"Starting Dr.MortgageUSA server on port {PORT}")
    print(f"Serving files from: {os.getcwd()}")
    
    try:
        with TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            print(f"Server running at http://0.0.0.0:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()