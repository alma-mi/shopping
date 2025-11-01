"""
Quick launcher for Shopping App
Starts server and GUI in separate processes
"""
import subprocess
import time
import sys

def main():
    print("=" * 60)
    print("Shopping App Launcher")
    print("=" * 60)
    
    # Start server
    print("\n[1/2] Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    # Wait a bit for server to initialize
    time.sleep(2)
    
    # Start GUI
    print("[2/2] Starting GUI client...")
    gui_process = subprocess.Popen([sys.executable, "shopping_gui.py"])
    
    print("\n✓ Shopping App is running!")
    print("\nDefault credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nPress Ctrl+C to stop server...")
    
    try:
        # Wait for GUI to close
        gui_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        # Clean up
        server_process.terminate()
        print("✓ Server stopped")

if __name__ == "__main__":
    main()
