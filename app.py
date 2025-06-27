#!/usr/bin/env python3
import http.server
import socketserver
import os

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

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Verify index.html exists
    if not os.path.exists('index.html'):
        print("ERROR: index.html not found in current directory")
        exit(1)
    
    print(f"Starting Dr.MortgageUSA web server on port {PORT}")
    print(f"Serving directory: {os.getcwd()}")
    
    try:
        with TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            print(f"Server successfully started at http://0.0.0.0:{PORT}")
            print("Server is ready to accept connections")
            httpd.serve_forever()
    except Exception as e:
        print(f"ERROR: Failed to start server - {e}")
        exit(1)