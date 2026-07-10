# gui.py - Lightweight desktop GUI wrapper for BrickSeek using pywebview and PyInstaller
import os
import sys
import threading
import webview

# Configure folder paths for PyInstaller environment
if getattr(sys, 'frozen', False):
    # Running inside the compiled PyInstaller bundle
    bundle_dir = sys._MEIPASS
else:
    # Running in standard Python development mode
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Dynamically override backend paths to read assets and database from the bundle
import server
server.DB_PATH = os.path.join(bundle_dir, "db", "lego.db")
server.STATIC_DIR = bundle_dir

def start_backend():
    print(f"[Desktop Main] Launching background API server at http://localhost:{server.PORT}")
    server.main()

if __name__ == '__main__':
    # 1. Start the Python SQLite API Gateway server in a background daemon thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 2. Start the native desktop container window
    print("[Desktop Main] Loading native container webview...")
    webview.create_window(
        title='BrickSeek 乐高人仔雷达 - 客户端',
        url=f'http://localhost:{server.PORT}',
        width=1280,
        height=850,
        resizable=True,
        min_size=(900, 600)
    )
    webview.start()
