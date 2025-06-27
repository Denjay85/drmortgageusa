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

def find_available_port(start_port=5000, host='0.0.0.0'):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, port))
                return port
        except socket.error:
            continue
    return None

# Start the server with SO_REUSEADDR
class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def main():
    """Main function to start the HTTP server"""
    global PORT
    # Verify index.html exists
    if not os.path.exists('index.html'):
        print("❌ index.html not found in current directory")
        sys.exit(1)
    
    httpd = None
    try:
        # Try to create the server
        httpd = ReuseAddrTCPServer(("0.0.0.0", PORT), HTTPHandler)
        
        # Test the connection to make sure it's actually bound
        import threading
        import time
        
        def test_connection():
            time.sleep(0.5)  # Give server time to start
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = test_socket.connect_ex(('localhost', PORT))
                test_socket.close()
                if result == 0:
                    print(f"✅ Port {PORT} confirmed accessible")
                else:
                    print(f"⚠️ Port {PORT} bind successful but not accessible (code: {result})")
            except Exception as e:
                print(f"⚠️ Port test failed: {e}")
        
        # Start connection test in background
        test_thread = threading.Thread(target=test_connection, daemon=True)
        test_thread.start()
        
        print(f"✅ Dr.MortgageUSA server running on http://0.0.0.0:{PORT}")
        print(f"📁 Serving files from: {os.getcwd()}")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Trying to find available port...")
            available_port = find_available_port(PORT + 1)
            if available_port:
                print(f"🔄 Retrying with port {available_port}")
                try:
                    httpd = ReuseAddrTCPServer(("0.0.0.0", available_port), HTTPHandler)
                    print(f"✅ Dr.MortgageUSA server running on http://0.0.0.0:{available_port}")
                    print(f"📁 Serving files from: {os.getcwd()}")
                    httpd.serve_forever()
                except Exception as retry_e:
                    print(f"❌ Failed to start on port {available_port}: {retry_e}")
                    sys.exit(1)
            else:
                print("❌ No available ports found")
                sys.exit(1)
        else:
            print(f"❌ Socket error: {e}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        if httpd:
            httpd.shutdown()
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()