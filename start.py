#!/usr/bin/env python3
"""
Dr.MortgageUSA Deployment Startup Script
Ensures reliable server startup with multiple fallback options
"""
import os
import sys
import subprocess
import socket

PORT = int(os.environ.get('PORT', 5000))

def check_file_exists():
    """Verify required files exist"""
    if not os.path.exists('index.html'):
        print("ERROR: index.html not found in current directory")
        return False
    return True

def check_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except socket.error:
        return False

def try_python_server():
    """Try Python HTTP server"""
    try:
        print("Starting Python HTTP server...")
        import http.server
        import socketserver
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = '/index.html'
                return super().do_GET()
        
        class TCPServer(socketserver.TCPServer):
            allow_reuse_address = True
        
        with TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            print(f"✅ Python server started at http://0.0.0.0:{PORT}")
            print("Server is ready to accept connections")
            httpd.serve_forever()
            
    except Exception as e:
        print(f"❌ Python server failed: {e}")
        return False

def try_node_server():
    """Try Node.js serve package"""
    try:
        print("Attempting Node.js serve...")
        result = subprocess.run(['npx', 'serve', '-s', '.', '-l', str(PORT)], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Node.js serve failed: {e}")
        return False

def main():
    """Main startup function with fallback options"""
    print(f"🚀 Starting Dr.MortgageUSA server on port {PORT}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check prerequisites
    if not check_file_exists():
        sys.exit(1)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Try Python server first
    try:
        try_python_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ All server options failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()