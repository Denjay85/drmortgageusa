#!/usr/bin/env python3
"""
Dr.MortgageUSA Static File Server
Simple, reliable HTTP server for serving the mortgage sales funnel
"""
import http.server
import socketserver
import os
import socket

PORT = int(os.environ.get('PORT', 5000))

class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

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

# Find available port
available_port = find_available_port(PORT)
if available_port is None:
    print("❌ No available ports found")
    exit(1)

# Start the server with SO_REUSEADDR
class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

try:
    httpd = ReuseAddrTCPServer(("0.0.0.0", available_port), HTTPHandler)
    print(f"✅ Dr.MortgageUSA server running on http://0.0.0.0:{available_port}")
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Server stopped")
    httpd.shutdown()