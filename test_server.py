#!/usr/bin/env python3
import http.server
import socketserver
import threading
import time
import socket

def find_available_port(start_port=5000):
    """Find an available port starting from start_port"""
    import socket
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except socket.error:
            continue
    return None

PORT = find_available_port(5000)
if PORT is None:
    print("❌ No available ports found")
    exit(1)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

def test_server():
    """Test if server is actually accessible"""
    time.sleep(1)  # Wait for server to start
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', PORT))
        sock.close()
        
        if result == 0:
            print(f"✅ Server accessible on 127.0.0.1:{PORT}")
            
            # Test HTTP request
            import urllib.request
            try:
                response = urllib.request.urlopen(f'http://127.0.0.1:{PORT}/', timeout=5)
                print(f"✅ HTTP response: {response.status}")
            except Exception as e:
                print(f"❌ HTTP request failed: {e}")
        else:
            print(f"❌ Server not accessible on 127.0.0.1:{PORT} (code: {result})")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

if __name__ == "__main__":
    # Start connectivity test in background
    test_thread = threading.Thread(target=test_server, daemon=True)
    test_thread.start()
    
    # Start server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"🚀 Test server starting on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")