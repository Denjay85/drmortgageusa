#!/usr/bin/env python3
"""
Dr.MortgageUSA Deployment Fix Script
Handles the python vs python3 executable issue for reliable deployment
"""
import os
import sys
import subprocess
import shutil

def check_python_executable():
    """Check which Python executable is available"""
    python_executables = ['python3', 'python']
    
    for executable in python_executables:
        if shutil.which(executable):
            print(f"✅ Found Python executable: {executable}")
            return executable
    
    print("❌ No Python executable found")
    return None

def start_server():
    """Start the server using the correct Python executable"""
    python_exec = check_python_executable()
    
    if not python_exec:
        print("❌ Cannot find Python executable. Falling back to Node.js...")
        return start_node_server()
    
    try:
        print(f"🚀 Starting Dr.MortgageUSA server with {python_exec}...")
        # Use python3 explicitly to avoid the deployment issue
        subprocess.run([python_exec, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Python server failed: {e}")
        print("🔄 Falling back to Node.js server...")
        return start_node_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True

def start_node_server():
    """Start Node.js server as fallback"""
    try:
        print("🚀 Starting Node.js serve server...")
        port = os.environ.get('PORT', '5000')
        subprocess.run(['npx', 'serve', '-s', '.', '-l', port], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Node.js server failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Node.js/npx not found")
        return False

if __name__ == "__main__":
    print("🔧 Dr.MortgageUSA Deployment Fix")
    print("   Resolving python vs python3 executable issue...")
    
    if not start_server():
        print("❌ All deployment options failed")
        sys.exit(1)