#!/usr/bin/env python3
"""
Dr.MortgageUSA Static File Server
Simple, reliable HTTP server for serving the mortgage sales funnel
"""
import http.server
import socketserver
import os
import socket
import sys

# Get port from environment variable or default to 5000
PORT = int(os.environ.get('PORT', 5000))

class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def find_available_port(start_port=5000):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except socket.error:
            continue
    return None

# Start the server with SO_REUSEADDR
class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def main():
    """Main function to start the HTTP server"""
    # Find available port
    available_port = find_available_port(PORT)
    if available_port is None:
        print("❌ No available ports found")
        sys.exit(1)
    
    # Verify index.html exists
    if not os.path.exists('index.html'):
        print("❌ index.html not found in current directory")
        sys.exit(1)
    
    try:
        httpd = ReuseAddrTCPServer(("0.0.0.0", available_port), HTTPHandler)
        print(f"✅ Dr.MortgageUSA server running on http://0.0.0.0:{available_port}")
        print(f"📁 Serving files from: {os.getcwd()}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()